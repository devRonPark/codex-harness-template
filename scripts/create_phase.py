#!/usr/bin/env python3
"""
Create a Codex harness phase scaffold.

Usage:
    python3 scripts/create_phase.py <phase-name> --steps step-one,step-two
"""

import argparse
import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

ROOT = Path(__file__).resolve().parent.parent
NAME_PATTERN = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")


class CreatePhaseError(Exception):
    """Raised when a phase scaffold cannot be created safely."""


@dataclass(frozen=True)
class CreatePhaseResult:
    phase_dir: Path
    phase_index: Path
    step_files: list[Path]


def parse_steps(raw_steps: str) -> list[str]:
    return [step.strip() for step in raw_steps.split(",") if step.strip()]


def create_phase(
    root: Path | str,
    phase_name: str,
    steps: Iterable[str],
    *,
    project: str | None = None,
) -> CreatePhaseResult:
    root_path = Path(root)
    step_names = list(steps)

    validate_name(phase_name, "phase name")
    if not step_names:
        raise CreatePhaseError("at least one step name is required")

    for step_name in step_names:
        validate_name(step_name, "step name")

    phases_dir = root_path / "phases"
    phase_dir = phases_dir / phase_name
    top_index_file = phases_dir / "index.json"

    if phase_dir.exists():
        raise CreatePhaseError(f"phase directory already exists: {phase_dir}")

    phases_dir.mkdir(parents=True, exist_ok=True)
    top_index = read_top_index(top_index_file)

    if any(phase.get("dir") == phase_name for phase in top_index["phases"]):
        raise CreatePhaseError(f"phase already exists in phases/index.json: {phase_name}")

    phase_dir.mkdir()
    phase_index = phase_dir / "index.json"
    step_files = []

    phase_data = {
        "project": project or infer_project_name(root_path),
        "phase": phase_name,
        "steps": [
            {
                "step": index,
                "name": step_name,
                "status": "pending",
            }
            for index, step_name in enumerate(step_names)
        ],
    }

    write_json(phase_index, phase_data)

    for index, step_name in enumerate(step_names):
        step_file = phase_dir / f"step{index}.md"
        step_file.write_text(step_template(phase_name, index, step_name), encoding="utf-8")
        step_files.append(step_file)

    top_index["phases"].append(
        {
            "dir": phase_name,
            "status": "pending",
        },
    )
    write_json(top_index_file, top_index)

    return CreatePhaseResult(
        phase_dir=phase_dir,
        phase_index=phase_index,
        step_files=step_files,
    )


def validate_name(value: str, label: str) -> None:
    if not NAME_PATTERN.fullmatch(value):
        raise CreatePhaseError(
            f"invalid {label}: {value!r}. Use lowercase kebab-case, e.g. example-phase.",
        )


def read_top_index(path: Path) -> dict:
    if not path.exists():
        return {"phases": []}

    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise CreatePhaseError(f"invalid JSON in {path}: {exc}") from exc

    phases = data.get("phases")
    if not isinstance(phases, list):
        raise CreatePhaseError(f"{path} must contain a phases list")

    return data


def write_json(path: Path, data: dict) -> None:
    path.write_text(f"{json.dumps(data, indent=2, ensure_ascii=False)}\n", encoding="utf-8")


def infer_project_name(root: Path) -> str:
    agents_md = root / "AGENTS.md"
    if not agents_md.exists():
        return "Project"

    for line in agents_md.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if not stripped.startswith("# "):
            continue

        title = stripped.removeprefix("# ").strip()
        if title.lower().startswith("project:"):
            return title.split(":", 1)[1].strip() or "Project"
        return title

    return "Project"


def step_template(phase_name: str, step_num: int, step_name: str) -> str:
    return f"""# Step {step_num}: {step_name}

## Read First

- `/AGENTS.md`
- `/docs/PRD.md`
- `/docs/ARCHITECTURE.md`
- `/docs/ADR.md`
- `/phases/{phase_name}/index.json`

## Files To Edit

- List the files this step is expected to modify.
- Add generated files, metadata files, or docs that must change for this step.

## Task

Describe the concrete implementation work. Include required file paths, interfaces,
behavioral constraints, and project boundaries.

## Expected Output

Describe the repository state, command output, user-facing behavior, or artifact
that should exist when this step is complete.

## Acceptance Criteria

```bash
# Replace with exact project-specific validation commands.
TBD
```

## Evidence

Record the exact validation command output or success observation. Include enough
detail for a later agent to verify what passed without rerunning everything.

## Decision Notes

- Record important implementation decisions or discoveries that later steps need.
- Leave as `N/A` if no decision context is needed.

## Recovery

If this step fails, preserve the failure context in `phases/{phase_name}/index.json`
and keep changes scoped so the step can be retried from a clean state.

## Verification

1. Run the acceptance criteria.
2. Record evidence from the validation command or success observation.
3. Check that the change follows `ARCHITECTURE.md`, `ADR.md`, and `AGENTS.md`.
4. Update `phases/{phase_name}/index.json`:
   - Success: set this step to `completed` and add `summary`.
   - Failed after reasonable retries: set this step to `error` and add `error_message`.
   - Needs user input: set this step to `blocked` and add `blocked_reason`.

## Do Not

- Add unrelated features. Reason: keep this step independently reviewable.
- Change files outside this step scope unless required by the acceptance criteria.
"""


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Create a Codex harness phase scaffold.")
    parser.add_argument("phase_name", help="Phase directory name, e.g. example-phase")
    parser.add_argument("--steps", required=True, help="Comma-separated kebab-case step names")
    parser.add_argument("--project", help="Project name override")
    parser.add_argument("--root", default=str(ROOT), help="Repository root. Defaults to this repo.")
    args = parser.parse_args(argv)

    try:
        result = create_phase(
            Path(args.root),
            args.phase_name,
            parse_steps(args.steps),
            project=args.project,
        )
    except CreatePhaseError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1

    print(f"Created phase: {result.phase_dir}")
    print(f"Created index: {result.phase_index}")
    for step_file in result.step_files:
        print(f"Created step: {step_file}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
