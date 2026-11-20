"""Streamed integer checks and source-conditional rational assessment.

A nonzero determinant modulo the single verified prime proves nonsingularity.
A zero residue does not prove singularity. Neither result accepts analytic source
bounds or admits a production theorem.
"""
from fractions import Fraction
from math import lcm
from operator import index


_PRIME = 65521
_BLOCK_KEYS = frozenset({
    "width", "goal", "modular_nonsingular", "margin", "tau",
    "direction_upper", "direction_mass", "direction_index",
})


def _integer(value, name, *, minimum=0):
    if type(value) is not int:
        raise TypeError(f"{name} must be a Python int")
    if value < minimum:
        raise ValueError(f"{name} must be at least {minimum}")
    return value


def _rational(value, name):
    if type(value) not in (int, Fraction):
        raise TypeError(f"{name} must be an exact int or Fraction")
    return Fraction(value)


def _shape(dimension, panel_size, read_tile):
    _integer(dimension, "dimension", minimum=1)
    _integer(panel_size, "panel_size", minimum=1)
    if not callable(read_tile):
        raise TypeError("read_tile must be callable")


def _tile(read_tile, i, j, rows, cols):
    tile = read_tile(i, j)
    if tile.nrows() != rows or tile.ncols() != cols:
        raise ValueError(f"tile at ({i}, {j}) has the wrong shape")
    return tile


def _entry(tile, r, c):
    value = tile[r, c]
    if type(value) is bool:
        raise TypeError("tile entries must be integers, not bool")
    # __index__ accepts native integer entries without rounding rationals/floats.
    return index(value)


def full_modular_nonsingularity(dimension, panel_size, read_tile, *, workspace_bytes):
    """Check the determinant of the complete transform at one fixed prime.

    The account reserves four dense word payloads, linear row/pivot space,
    and fixed overhead. This includes the input and a determinant copy with
    two additional payloads of workspace headroom. Admission precedes importing
    FLINT, allocating the modular matrix, and reading any source tile.
    """
    _shape(dimension, panel_size, read_tile)
    _integer(workspace_bytes, "workspace_bytes")
    word_payload_bytes = 8 * dimension * dimension
    workspace_account_bytes = 4 * word_payload_bytes + 256 * dimension + 16384
    if workspace_account_bytes > workspace_bytes:
        raise MemoryError("complete modular determinant exceeds workspace_bytes")

    # Verify the fixed modulus by trial division using integer arithmetic only.
    divisor = 2
    while divisor * divisor <= _PRIME:
        if _PRIME % divisor == 0:
            raise ValueError("modular determinant modulus must be prime")
        divisor += 1

    from flint import nmod_mat

    matrix = nmod_mat(dimension, dimension, _PRIME)
    global_input_entries = 0
    for i in range(0, dimension, panel_size):
        rows = min(panel_size, dimension - i)
        for j in range(0, dimension, panel_size):
            cols = min(panel_size, dimension - j)
            tile = _tile(read_tile, i, j, rows, cols)
            for r in range(rows):
                for c in range(cols):
                    matrix[i + r, j + c] = _entry(tile, r, c) % _PRIME
                    global_input_entries += 1
            del tile
    residue = int(matrix.det())
    return {
        "prime": _PRIME,
        "residue": residue,
        "nonsingular": residue != 0,
        "global_input_entries": global_input_entries,
        "word_payload_bytes": word_payload_bytes,
        "workspace_account_bytes": workspace_account_bytes,
    }


