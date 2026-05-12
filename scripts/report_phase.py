#!/usr/bin/env python3
"""
Report Codex harness phase status.

Usage:
    python3 scripts/report_phase.py <phase-name>
"""

import argparse
import json
import sys
from pathlib import Path
from typing import Any

import validate_phase

ROOT = Path(__file__).resolve().parent.parent
STATUS_ORDER = ("completed", "pending", "blocked", "error")


def report_phase(root: Path | str, phase_name: str) -> int:
    root_path = Path(root)
    validation = validate_phase.validate_phase(root_path, phase_name)
    if not validation.valid:
        print(f"ERROR: phase '{validation.phase_name}' metadata is invalid", file=sys.stderr)
        for error in validation.errors:
            print(f"- {error}", file=sys.stderr)
        return 1

    phases_dir = root_path / "phases"
    phase_dir = phases_dir / phase_name
    top_index = read_json(phases_dir / "index.json")
    phase_index = read_json(phase_dir / "index.json")
    steps = phase_index["steps"]

    print(f"\n{'=' * 60}")
    print("  Harness Phase Report")
    print(f"  Phase: {phase_name}")
    print(f"{'=' * 60}")
    print(f"Project: {phase_index.get('project', 'unknown')}")
    print(f"Phase status: {phase_status(top_index, phase_name)}")
    print(f"Steps: {format_counts(count_statuses(steps))}")

    next_step = next((step for step in steps if step.get("status") == "pending"), None)
    if next_step is None:
        print("Next pending step: none")
    else:
        print(f"Next pending step: {next_step['step']} ({next_step['name']})")

    latest_completed = next(
        (step for step in reversed(steps) if step.get("status") == "completed"),
        None,
    )
    if latest_completed is not None:
        print(
            "Latest completed: "
            f"Step {latest_completed['step']} ({latest_completed['name']}): "
            f"{latest_completed['summary']}"
        )

    for step in steps:
        if step.get("status") == "blocked":
            print(f"Blocked: Step {step['step']} ({step['name']}): {step['blocked_reason']}")
        elif step.get("status") == "error":
            print(f"Error: Step {step['step']} ({step['name']}): {step['error_message']}")

    artifacts = output_artifacts(phase_dir)
    if artifacts:
        print("\nArtifacts:")
        for artifact in artifacts:
            print(f"Artifact: {relative_path(root_path, artifact)}")

    return 0


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def phase_status(top_index: dict[str, Any], phase_name: str) -> str:
    for phase in top_index.get("phases", []):
        if isinstance(phase, dict) and phase.get("dir") == phase_name:
            return str(phase.get("status", "unknown"))
    return "unknown"


def count_statuses(steps: list[dict[str, Any]]) -> dict[str, int]:
    counts = {status: 0 for status in STATUS_ORDER}
    for step in steps:
        status = step.get("status")
        if status in counts:
            counts[status] += 1
    return counts


def format_counts(counts: dict[str, int]) -> str:
    return ", ".join(f"{counts[status]} {status}" for status in STATUS_ORDER)


def output_artifacts(phase_dir: Path) -> list[Path]:
    return sorted(
        [
            *phase_dir.glob("step*-output.json"),
            *phase_dir.glob("phase*-output.json"),
        ],
    )


def relative_path(root: Path, path: Path) -> str:
    try:
        return path.relative_to(root).as_posix()
    except ValueError:
        return path.as_posix()


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Report Codex harness phase status.")
    parser.add_argument("phase_name", help="Phase directory name, e.g. example-phase")
    parser.add_argument("--root", default=str(ROOT), help="Repository root. Defaults to this repo.")
    args = parser.parse_args(argv)

    return report_phase(Path(args.root), args.phase_name)


if __name__ == "__main__":
    raise SystemExit(main())
