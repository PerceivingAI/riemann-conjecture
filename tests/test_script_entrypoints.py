"""Smoke and validation tests for the standalone research-script entry points."""

from __future__ import annotations

import importlib
import subprocess
import sys

import pytest

from scripts.positivity_kernel_diagnostics import laguerre_l1
from scripts.weil_support_geometry import active_chain_vertices


PACKAGE_ENTRYPOINTS = [
    "scripts.kernel_scan",
    "scripts.prime_range_decomposition",
    "scripts.prime_trace",
    "scripts.uniform_phase_diagnostics",
    "scripts.window_diagnostics",
    "scripts.zero_mode_bins",
]


def test_support_chain_threshold_has_no_epsilon_dead_zone() -> None:
    import math

    shift = math.log(2.0)
    ratio = 2.0 + 5e-15
    support = ratio * shift / 2.0
    assert 2.0 * support / shift > 2.0
    assert active_chain_vertices(support, shift) == 3


def test_diagnostic_laguerre_rejects_negative_degree() -> None:
    with pytest.raises(ValueError, match="nonnegative"):
        laguerre_l1(-1, 0.0)


@pytest.mark.parametrize("module_name", PACKAGE_ENTRYPOINTS)
def test_diagnostic_script_is_package_importable(module_name: str) -> None:
    importlib.import_module(module_name)


@pytest.mark.parametrize(
    ("module_name", "args", "message"),
    [
        ("scripts.kernel_scan", ["--steps", "0"], "steps must be >= 1"),
        ("scripts.prime_range_decomposition", ["--max-m", "1"], "max-m must be >= 2"),
        ("scripts.prime_trace", ["--precision", "0"], "precision must be >= 1"),
        ("scripts.uniform_phase_diagnostics", ["--dps", "0"], "dps must be >= 1"),
        ("scripts.window_diagnostics", ["--s0", "3", "--betas", "3"], "every beta must be < s0"),
        (
            "scripts.zero_mode_bins",
            ["--s0", "3", "--beta", "3", "--n", "1", "--u-bins", "0,0.01", "--steps-per-bin", "2"],
            "beta must be < s0",
        ),
        ("scripts.verify_identities", ["--max-n", "0"], "max-n must be >= 1"),
        ("scripts.chirp_window_diagnostics", ["--u", "0"], "u must contain values strictly between 0 and 1"),
        ("scripts.bilinear_chirp_geometry", ["--u", "1"], "u must contain values strictly between 0 and 1"),
    ],
)
def test_invalid_cli_domain_fails_closed(
    module_name: str, args: list[str], message: str
) -> None:
    completed = subprocess.run(
        [sys.executable, "-m", module_name, *args],
        capture_output=True,
        text=True,
        timeout=30,
        check=False,
    )
    assert completed.returncode != 0
    assert message in completed.stderr