def mass_trace(dimension, parity, transform_bits, panel_size, read_tile):
    """Compute physical column masses and their trace without forming a Gram matrix."""
    _shape(dimension, panel_size, read_tile)
    _integer(parity, "parity")
    if parity not in (0, 1):
        raise ValueError("parity must be 0 or 1")
    _integer(transform_bits, "transform_bits")
    mass_lcm = 1
    for i in range(dimension):
        mass_lcm = lcm(mass_lcm, 2 * (2 * i + parity) + 1)
    mass_weights = [2 * mass_lcm // (2 * (2 * i + parity) + 1)
                    for i in range(dimension)]
    direction_sums = [0] * dimension
    for i in range(0, dimension, panel_size):
        rows = min(panel_size, dimension - i)
        for j in range(0, dimension, panel_size):
            cols = min(panel_size, dimension - j)
            tile = _tile(read_tile, i, j, rows, cols)
            for r in range(rows):
                weight = mass_weights[i + r]
                for c in range(cols):
                    value = _entry(tile, r, c)
                    direction_sums[j + c] += weight * value * value
            del tile
    denominator = mass_lcm * (1 << (2 * transform_bits))
    return {
        "mass_lcm": mass_lcm,
        "mass_weights": mass_weights,
        "minimum_mass": Fraction(2, 2 * (2 * (dimension - 1) + parity) + 1),
        "tau": Fraction(sum(direction_sums), denominator),
        "direction_masses": [Fraction(value, denominator) for value in direction_sums],
    }


def assess(blocks, *, eta, m, b_K, delta, control=False):
    """Assess two parity blocks, conditional on their supplied analytic bounds."""
    if type(blocks) not in (list, tuple) or len(blocks) != 2:
        raise ValueError("blocks must contain the even and odd blocks in order")
    if type(control) is not bool:
        raise TypeError("control must be bool")
    eta = _rational(eta, "eta")
    m = _rational(m, "m")
    b_K = _rational(b_K, "b_K")
    delta = _rational(delta, "delta")
    if eta <= 0 or m <= 0 or b_K < 0 or delta < 0:
        raise ValueError("eta and m must be positive; b_K and delta must be nonnegative")
    checked = []
    for block in blocks:
        if type(block) is not dict or block.keys() != _BLOCK_KEYS:
            raise ValueError("each block must contain exactly the assessment fields")
        if type(block["modular_nonsingular"]) is not bool:
            raise TypeError("modular_nonsingular must be bool")
        _integer(block["direction_index"], "direction_index")
        values = {key: _rational(block[key], key) for key in (
            "width", "goal", "margin", "tau", "direction_upper", "direction_mass",
        )}
        if values["width"] < 0 or values["goal"] < 0:
            raise ValueError("width and goal must be nonnegative")
        values["modular_nonsingular"] = block["modular_nonsingular"]
        checked.append(values)

    width_passed = all(block["width"] <= block["goal"] for block in checked)
    global_nonsingularity = all(block["modular_nonsingular"] for block in checked)
    positive_paid_lower = width_passed and global_nonsingularity and all(
        block["margin"] > 0 and block["tau"] > 0 for block in checked
    )
    sigma = gamma = None
    if not width_passed:
        status = "WIDTH_GOAL_FAILED"
    elif positive_paid_lower:
        sigma = min(block["margin"] / block["tau"] for block in checked)
        gamma = min(
            sigma / (1 + 2 * (b_K + delta) ** 2 / (eta ** 2 * m ** 2)),
            eta * m / 2,
        )
        status = "PASS_EXACT_PAID_LOWER_SOURCE_CONDITIONAL"
    elif any(block["direction_upper"] < 0 and block["direction_mass"] > 0
             for block in checked):
        status = "SELECTED_PAID_LOWER_NEGATIVE_NOT_WEIL_NEGATIVITY"
    elif not global_nonsingularity:
        status = "UNRESOLVED_MODULAR_NONSINGULARITY"
    else:
        status = "UNRESOLVED_PAID_LOWER"
    return {
        "status": status,
        "sigma": sigma,
        "gamma": gamma,
        "width_passed": width_passed,
        "global_nonsingularity": global_nonsingularity,
        "positive_paid_lower": positive_paid_lower,
        "source_conditional": True,
        "control": control,
        "analytical_source_acceptance": False,
        "production_admission": False,
    }
