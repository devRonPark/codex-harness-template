import json
import os
import subprocess
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RUN_PROFILE = ROOT / ".codex" / "hooks" / "run-profile.sh"


def implementation_edit_payload(path: str = "src/example.ts") -> str:
    return json.dumps(
        {
            "tool_input": {
                "command": "\n".join(
                    [
                        "*** Begin Patch",
                        f"*** Update File: {path}",
                        "@@",
                        "-old",
                        "+new",
                        "*** End Patch",
                    ],
                ),
            },
        },
    )


class HookProfileTests(unittest.TestCase):
    def run_codex_hook(self, profile: str, payload: str) -> subprocess.CompletedProcess:
        env = os.environ.copy()
        env["HARNESS_HOOK_PROFILE"] = profile
        return subprocess.run(
            ["bash", str(RUN_PROFILE), "codex-pre-tool-use"],
            cwd=ROOT,
            input=payload,
            text=True,
            capture_output=True,
            env=env,
        )

    def test_minimal_profile_allows_implementation_edits_without_tdd_test(self):
        result = self.run_codex_hook("minimal", implementation_edit_payload())

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout, "")

    def test_tdd_profile_runs_existing_tdd_guard(self):
        result = self.run_codex_hook("tdd", implementation_edit_payload())

        self.assertEqual(result.returncode, 0, result.stderr)
        response = json.loads(result.stdout)
        hook_output = response["hookSpecificOutput"]
        self.assertEqual(hook_output["hookEventName"], "PreToolUse")
        self.assertEqual(hook_output["permissionDecision"], "deny")
        self.assertIn("TDD GUARD", hook_output["permissionDecisionReason"])

    def test_unknown_profile_fails_before_running_pre_commit_checks(self):
        env = os.environ.copy()
        env["HARNESS_HOOK_PROFILE"] = "unknown-profile"

        result = subprocess.run(
            ["bash", str(RUN_PROFILE), "pre-commit"],
            cwd=ROOT,
            text=True,
            capture_output=True,
            env=env,
        )

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("unknown hook profile: unknown-profile", result.stderr)


if __name__ == "__main__":
    unittest.main()
