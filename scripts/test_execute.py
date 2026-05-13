import json
import sys
import unittest
from contextlib import redirect_stderr, redirect_stdout
from io import StringIO
from pathlib import Path
from tempfile import TemporaryDirectory

sys.path.insert(0, str(Path(__file__).parent))

import execute


def write_json(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(f"{json.dumps(data, indent=2)}\n", encoding="utf-8")


def init_git_repo(root: Path) -> None:
    execute.subprocess.run(["git", "init"], cwd=root, check=True, capture_output=True, text=True)
    execute.subprocess.run(["git", "config", "user.email", "test@example.invalid"], cwd=root, check=True)
    execute.subprocess.run(["git", "config", "user.name", "Harness Test"], cwd=root, check=True)


def commit_all(root: Path, message: str = "initial commit") -> None:
    execute.subprocess.run(["git", "add", "."], cwd=root, check=True)
    execute.subprocess.run(["git", "commit", "-m", message], cwd=root, check=True, capture_output=True, text=True)


def write_minimal_phase(root: Path, phase_name: str = "demo-phase") -> None:
    (root / "AGENTS.md").write_text("# Project: Demo Harness\n", encoding="utf-8")
    (root / "docs").mkdir()
    (root / "docs" / "PRD.md").write_text("# PRD\n", encoding="utf-8")
    write_json(
        root / "phases" / "index.json",
        {"phases": [{"dir": phase_name, "status": "pending"}]},
    )
    write_json(
        root / "phases" / phase_name / "index.json",
        {
            "project": "Demo Harness",
            "phase": phase_name,
            "steps": [{"step": 0, "name": "first-step", "status": "pending"}],
        },
    )
    (root / "phases" / phase_name / "step0.md").write_text("# Step 0\n", encoding="utf-8")


class ExecuteDryRunTests(unittest.TestCase):
    def test_dry_run_reports_next_pending_step_without_writing_files(self):
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "AGENTS.md").write_text("# Project: Demo Harness\n", encoding="utf-8")
            (root / "docs").mkdir()
            (root / "docs" / "PRD.md").write_text("# PRD\n", encoding="utf-8")
            write_json(
                root / "phases" / "index.json",
                {"phases": [{"dir": "demo-phase", "status": "pending"}]},
            )
            phase_index = root / "phases" / "demo-phase" / "index.json"
            write_json(
                phase_index,
                {
                    "project": "Demo Harness",
                    "phase": "demo-phase",
                    "steps": [
                        {
                            "step": 0,
                            "name": "first-step",
                            "status": "completed",
                            "summary": "Created the first piece.",
                        },
                        {"step": 1, "name": "second-step", "status": "pending"},
                    ],
                },
            )
            (root / "phases" / "demo-phase" / "step0.md").write_text("# Step 0\n", encoding="utf-8")
            (root / "phases" / "demo-phase" / "step1.md").write_text("# Step 1\n", encoding="utf-8")
            before = phase_index.read_text(encoding="utf-8")

            stdout = StringIO()
            with redirect_stdout(stdout):
                exit_code = execute.main(["demo-phase", "--dry-run", "--root", str(root)])

            output = stdout.getvalue()
            self.assertEqual(exit_code, 0)
            self.assertIn("Validation: OK", output)
            self.assertIn("Target branch: feat-demo-phase", output)
            self.assertIn("Next pending step: 1 (second-step)", output)
            self.assertIn("Step prompt: phases/demo-phase/step1.md", output)
            self.assertIn("Step 0 (first-step): Created the first piece.", output)
            self.assertIn("Codex will not be invoked.", output)
            self.assertEqual(phase_index.read_text(encoding="utf-8"), before)
            self.assertFalse((root / "phases" / "demo-phase" / "step1-output.json").exists())

    def test_dry_run_returns_validation_errors_without_constructing_executor(self):
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_json(root / "phases" / "index.json", {"phases": []})

            stdout = StringIO()
            stderr = StringIO()
            with redirect_stdout(stdout), redirect_stderr(stderr):
                exit_code = execute.main(["missing-phase", "--dry-run", "--root", str(root)])

            self.assertEqual(exit_code, 1)
            self.assertIn("Validation: ERROR", stdout.getvalue())
            self.assertIn("phases/index.json has no entry for phase 'missing-phase'", stderr.getvalue())
            self.assertIn("phase directory not found: phases/missing-phase", stderr.getvalue())


class ExecuteWorktreeSafetyTests(unittest.TestCase):
    def test_executor_refuses_dirty_worktree_before_running_steps(self):
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_minimal_phase(root)
            init_git_repo(root)
            commit_all(root)
            (root / ".claude").mkdir()
            (root / ".claude" / "plan-progress.md").write_text("local only\n", encoding="utf-8")

            stdout = StringIO()
            executor = execute.StepExecutor("demo-phase", root=root)

            with redirect_stdout(stdout), self.assertRaises(SystemExit) as raised:
                executor.run()

            self.assertEqual(raised.exception.code, 3)
            output = stdout.getvalue()
            self.assertIn("ERROR: worktree is not clean", output)
            self.assertIn("?? .claude/plan-progress.md", output)


if __name__ == "__main__":
    unittest.main()
