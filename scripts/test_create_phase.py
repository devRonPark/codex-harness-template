import json
import sys
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

sys.path.insert(0, str(Path(__file__).parent))

import create_phase


class CreatePhaseTests(unittest.TestCase):
    def test_creates_phase_registry_index_and_step_files(self):
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "AGENTS.md").write_text("# Project: Demo Harness\n", encoding="utf-8")
            phases_dir = root / "phases"
            phases_dir.mkdir()
            (phases_dir / "index.json").write_text('{"phases": []}\n', encoding="utf-8")

            result = create_phase.create_phase(
                root,
                "add-auth",
                ["project-setup", "api-layer"],
            )

            self.assertEqual(result.phase_dir, phases_dir / "add-auth")

            top_index = json.loads((phases_dir / "index.json").read_text(encoding="utf-8"))
            self.assertEqual(top_index["phases"], [{"dir": "add-auth", "status": "pending"}])

            phase_index = json.loads(
                (phases_dir / "add-auth" / "index.json").read_text(encoding="utf-8"),
            )
            self.assertEqual(phase_index["project"], "Demo Harness")
            self.assertEqual(phase_index["phase"], "add-auth")
            self.assertEqual(
                phase_index["steps"],
                [
                    {"step": 0, "name": "project-setup", "status": "pending"},
                    {"step": 1, "name": "api-layer", "status": "pending"},
                ],
            )

            step0 = (phases_dir / "add-auth" / "step0.md").read_text(encoding="utf-8")
            self.assertIn("# Step 0: project-setup", step0)
            self.assertIn("- `/AGENTS.md`", step0)
            self.assertIn("phases/add-auth/index.json", step0)

            step1 = (phases_dir / "add-auth" / "step1.md").read_text(encoding="utf-8")
            self.assertIn("# Step 1: api-layer", step1)

    def test_appends_phase_without_removing_existing_registry_entries(self):
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            phases_dir = root / "phases"
            phases_dir.mkdir()
            (phases_dir / "index.json").write_text(
                json.dumps(
                    {"phases": [{"dir": "existing-phase", "status": "completed"}]},
                    indent=2,
                ),
                encoding="utf-8",
            )

            create_phase.create_phase(root, "next-phase", ["first-step"], project="Manual Project")

            top_index = json.loads((phases_dir / "index.json").read_text(encoding="utf-8"))
            self.assertEqual(
                top_index["phases"],
                [
                    {"dir": "existing-phase", "status": "completed"},
                    {"dir": "next-phase", "status": "pending"},
                ],
            )

    def test_step_template_includes_v2_execution_context_sections(self):
        template = create_phase.step_template("add-auth", 0, "project-setup")

        expected_sections = [
            "## Read First",
            "## Files To Edit",
            "## Task",
            "## Expected Output",
            "## Acceptance Criteria",
            "## Evidence",
            "## Decision Notes",
            "## Recovery",
            "## Verification",
            "## Do Not",
        ]

        last_index = -1
        for section in expected_sections:
            current_index = template.find(section)
            self.assertNotEqual(current_index, -1, f"missing section: {section}")
            self.assertGreater(current_index, last_index, f"section out of order: {section}")
            last_index = current_index

        self.assertIn("List the files this step is expected to modify.", template)
        self.assertIn("Record the exact validation command output or success observation.", template)
        self.assertIn("If this step fails", template)

    def test_rejects_invalid_phase_and_step_names(self):
        with TemporaryDirectory() as tmp:
            root = Path(tmp)

            with self.assertRaisesRegex(create_phase.CreatePhaseError, "phase name"):
                create_phase.create_phase(root, "../bad", ["first-step"])

            with self.assertRaisesRegex(create_phase.CreatePhaseError, "step name"):
                create_phase.create_phase(root, "valid-phase", ["Bad Step"])

    def test_rejects_existing_phase_directory(self):
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            phase_dir = root / "phases" / "existing-phase"
            phase_dir.mkdir(parents=True)

            with self.assertRaisesRegex(create_phase.CreatePhaseError, "already exists"):
                create_phase.create_phase(root, "existing-phase", ["first-step"])

    def test_parse_steps_accepts_comma_separated_values(self):
        self.assertEqual(
            create_phase.parse_steps("project-setup, api-layer,final-review"),
            ["project-setup", "api-layer", "final-review"],
        )


if __name__ == "__main__":
    unittest.main()
