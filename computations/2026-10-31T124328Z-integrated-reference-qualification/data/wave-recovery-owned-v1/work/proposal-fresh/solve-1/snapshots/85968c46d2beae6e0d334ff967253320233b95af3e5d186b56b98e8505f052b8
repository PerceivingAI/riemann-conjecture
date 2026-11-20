"""Byte-admitted ephemeral working sets; persisted operands remain authoritative."""
from collections import OrderedDict
import sys

from scripts.whole_source.contract import ContractError

MIB = 1024*1024
PREPARED_BYTES = 32*MIB
SOURCE_DECODED_BYTES = 64*MIB
PANEL_DECODED_BYTES = 8*MIB


def python_bytes(value):
    """Price Python-owned canonical values, never native backend payloads."""
    if type(value) in (tuple,list):
        return sys.getsizeof(value)+sum(python_bytes(part) for part in value)
    if type(value) is dict:
        return sys.getsizeof(value)+sum(python_bytes(k)+python_bytes(v) for k,v in value.items())
    if type(value) not in (str,bytes,int,bool,type(None)):
        raise TypeError('native working values require an explicit limb/storage account')
    return sys.getsizeof(value)


class WorkingSet:
    """One bounded LRU per explicit immutable policy, including replacement overlap."""
    def __init__(self,limit):
        if type(limit) is not int or limit < 4096:
            raise ContractError('invalid reuse byte allowance')
        self.limit = limit
        self.policy = None
        self.values = OrderedDict()
        self.resident = 4096
        self.peak = self.resident
        self.hits = self.misses = 0

    def bind(self,policy):
        if policy != self.policy:
            self.values.clear()
            self.resident = 4096
            self.policy = policy
        return self

    def get(self,key):
        entry = self.values.get(key)
        if entry is None:
            self.misses += 1
            return None
        self.values.move_to_end(key)
        self.hits += 1
        return entry[0]

    def reserve(self,key,payload_bytes):
        """Evict before constructing a replacement; caller prices active operands."""
        charge = payload_bytes+512+python_bytes(key)
        if charge+4096 > self.limit:
            return False
        old = self.values.pop(key,None)
        if old is not None:
            self.resident -= old[1]
        while self.resident+charge > self.limit:
            _,entry = self.values.popitem(last=False)
            self.resident -= entry[1]
        return True

    def put(self,key,value,payload_bytes):
        if not self.reserve(key,payload_bytes):
            return value
        charge = payload_bytes+512+python_bytes(key)
        self.values[key] = (value,charge)
        self.resident += charge
        self.peak = max(self.peak,self.resident)
        return value


def panel_inputs(problem,inputs):
    values = tuple(inputs)
    if (not 1 <= len(values) <= 2 or any(type(n) is not int or not 0 <= n < problem.N for n in values)
            or values != tuple(sorted(set(values))) or len({n%2 for n in values}) != 1):
        raise ValueError('one or two ordered same-parity input columns required')
    return values


def preparation_policy(problem,precision,threads):
    return (problem.support,problem.N,problem.M,problem.K,tuple(problem.kernel_coefficients),precision,threads)

def exact_polynomial_bytes(degree):
    # Legendre numerator/denominator bounds, native limb over-allocation and slots.
    return 512+(degree+1)*(128+2*((4*(degree+1)+7)//8))
