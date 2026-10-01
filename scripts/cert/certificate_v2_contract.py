"""Structural contract helpers for rh-weil-certificate-v2.

This module deliberately separates syntax/structure validation from theorem
admission. A certificate can satisfy the v2 structural contract while still
being ineligible for theorem verification. The production v2 whitelist starts
empty and must be changed explicitly in a later admission slice.
"""

from __future__ import annotations

import json
import math
from fractions import Fraction
from functools import lru_cache
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator, FormatChecker


CERTIFICATE_FORMAT_V2 = "rh-weil-certificate-v2"
CLAIM_PROFILE_V2 = "multi_prime_power_legendre_schur"
REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
SCHEMA_PATH_V2 = (
    REPOSITORY_ROOT / "docs" / "contracts" / "rh-weil-certificate-v2.json"
)

# Production theorem admission is intentionally empty in P6. Structural
# validation must never be interpreted as theorem admission.
V2_ALLOWED_CONFIGURATIONS: frozenset[tuple[Fraction, int]] = frozenset()

_TERM_INTERVAL_FIELDS = (
    "log_m",
    "tau",
    "von_mangoldt",
    "coefficient",
    "compressed_shift_norm_bound",
    "complement_contribution",
)


@lru_cache(maxsize=1)
def certificate_v2_validator() -> Draft202012Validator:
    schema = json.loads(SCHEMA_PATH_V2.read_text(encoding="utf-8"))
    Draft202012Validator.check_schema(schema)
    return Draft202012Validator(schema, format_checker=FormatChecker())


def _format_schema_error(error: Any) -> str:
    path = "$"
    for part in error.absolute_path:
        path += f"[{part}]" if isinstance(part, int) else f".{part}"
    return f"{path}: {error.message}"


def _first_float_path(value: Any, path: str = "$") -> str | None:
    if isinstance(value, float):
        return path
    if isinstance(value, dict):
        for key, child in value.items():
            found = _first_float_path(child, f"{path}.{key}")
            if found is not None:
                return found
    elif isinstance(value, list):
        for index, child in enumerate(value):
            found = _first_float_path(child, f"{path}[{index}]")
            if found is not None:
                return found
    return None


def _canonical_fraction(num: str, den: str, path: str) -> Fraction:
    value = Fraction(int(num), int(den))
    if str(value.numerator) != num or str(value.denominator) != den:
        raise ValueError(f"{path} must be a reduced canonical rational")
    return value


def _validate_interval(value: dict[str, Any], path: str) -> None:
    lo = _canonical_fraction(value["lo_num"], value["lo_den"], f"{path}.lo")
    hi = _canonical_fraction(value["hi_num"], value["hi_den"], f"{path}.hi")
    if lo > hi:
        raise ValueError(f"{path} has lower endpoint greater than upper endpoint")


def _is_prime(n: int) -> bool:
    if n < 2:
        return False
    if n == 2:
        return True
    if n % 2 == 0:
        return False
    limit = math.isqrt(n)
    divisor = 3
    while divisor <= limit:
        if n % divisor == 0:
            return False
        divisor += 2
    return True


def _validate_full_matrix(
    value: dict[str, Any],
    dimension: int,
    path: str,
    *,
    exact: bool,
) -> None:
    if value["dimension"] != dimension:
        raise ValueError(f"{path}.dimension must equal {dimension}")
    entries = value["entries"]
    if len(entries) != dimension * dimension:
        raise ValueError(
            f"{path}.entries must contain exactly {dimension * dimension} entries"
        )
    coordinates: set[tuple[int, int]] = set()
    for index, entry in enumerate(entries):
        coordinate = (entry["row"], entry["col"])
        if coordinate[0] >= dimension or coordinate[1] >= dimension:
            raise ValueError(f"{path}.entries[{index}] coordinate is outside the matrix")
        if coordinate in coordinates:
            raise ValueError(f"{path}.entries contains duplicate coordinate {coordinate}")
        coordinates.add(coordinate)
        if exact:
            _canonical_fraction(
                entry["num"],
                entry["den"],
                f"{path}.entries[{index}]",
            )
        else:
            _validate_interval(entry, f"{path}.entries[{index}]")


def validate_certificate_v2_schema(certificate: dict[str, Any]) -> tuple[bool, str]:
    """Validate only the closed v2 JSON Schema."""
    validator = certificate_v2_validator()
    errors = sorted(
        validator.iter_errors(certificate),
        key=lambda error: tuple(str(part) for part in error.absolute_path),
    )
    if errors:
        return False, _format_schema_error(errors[0])
    return True, "ok"


def validate_certificate_v2_structure(certificate: dict[str, Any]) -> tuple[bool, str]:
    """Validate canonical cross-field structure without granting theorem status."""
    valid, message = validate_certificate_v2_schema(certificate)
    if not valid:
        return valid, message

    float_path = _first_float_path(certificate)
    if float_path is not None:
        return False, f"{float_path}: floating-point values are forbidden"

    try:
        support_obj = certificate["support_T"]
        support = _canonical_fraction(
            support_obj["num"],
            support_obj["den"],
            "$.support_T",
        )
        if support <= 0:
            raise ValueError("$.support_T must be strictly positive")
        if support_obj["frac"] != f"{support.numerator}/{support.denominator}":
            raise ValueError("$.support_T.frac must equal canonical num/den")

        dimension = certificate["dimension"]
        if certificate["basis"]["dimension"] != dimension:
            raise ValueError("$.basis.dimension must equal $.dimension")
        if certificate["tail_bound"]["harmonic_index"] != dimension:
            raise ValueError("$.tail_bound.harmonic_index must equal $.dimension")

        for name in ("c_T", "rho_R"):
            _validate_interval(certificate["constants"][name], f"$.constants.{name}")

        previous_m = 1
        for index, term in enumerate(certificate["arithmetic_terms"]):
            path = f"$.arithmetic_terms[{index}]"
            m = term["m"]
            base_prime = term["base_prime"]
            exponent = term["exponent"]
            if m <= previous_m:
                raise ValueError(
                    "$.arithmetic_terms must be strictly increasing by m"
                )
            previous_m = m
            if not _is_prime(base_prime):
                raise ValueError(f"{path}.base_prime must be prime")
            if base_prime**exponent != m:
                raise ValueError(
                    f"{path} identity must satisfy m = base_prime^exponent"
                )
            for field in _TERM_INTERVAL_FIELDS:
                _validate_interval(term[field], f"{path}.{field}")

        _validate_full_matrix(
            certificate["matrix"],
            dimension,
            "$.matrix",
            exact=False,
        )
        for name in ("GV", "GP", "GR"):
            _validate_full_matrix(
                certificate["schur_proof"][name],
                dimension,
                f"$.schur_proof.{name}",
                exact=False,
            )

        even_dimension = (dimension + 1) // 2
        odd_dimension = dimension // 2
        _validate_full_matrix(
            certificate["schur_proof"]["even_witness"],
            even_dimension,
            "$.schur_proof.even_witness",
            exact=True,
        )
        _validate_full_matrix(
            certificate["schur_proof"]["odd_witness"],
            odd_dimension,
            "$.schur_proof.odd_witness",
            exact=True,
        )
    except (KeyError, TypeError, ValueError, ZeroDivisionError) as exc:
        return False, str(exc)

    return True, "ok"


def is_allowed_v2_configuration(support: Fraction, dimension: int) -> bool:
    """Return production theorem admission for a v2 support/dimension pair."""
    return (support, dimension) in V2_ALLOWED_CONFIGURATIONS
