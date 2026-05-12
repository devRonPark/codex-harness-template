#!/usr/bin/env python3
"""
Validate Codex harness phase metadata.

Usage:
    python3 scripts/validate_phase.py <phase-name>
"""

import argparse
import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
NAME_PATTERN = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
VALID_STATUSES = {"pending", "completed", "error", "blocked"}
STATUS_LABEL = ", ".join(sorted(VALID_STATUSES))


@dataclass(frozen=True)
class ValidationResult:
    phase_name: str
    errors: list[str]

    @property
    def valid(self) -> bool:
        return not self.errors


def validate_phase(root: Path | str, phase_name: str) -> ValidationResult:
    root_path = Path(root)
    errors: list[str] = []

    if not NAME_PATTERN.fullmatch(phase_name):
        errors.append(f"phase name must use lowercase kebab-case: {phase_name!r}")
        return ValidationResult(phase_name=phase_name, errors=errors)

    phases_dir = root_path / "phases"
    top_index_file = phases_dir / "index.json"
    phase_dir = phases_dir / phase_name
    phase_index_file = phase_dir / "index.json"

    top_index = read_json(root_path, top_index_file, errors)
    if top_index is not None:
        validate_top_index(root_path, top_index_file, top_index, phase_name, errors)

    if not phase_dir.is_dir():
        errors.append(f"phase directory not found: {relative_path(root_path, phase_dir)}")
        return ValidationResult(phase_name=phase_name, errors=errors)

    phase_index = read_json(root_path, phase_index_file, errors)
    if phase_index is not None:
        validate_phase_index(root_path, phase_index_file, phase_index, phase_name, errors)

    return ValidationResult(phase_name=phase_name, errors=errors)


def read_json(root: Path, path: Path, errors: list[str]) -> dict[str, Any] | None:
    rel = relative_path(root, path)
    if not path.exists():
        errors.append(f"missing file: {rel}")
        return None

    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        errors.append(f"invalid JSON in {rel}: {exc.msg} at line {exc.lineno}, column {exc.colno}")
        return None

    if not isinstance(data, dict):
        errors.append(f"{rel} must contain a JSON object")
        return None

    return data


def validate_top_index(
    root: Path,
    path: Path,
    data: dict[str, Any],
    phase_name: str,
    errors: list[str],
) -> None:
    rel = relative_path(root, path)
    phases = data.get("phases")
    if not isinstance(phases, list):
        errors.append(f"{rel} must contain a phases list")
        return

    matching_entries = []
    for index, entry in enumerate(phases):
        if not isinstance(entry, dict):
            errors.append(f"{rel} phases[{index}] must be an object")
            continue
        if entry.get("dir") == phase_name:
            matching_entries.append(entry)

    if not matching_entries:
        errors.append(f"{rel} has no entry for phase '{phase_name}'")
        return

    if len(matching_entries) > 1:
        errors.append(f"{rel} has duplicate entries for phase '{phase_name}'")

    for entry in matching_entries:
        status = entry.get("status")
        if status not in VALID_STATUSES:
            errors.append(f"{rel} phase '{phase_name}' status must be one of: {STATUS_LABEL}")


def validate_phase_index(
    root: Path,
    path: Path,
    data: dict[str, Any],
    phase_name: str,
    errors: list[str],
) -> None:
    rel = relative_path(root, path)
    phase = data.get("phase")
    if phase != phase_name:
        errors.append(f"{rel} phase field must be '{phase_name}', got {phase!r}")

    steps = data.get("steps")
    if not isinstance(steps, list):
        errors.append(f"{rel} must contain a steps list")
        return

    if not steps:
        errors.append(f"{rel} must contain at least one step")
        return

    step_numbers = [step.get("step") if isinstance(step, dict) else None for step in steps]
    expected_numbers = list(range(len(steps)))
    if step_numbers != expected_numbers:
        errors.append(f"{rel} steps must be numbered 0..{len(steps) - 1}")

    for expected_num in expected_numbers:
        step_file = path.parent / f"step{expected_num}.md"
        if not step_file.exists():
            errors.append(f"missing step file: {relative_path(root, step_file)}")

    for index, step in enumerate(steps):
        if not isinstance(step, dict):
            errors.append(f"{rel} steps[{index}] must be an object")
            continue
        validate_step(step, index, errors)


def validate_step(
    step: dict[str, Any],
    fallback_index: int,
    errors: list[str],
) -> None:
    step_num = step.get("step")
    label = f"step {step_num}" if isinstance(step_num, int) else f"steps[{fallback_index}]"

    if not isinstance(step_num, int):
        errors.append(f"{label} step field must be an integer")

    name = step.get("name")
    if not isinstance(name, str) or not NAME_PATTERN.fullmatch(name):
        errors.append(f"{label} name must use lowercase kebab-case")

    status = step.get("status")
    if status not in VALID_STATUSES:
        errors.append(f"{label} status must be one of: {STATUS_LABEL}")
    elif status == "completed" and not has_non_empty_string(step, "summary"):
        errors.append(f"{label} completed status requires non-empty summary")
    elif status == "blocked" and not has_non_empty_string(step, "blocked_reason"):
        errors.append(f"{label} blocked status requires non-empty blocked_reason")
    elif status == "error" and not has_non_empty_string(step, "error_message"):
        errors.append(f"{label} error status requires non-empty error_message")


def has_non_empty_string(data: dict[str, Any], key: str) -> bool:
    value = data.get(key)
    return isinstance(value, str) and bool(value.strip())


def relative_path(root: Path, path: Path) -> str:
    try:
        return path.relative_to(root).as_posix()
    except ValueError:
        return path.as_posix()


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Validate Codex harness phase metadata.")
    parser.add_argument("phase_name", help="Phase directory name, e.g. example-phase")
    parser.add_argument("--root", default=str(ROOT), help="Repository root. Defaults to this repo.")
    args = parser.parse_args(argv)

    result = validate_phase(Path(args.root), args.phase_name)
    if result.valid:
        print(f"OK: phase '{result.phase_name}' metadata is valid")
        return 0

    print(f"ERROR: phase '{result.phase_name}' metadata is invalid", file=sys.stderr)
    for error in result.errors:
        print(f"- {error}", file=sys.stderr)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
