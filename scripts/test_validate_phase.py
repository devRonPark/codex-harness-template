import json
import sys
import unittest
from contextlib import redirect_stderr
from io import StringIO
from pathlib import Path
from tempfile import TemporaryDirectory

sys.path.insert(0, str(Path(__file__).parent))

import validate_phase


def write_json(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(f"{json.dumps(data, indent=2)}\n", encoding="utf-8")


class ValidatePhaseTests(unittest.TestCase):
    def test_accepts_valid_phase_metadata(self):
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_json(
                root / "phases" / "index.json",
                {"phases": [{"dir": "demo-phase", "status": "pending"}]},
            )
            write_json(
                root / "phases" / "demo-phase" / "index.json",
                {
                    "project": "Demo",
                    "phase": "demo-phase",
                    "steps": [
                        {
                            "step": 0,
                            "name": "first-step",
                            "status": "completed",
                            "summary": "Created the initial scaffold.",
                        },
                        {"step": 1, "name": "second-step", "status": "pending"},
                    ],
                },
            )
            (root / "phases" / "demo-phase" / "step0.md").write_text("# Step 0\n", encoding="utf-8")
            (root / "phases" / "demo-phase" / "step1.md").write_text("# Step 1\n", encoding="utf-8")

            result = validate_phase.validate_phase(root, "demo-phase")

            self.assertTrue(result.valid)
            self.assertEqual(result.errors, [])

    def test_reports_registry_phase_and_step_errors(self):
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_json(
                root / "phases" / "index.json",
                {"phases": [{"dir": "other-phase", "status": "pending"}]},
            )
            write_json(
                root / "phases" / "demo-phase" / "index.json",
                {
                    "project": "Demo",
                    "phase": "wrong-phase",
                    "steps": [
                        {"step": 1, "name": "first-step", "status": "done"},
                        {"step": 2, "name": "Bad Step", "status": "completed"},
                        {"step": 3, "name": "third-step", "status": "blocked"},
                        {"step": 4, "name": "fourth-step", "status": "error"},
                    ],
                },
            )
            (root / "phases" / "demo-phase" / "step1.md").write_text("# Step 1\n", encoding="utf-8")

            result = validate_phase.validate_phase(root, "demo-phase")

            self.assertFalse(result.valid)
            self.assertIn("phases/index.json has no entry for phase 'demo-phase'", result.errors)
            self.assertIn(
                "phases/demo-phase/index.json phase field must be 'demo-phase', got 'wrong-phase'",
                result.errors,
            )
            self.assertIn("phases/demo-phase/index.json steps must be numbered 0..3", result.errors)
            self.assertIn("step 1 status must be one of: blocked, completed, error, pending", result.errors)
            self.assertIn("step 2 name must use lowercase kebab-case", result.errors)
            self.assertIn("step 2 completed status requires non-empty summary", result.errors)
            self.assertIn("step 3 blocked status requires non-empty blocked_reason", result.errors)
            self.assertIn("step 4 error status requires non-empty error_message", result.errors)
            self.assertIn("missing step file: phases/demo-phase/step0.md", result.errors)

    def test_rejects_invalid_status_in_top_index(self):
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_json(
                root / "phases" / "index.json",
                {"phases": [{"dir": "demo-phase", "status": "done"}]},
            )
            write_json(
                root / "phases" / "demo-phase" / "index.json",
                {
                    "project": "Demo",
                    "phase": "demo-phase",
                    "steps": [{"step": 0, "name": "first-step", "status": "pending"}],
                },
            )
            (root / "phases" / "demo-phase" / "step0.md").write_text("# Step 0\n", encoding="utf-8")

            result = validate_phase.validate_phase(root, "demo-phase")

            self.assertFalse(result.valid)
            self.assertIn(
                "phases/index.json phase 'demo-phase' status must be one of: blocked, completed, error, pending",
                result.errors,
            )

    def test_cli_returns_nonzero_for_invalid_phase(self):
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_json(root / "phases" / "index.json", {"phases": []})

            with redirect_stderr(StringIO()):
                exit_code = validate_phase.main(["demo-phase", "--root", str(root)])

            self.assertEqual(exit_code, 1)


if __name__ == "__main__":
    unittest.main()
