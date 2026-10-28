"""Six false-source subset controls sharing the current full audit's even reconstruction."""
import copy,gzip,hashlib,json,time
from fractions import Fraction
from pathlib import Path,PurePosixPath,PureWindowsPath
DIM,BITS,SCALE=413,256,1<<256
KINDS=('A_model','weighted_head','weighted_complete_tail')
NATIVE_PIN=None
def require(ok, message):
    if not ok:
        raise ValueError(message)

def digest(raw):
    return hashlib.sha256(raw).hexdigest()

def unique(items):
    result = {}
    for key, value in items:
        require(key not in result, 'duplicate JSON key: ' + key)
        result[key] = value
    return result

def load(raw):
    return json.loads(raw, object_pairs_hook=unique,
                      parse_constant=lambda value: (_ for _ in ()).throw(ValueError(value)))

def encode(value):
    return (json.dumps(value, sort_keys=True, indent=2) + '\n').encode('utf-8')

def fresh(path, raw):
    with path.open('xb') as handle:
        handle.write(raw)

def confined(base, relative):
    require(type(relative) is str and relative and '\\' not in relative and
            '\x00' not in relative and ':' not in relative, 'portable relative path required')
    require(not PurePosixPath(relative).is_absolute() and
            not PureWindowsPath(relative).drive and
            all(part not in ('', '.', '..') for part in relative.split('/')),
            'invalid relative path component')
    path = (base / relative).resolve()
    require(path.is_relative_to(base.resolve()), 'path escapes bound directory')
    return path

def validate_payload(payload, kind, parity):
    require(set(payload) == {'kind', 'parity', 'dimension', 'bits', 'upper_triangle'},
            'matrix payload schema')
    require((payload['kind'], payload['parity'], payload['dimension'], payload['bits']) ==
            (kind, parity, DIM, BITS), 'matrix identity')
    triangle = payload['upper_triangle']
    require(type(triangle) is list and len(triangle) == DIM * (DIM + 1) // 2,
            'matrix triangle size')
    require(all(type(pair) is list and len(pair) == 2 and
                all(type(x) is int and x.bit_length() <= 16384 for x in pair) and
                pair[0] <= pair[1] for pair in triangle), 'matrix endpoint structure')

def floor_q(value):
    value = Fraction(str(value))
    return value.numerator // value.denominator

def ceil_q(value):
    return -floor_q(-Fraction(str(value)))

def prime5_changes(native, kappa):
    """Independent P_0 window formula; no producer arithmetic is evaluated."""
    arb = native.arb
    support = arb(native.fmpq(81, 100))
    tau5 = arb(5).log() / support
    delta = 2 - tau5
    c5 = arb(5).log() / arb(5).sqrt()
    other = (arb(2).log() / arb(2).sqrt() + arb(3).log() / arb(3).sqrt() +
             arb(2).log() / arb(4).sqrt())
    # On both edge windows, P5 P0 = -c5; each has length delta.
    # P5's signed low constant is -2 delta c5. Removing it adds that magnitude.
    # In P^2 the two mixed orientations and two edge windows contribute
    # 4 delta c5 (c2+c3+c4). Keep the low/head subtractions unchanged.
    require(native.endpoints(delta)[0] > 0, 'nonpositive prime-five edge window')
    low = 2 * c5 * delta
    mixed = -arb(kappa) * 4 * delta * c5 * other
    require(native.endpoints(tau5 - 1)[0] > 0, 'prime-five edge windows overlap')
    overlap_checks = []
    for m in (2, 3, 4):
        tau = arb(m).log() / support
        separated = native.endpoints(tau5 + tau - 2)
        nested = native.endpoints(tau5 - tau)
        require(separated[0] > 0 and nested[0] > 0,
                'prime-five mixed constant window formula not qualified')
        overlap_checks.append({'m': m, 'tau5_plus_tau_minus_2': [str(x) for x in separated],
                               'tau5_minus_tau': [str(x) for x in nested]})
    changes = {}
    evidence = {'tau5': [str(x) for x in native.endpoints(tau5)],
                'delta_equals_2_minus_tau5': [str(x) for x in native.endpoints(delta)],
                'c5': [str(x) for x in native.endpoints(c5)],
                'c2_plus_c3_plus_c4': [str(x) for x in native.endpoints(other)],
                'kappa': str(kappa), 'publication_bits': BITS, 'changes': {}}
    evidence['other_shift_window_inequalities'] = overlap_checks
    evidence['signed_prime5_low_P00'] = [str(x) for x in native.endpoints(-low)]
    for name, value, formula in (
            ('omitted-prime5-low-term', low, '+2*c5*(2-log(5)/T)'),
            ('omitted-prime5-mixed-square', mixed, '-kappa*4*(2-log(5)/T)*c5*(c2+c3+c4)')):
        lower, upper = native.endpoints(value)
        pair = [floor_q(lower * SCALE), ceil_q(upper * SCALE)]
        changes[name] = pair
        evidence['changes'][name] = {'formula': formula, 'cell': [0, 0],
                                      'exact_Arb_endpoint_enclosure': [str(lower), str(upper)],
                                      'outward_dyadic_shift_numerators': pair}
    return changes, evidence

