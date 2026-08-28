"""Explicit real-artifact acceptance for the retained theorem proof chain.

This module is excluded from ordinary pytest runs by the ``retained_proofs``
marker. Run it deliberately when the exact theorem artifacts themselves must be
replayed through the current independent Rust verifier.
"""

from __future__ import annotations

import subprocess
import sys

import pytest

from scripts.cert.verify_retained_proofs import REPOSITORY_ROOT


@pytest.mark.retained_proofs
def test_real_retained_proof_chain() -> None:
    completed = subprocess.run(
        [sys.executable, "-m", "scripts.cert.verify_retained_proofs"],
        cwd=REPOSITORY_ROOT,
        capture_output=True,
        text=True,
        check=False,
        timeout=600,
    )

    assert completed.returncode == 0, completed.stderr or completed.stdout
    lines = [line.strip() for line in completed.stdout.splitlines() if line.strip()]
    assert lines == [
        "C-0050 HASH PASS VERIFY PASS T=7/20 N=32",
        "C-0051 HASH PASS VERIFY PASS T=2/5 N=40",
        "C-0052 HASH PASS VERIFY PASS T=17/40 N=48",
        "C-0053 HASH PASS VERIFY PASS T=9/20 N=56",
        "C-0054 HASH PASS VERIFY PASS T=19/40 N=68",
        "C-0055 HASH PASS VERIFY PASS T=1/2 N=80",
        "C-0056 HASH PASS VERIFY PASS T=21/40 N=96",
        "RETAINED PROOF CHAIN: PASS - 7/7",
    ]
    assert completed.stderr == ""
