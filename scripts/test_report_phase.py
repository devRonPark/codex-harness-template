import json
import sys
import unittest
from contextlib import redirect_stderr, redirect_stdout
from io import StringIO
from pathlib import Path
from tempfile import TemporaryDirectory

sys.path.insert(0, str(Path(__file__).parent))

import report_phase


def write_json(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(f"{json.dumps(data, indent=2)}\n", encoding="utf-8")


class ReportPhaseTests(unittest.TestCase):
    def test_reports_phase_counts_next_step_summaries_and_artifacts(self):
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_json(
                root / "phases" / "index.json",
                {"phases": [{"dir": "demo-phase", "status": "pending"}]},
            )
            write_json(
                root / "phases" / "demo-phase" / "index.json",
                {
                    "project": "Demo Harness",
                    "phase": "demo-phase",
                    "steps": [
                        {
                            "step": 0,
                            "name": "project-setup",
                            "status": "completed",
                            "summary": "Created the project files.",
                        },
                        {"step": 1, "name": "api-layer", "status": "pending"},
                        {
                            "step": 2,
                            "name": "manual-review",
                            "status": "blocked",
                            "blocked_reason": "Needs API credentials.",
                        },
                        {
                            "step": 3,
                            "name": "final-check",
                            "status": "error",
                            "error_message": "Acceptance criteria failed.",
                        },
                    ],
                },
            )
            for step_num in range(4):
                (root / "phases" / "demo-phase" / f"step{step_num}.md").write_text(
                    f"# Step {step_num}\n",
                    encoding="utf-8",
                )
            write_json(
                root / "phases" / "demo-phase" / "step0-output.json",
                {"step": 0, "exitCode": 0},
            )

            stdout = StringIO()
            with redirect_stdout(stdout):
                exit_code = report_phase.main(["demo-phase", "--root", str(root)])

            output = stdout.getvalue()
            self.assertEqual(exit_code, 0)
            self.assertIn("Phase: demo-phase", output)
            self.assertIn("Project: Demo Harness", output)
            self.assertIn("Phase status: pending", output)
            self.assertIn("Steps: 1 completed, 1 pending, 1 blocked, 1 error", output)
            self.assertIn("Next pending step: 1 (api-layer)", output)
            self.assertIn("Latest completed: Step 0 (project-setup): Created the project files.", output)
            self.assertIn("Blocked: Step 2 (manual-review): Needs API credentials.", output)
            self.assertIn("Error: Step 3 (final-check): Acceptance criteria failed.", output)
            self.assertIn("Artifact: phases/demo-phase/step0-output.json", output)

    def test_returns_validator_errors_for_invalid_phase(self):
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_json(root / "phases" / "index.json", {"phases": []})

            stdout = StringIO()
            stderr = StringIO()
            with redirect_stdout(stdout), redirect_stderr(stderr):
                exit_code = report_phase.main(["missing-phase", "--root", str(root)])

            self.assertEqual(exit_code, 1)
            self.assertIn("ERROR: phase 'missing-phase' metadata is invalid", stderr.getvalue())
            self.assertIn("phases/index.json has no entry for phase 'missing-phase'", stderr.getvalue())
            self.assertIn("phase directory not found: phases/missing-phase", stderr.getvalue())


if __name__ == "__main__":
    unittest.main()