def modify(payload, mode, changes):
    """Native omissions change only cell 00, a sufficient false-enclosure witness."""
    kind, parity = payload['kind'], payload['parity']
    triangle = payload['upper_triangle']
    lo, hi = triangle[0]
    if parity == 0:
        if mode == 'wrongactual-lowconstant' and kind == 'A_model':
            triangle[0] = [lo + 2 * SCALE, hi + 2 * SCALE]
        elif mode == 'underpaidweightedhead' and kind == 'weighted_head':
            triangle[0] = [lo // 2, -(-hi // 2)]
        elif mode == 'omitted-complete-physicalexterior' and kind == 'weighted_complete_tail':
            triangle[0] = [0, 0]
        elif ((mode == 'omitted-prime5-low-term' and kind == 'A_model') or
              (mode == 'omitted-prime5-mixed-square' and kind == 'weighted_complete_tail')):
            shift_lo, shift_hi = changes[mode]
            triangle[0] = [lo + shift_lo, hi + shift_hi]
    if mode == 'synthetic-selected-negative' and kind == 'A_model':
        replacement = []
        for i in range(DIM):
            for j in range(i, DIM):
                value = -Fraction(2 * SCALE, 2 * (2 * i + parity) + 1) if i == j else Fraction(0)
                replacement.append([floor_q(value) - 1, ceil_q(value) + 1])
        payload['upper_triangle'] = replacement
    elif mode == 'numerical-width-uncertainty' and kind == 'A_model':
        triangle[0] = [lo - SCALE, hi + SCALE]

def packet(directory, source, matrices, mode, changes):
    result = copy.deepcopy(source)
    (directory / 'matrices').mkdir()
    mutations = []
    for key, (original_raw, original) in matrices.items():
        payload = copy.deepcopy(original)
        modify(payload, mode, changes)
        validate_payload(payload, original['kind'], original['parity'])
        changed = payload != original
        raw = gzip.compress(encode(payload), compresslevel=9, mtime=0) if changed else original_raw
        relative = 'matrices/' + key + '.json.gz'
        fresh(confined(directory, relative), raw)
        result['matrices'][key] = {'path': relative, 'sha256': digest(raw), 'size': len(raw)}
        if changed:
            mutations.append({'family': key, 'original_sha256': digest(original_raw),
                              'modified_sha256': digest(raw),
                              'original_cell_00': original['upper_triangle'][0],
                              'modified_cell_00': payload['upper_triangle'][0]})
    if mode == 'underpaid-terminal-inverseweight':
        result['inverse_weight_uppers'][-1] = '0'
    raw = encode(result)
    fresh(directory / 'source.json', raw)
    return result, digest(raw), mutations

def native_probe(native, declaration, reconstructed, source, source_sha, directory, kind, expected):
    started = time.monotonic()
    record = {'consumer_sha256': NATIVE_PIN, 'source_sha256': source_sha,
              'scope': 'SUBSET parity 0; shared fresh independent even reconstruction',
              'shared_control': '../native-even-control.json',
              'predicate': 'validate_weights' if kind is None else 'check_matrix',
              'family': None if kind is None else kind + '-0',
              'expected': expected, 'status': 'SOURCE_PROBE_DID_NOT_REJECT',
              'complete_source_audit': False, 'production_admission': False}
    passed = False
    try:
        # Re-read retained packet, rather than bypassing its serialized source.
        retained_raw = (directory / 'source.json').read_bytes()
        require(digest(retained_raw) == source_sha, 'retained probe source binding')
        retained = native.load(retained_raw)
        require(retained == source, 'retained probe packet differs')
        if kind is None:
            native.validate_weights(retained, declaration)
        else:
            native.check_matrix(retained, directory, kind, 0, reconstructed[kind])
    except Exception as error:
        record.update({'status': 'REJECT_NATIVE_SUBSET_SOURCE_PROBE',
                       'error_type': type(error).__name__, 'error': str(error)})
        passed = isinstance(error, ValueError) and str(error).startswith(expected)
    record.update({'passed': passed, 'elapsed_seconds': time.monotonic() - started})
    fresh(directory / 'receipt.json', encode(record))
    return passed

def run(native, source, source_parent, declaration, reconstructed, output, *, source_sha256, positive_counts):
    global NATIVE_PIN
    NATIVE_PIN=digest(Path(native.__file__).read_bytes())
    output.mkdir(parents=True,exist_ok=False)
    require(set(positive_counts)==set(KINDS) and sum(positive_counts.values())==256473,
            'complete original even control must pass before false-source probes')
    matrices={}
    for key,descriptor in source['matrices'].items():
        raw=confined(source_parent,descriptor['path']).read_bytes()
        require(digest(raw)==descriptor['sha256'] and len(raw)==descriptor['size'],'positive matrix binding')
        payload=load(gzip.decompress(raw));kind,parity=key.rsplit('-',1)
        validate_payload(payload,kind,int(parity));matrices[key]=(raw,payload)
    changes,evidence=prime5_changes(native,native.rational(source['weighted_tail_norm_upper']))
    cases=[]
    definitions=(('wrongactual-lowconstant','A_model','source enclosure fails at A_model-0 cell (0, 0)'),
        ('underpaidweightedhead','weighted_head','source enclosure fails at weighted_head-0 cell (0, 0)'),
        ('omitted-complete-physicalexterior','weighted_complete_tail','source enclosure fails at weighted_complete_tail-0 cell (0, 0)'),
        ('underpaid-terminal-inverseweight',None,'inverse weights differ from declaration'),
        ('omitted-prime5-low-term','A_model','source enclosure fails at A_model-0 cell (0, 0)'),
        ('omitted-prime5-mixed-square','weighted_complete_tail','source enclosure fails at weighted_complete_tail-0 cell (0, 0)'))
    for name,kind,expected in definitions:
        directory=output/name;directory.mkdir()
        altered,source_sha,mutations=packet(directory,source,matrices,name,changes)
        passed=native_probe(native,declaration,reconstructed,altered,source_sha,directory,kind,expected)
        require(passed,'false analytical input did not reach the expected mathematical rejection: '+name)
        cases.append({'case':name,'passed':passed,'source_sha256':source_sha,'mutations':mutations})
    report={'format':'t081-current-audit-native-controls-v1','status':'PASS_SIX_NATIVE_SUBSET_CONTROLS',
        'consumer_sha256':NATIVE_PIN,'source_sha256':source_sha256,
        'original_even_entries_already_checked':256473,
        'scope':'six subset probes after the current full audit checked all three original even families; not independent full malformed-source audits',
        'prime5_changes':evidence,'cases':cases,'production_admission':False}
    fresh(output/'native-controls.json',encode(report))
