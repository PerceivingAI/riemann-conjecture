"""Behavior regressions for the successor execution measurement tools."""
from __future__ import annotations

import importlib.util
import io
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
BUNDLE = ROOT / "computations/2026-10-28T024305Z-t081-execution-corrections"


def load_module(filename, name):
    spec = importlib.util.spec_from_file_location(name, BUNDLE / filename)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


instrument = load_module("instrument-t081-v2.py", "t081_profile_instrument_tests")
driver = load_module("measure-t081-execution-v2.py", "t081_profile_driver_tests")


class MemoryAndSamplingTests(unittest.TestCase):
    def test_os_peak_and_final_sample_survive_lower_current_working_set(self):
        probe = instrument.Instrumentation(ROOT, BUNDLE / "instrument-t081-v2.py")
        values = iter([
            {"working_set": 100, "peak_working_set": 800, "private_bytes": None},
            {"working_set": 50, "peak_working_set": 1200, "private_bytes": 70},
        ])
        with patch.object(instrument, "_process_memory", side_effect=lambda: next(values)), \
                patch.object(instrument, "_thread_count", return_value=2), \
                patch.object(instrument, "SAMPLE_SECONDS", 60):
            probe.start()
            probe.finish()
        report = probe.report({})
        self.assertEqual(report["peak_working_set_bytes"], 1200)
        self.assertEqual(report["sampled_peak_working_set_bytes"], 100)
        self.assertEqual(report["peak_private_bytes"], 70)
        self.assertEqual(report["memory_series"][-1][1:3], [50, 70])

    def test_unknown_memory_is_null_not_zero_and_virtual_is_not_private(self):
        with patch.object(instrument, "WIN", False), \
                patch("builtins.open", return_value=io.StringIO(
                    "VmRSS:\t12 kB\nVmHWM:\t18 kB\nVmSize:\t900 kB\n")):
            counters = instrument._process_memory()
        self.assertEqual(counters["working_set"], 12 * 1024)
        self.assertEqual(counters["peak_working_set"], 18 * 1024)
        self.assertEqual(counters["virtual_bytes"], 900 * 1024)
        self.assertIsNone(counters["private_bytes"])
        probe = instrument.Instrumentation(ROOT, BUNDLE / "instrument-t081-v2.py")
        probe.observe_memory(counters, "source")
        probe.observe_memory({"working_set": None, "private_bytes": None}, "source")
        report = probe.report({})
        self.assertEqual(report["peak_working_set_bytes"], 18 * 1024)
        self.assertIsNone(report["peak_private_bytes"])
        empty = instrument.Instrumentation(ROOT, BUNDLE / "instrument-t081-v2.py")
        self.assertIsNone(empty.report({})["peak_working_set_bytes"])

    def test_live_os_memory_counters_have_correct_available_fields(self):
        counters = instrument._process_memory()
        if instrument.WIN:
            self.assertGreater(counters["private_bytes"], 0)
            self.assertGreaterEqual(counters["peak_working_set"], counters["working_set"])
            self.assertIsNone(counters["virtual_bytes"])
        elif Path("/proc/self/status").exists():
            self.assertGreater(counters["virtual_bytes"], 0)
            self.assertIsNone(counters["private_bytes"])

    def test_nested_stack_selects_innermost_matching_frame(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            program = root / "nested.py"
            program.write_text("def outer(callback):\n    return inner(callback)\n"
                               "def inner(callback):\n    return callback()\n", encoding="utf-8")
            module = instrument.load_module(program, "t081_nested_stack_test")
            probe = instrument.Instrumentation(root, BUNDLE / "instrument-t081-v2.py")
            location = module.outer(probe._main_frame)
            self.assertEqual(location[0], "nested.py")
            self.assertEqual(location[2], "inner")

    def test_child_run_preserves_check_and_input_semantics(self):
        child = instrument.ChildAccounting()
        run = child.wrap(subprocess.run)
        result = run([sys.executable, "-c", "print(input().upper())"],
                     input="measured\n", text=True, capture_output=True, check=True)
        self.assertEqual(result.stdout.strip(), "MEASURED")
        with self.assertRaises(subprocess.CalledProcessError):
            run([sys.executable, "-c", "raise SystemExit(6)"], check=True)
        self.assertEqual(child.records[-1]["returncode"], 6)


class HarnessLifecycleTests(unittest.TestCase):
    def invoke(self, root, program_text, *, level="coarse", report_exists=False):
        (root / "scripts").mkdir()
        (root / "computations").mkdir()
        program = root / "program.py"
        program.write_text(program_text, encoding="utf-8")
        report = root / "report.json"
        if report_exists:
            report.write_bytes(b"untouched")
        command = [sys.executable, "-I", "-B", str(BUNDLE / "instrument-t081-v2.py"),
                   "--program", str(program), "--kind", "build", "--level", level,
                   "--report", str(report)]
        result = subprocess.run(command, cwd=root, capture_output=True, text=True)
        return result, report

    def test_nested_timers_do_not_double_count_child_time(self):
        probe = instrument.Instrumentation(ROOT, BUNDLE / "instrument-t081-v2.py")
        target = SimpleNamespace(inner=lambda: None)
        target.outer = lambda: target.inner()
        probe.wrap(target, "inner")
        probe.wrap(target, "outer")
        with patch.object(instrument.time, "perf_counter", side_effect=[0, 2, 5, 8]), \
                patch.object(instrument.time, "process_time", side_effect=[0, 2, 5, 8]):
            target.outer()
        stages = {stage["stage"]: stage for stage in probe.report({})["stages"]}
        self.assertEqual(stages["outer"]["inclusive_wall_seconds"], 8)
        self.assertEqual(stages["inner"]["inclusive_wall_seconds"], 3)
        self.assertEqual(stages["outer"]["exclusive_wall_seconds"], 5)
        self.assertEqual(sum(stage["exclusive_wall_seconds"] for stage in stages.values()), 8)

    def test_nonzero_return_and_exception_are_recorded_as_failures(self):
        for body, code, error in [("return 9", 9, "exit status 9"),
                                  ("raise RuntimeError('actual failure')", None, "actual failure")]:
            with self.subTest(body=body), tempfile.TemporaryDirectory() as temporary:
                result, report = self.invoke(Path(temporary), f"def main():\n    {body}\n")
                self.assertNotEqual(result.returncode, 0)
                payload = json.loads(report.read_bytes())
                self.assertEqual(payload["status"], "FAILED")
                self.assertIn(error, payload["error"])
                if code is not None:
                    self.assertEqual(payload["exit_code"], code)

    def test_existing_report_is_rejected_before_import_side_effect(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            result, report = self.invoke(root,
                "from pathlib import Path\nPath('executed').write_text('bad')\ndef main(): return 0\n",
                report_exists=True)
            self.assertNotEqual(result.returncode, 0)
            self.assertEqual(report.read_bytes(), b"untouched")
            self.assertFalse((root / "executed").exists())

    def test_in_process_failure_restores_subprocess_run_and_argv(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / "scripts").mkdir()
            (root / "computations").mkdir()
            program = root / "fail.py"
            program.write_text("def main():\n    raise ValueError('restore me')\n", encoding="utf-8")
            report = root / "report.json"
            original_run = subprocess.run
            argv = ["instrument", "--program", str(program), "--kind", "build", "--report", str(report)]
            with patch.object(Path, "cwd", return_value=root), patch.object(sys, "argv", argv):
                with self.assertRaisesRegex(ValueError, "restore me"):
                    instrument.main()
                self.assertIs(subprocess.run, original_run)
                self.assertIs(sys.argv, argv)
            self.assertEqual(json.loads(report.read_bytes())["status"], "FAILED")


class DriverCleanupTests(unittest.TestCase):
    def fixture(self, root, *, failure=False):
        bundle = "computations/2026-10-27T140745Z-t081-complete-gram-attempt"
        source_bytes = b'{"matrices": {}}\n'
        source_program = (
            "import argparse\nfrom pathlib import Path\n"
            "def main():\n"
            "    p = argparse.ArgumentParser()\n"
            "    p.add_argument('--inputs'); p.add_argument('--output')\n"
            "    a = p.parse_args()\n"
            + ("    raise RuntimeError('fixture execution failed')\n" if failure else
               "    Path(a.output).write_bytes(b'{\"matrices\": {}}\\n')\n    return 0\n"))
        audit_program = (
            "import argparse, json\nfrom pathlib import Path\n"
            "def main():\n"
            "    p = argparse.ArgumentParser()\n"
            "    p.add_argument('--inputs'); p.add_argument('--source'); p.add_argument('--output')\n"
            "    a = p.parse_args()\n"
            "    Path(a.output).write_text(json.dumps(dict(source=a.source, inputs=a.inputs, checked_triangular_entries=1)))\n"
            "    return 0\n")
        raws = {bundle + "/build-whole-source-v1.py": source_program.encode(),
                bundle + "/verify-whole-source-v1.py": audit_program.encode(),
                bundle + "/whole-inputs-v1.json": b"{}", "scripts/__init__.py": b"",
                bundle + "/data/source-v1.json": source_bytes}
        capture = {"files": [{"destination": name, "roles": ["expected_target_only" if name.endswith("/data/source-v1.json") else "installed"]}
                             for name in raws]}
        acceptance = root / "acceptance"
        acceptance.mkdir()
        (acceptance / "captured-source-inputs-v1.json").write_text("{}", encoding="utf-8")
        candidate = root / "candidate"
        (candidate / "data").mkdir(parents=True)
        (candidate / "data/source-audit-v1.json").write_text(json.dumps(
            dict(source="retained", inputs="retained", checked_triangular_entries=1)), encoding="utf-8")
        return capture, raws, acceptance, candidate, driver.digest(source_bytes)

    def exercise(self, root, *, phase="both", failure=False):
        capture, raws, acceptance, candidate, digest = self.fixture(root, failure=failure)
        owned = []
        temporary_directory = tempfile.TemporaryDirectory

        def tracked_directory(*args, **kwargs):
            directory = temporary_directory(*args, **kwargs)
            owned.append(Path(directory.name))
            return directory

        with patch.multiple(driver, ROOT=root, ACCEPTANCE=acceptance, CANDIDATE=candidate, SOURCE_SHA=digest), \
                patch.object(driver, "capture_closure", return_value=(capture, raws)), \
                patch.object(driver.tempfile, "TemporaryDirectory", side_effect=tracked_directory):
            try:
                result = driver.measure(phase=phase, level="coarse", profile_dir=root / "profiles")
            finally:
                self.assertEqual(len(owned), 1)
                self.assertFalse(owned[0].exists(), "owned temporary tree leaked")
        return result

    def test_success_checks_cleanup_after_context_exit(self):
        with tempfile.TemporaryDirectory() as temporary:
            result = self.exercise(Path(temporary))
            self.assertTrue(result["isolated_tree_removed"])

    def test_child_failure_still_removes_owned_tree_and_retains_failure_profile(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            with self.assertRaisesRegex(ValueError, "source_profile failed"):
                self.exercise(root, failure=True)
            profile = json.loads((root / "profiles/source-profile-v2.json").read_bytes())
            self.assertEqual(profile["status"], "FAILED")
            self.assertIn("fixture execution failed", profile["error"])

    def test_audit_only_does_not_run_failing_producer(self):
        with tempfile.TemporaryDirectory() as temporary:
            result = self.exercise(Path(temporary), phase="audit", failure=True)
            self.assertEqual([step["step"] for step in result["steps"]], ["audit_profile"])
            self.assertTrue(result["isolated_tree_removed"])

    def test_existing_profile_prevents_capture_and_execution(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            profile = root / "source-profile-v2.json"
            profile.write_bytes(b"historical")
            with patch.object(driver, "capture_closure", side_effect=AssertionError("expensive work")):
                with self.assertRaisesRegex(ValueError, "fresh profile required"):
                    driver.measure(phase="source", profile_dir=root)
            self.assertEqual(profile.read_bytes(), b"historical")


if __name__ == "__main__":
    unittest.main()
