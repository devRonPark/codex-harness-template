# Project: Codex Harness Template

## Purpose

This repository is a minimal Codex harness template. It provides a repeatable way to turn a product or engineering goal into phase files, run those steps through Codex, and preserve execution status in machine-readable metadata.

It intentionally does not include an application scaffold, package manager setup, framework dependency, API provider integration, or product-specific implementation.

## Core Files

- `.agents/skills/harness/SKILL.md`: planning and execution workflow for Codex harness work.
- `.agents/skills/review/SKILL.md`: review checklist for changes made through the harness.
- `.codex/config.toml`: enables Codex hooks.
- `.codex/hooks.json`: registers local hook commands.
- `.codex/hooks/run-profile.sh`: dispatches optional hook profiles for Codex hooks and pre-commit.
- `.codex/hooks/tdd-guard.sh`: optional TDD guard for implementation edits.
- `.githooks/pre-commit`: template-level validation hook.
- `scripts/create_phase.py`: phase scaffold generator.
- `scripts/validate_phase.py`: phase metadata validator.
- `scripts/report_phase.py`: phase status reporter.
- `scripts/execute.py`: phase executor that invokes `codex exec` for pending steps.
- `phases/index.json`: top-level list of planned phase directories.
- `docs/PRD.md`: product requirements template for the target project.
- `docs/ARCHITECTURE.md`: architecture template for the target project.
- `docs/ADR.md`: architecture decision record template.
- `docs/TEMPLATE_EVOLUTION.md`: roadmap for evolving this base harness into a personal harness.

## Harness Workflow

1. Define the target product or engineering objective in `docs/PRD.md`.
2. Define the architecture and boundaries in `docs/ARCHITECTURE.md`.
3. Capture important technical decisions in `docs/ADR.md`.
4. Add a phase entry to `phases/index.json`.
5. Create `phases/{phase-name}/index.json`.
6. Create self-contained `phases/{phase-name}/step{N}.md` files.
7. Run `python3 scripts/execute.py {phase-name}` when the plan is approved.

## Phase Rules

- Phase directory names use short kebab-case names.
- Step names use short kebab-case names.
- Step numbers start at `0`.
- Step files must be self-contained because each step can run in a fresh Codex execution.
- Each step must list the files to read before editing.
- Each step should list the files it expects to edit.
- Each step must include concrete acceptance criteria.
- Each completed step should record validation evidence or a concrete success observation.
- Each step must update its entry in `phases/{phase-name}/index.json`.

## Status Values

Allowed phase and step statuses:

- `pending`
- `completed`
- `error`
- `blocked`

Completed steps should include a one-line `summary` that helps later steps understand what changed.

Blocked steps should include `blocked_reason`.

Failed steps should include `error_message`.

## Development Rules

- Keep this template product-neutral.
- Do not add application code to the template root unless it is part of a deliberate example phase.
- Do not commit generated caches such as `__pycache__`, `node_modules`, build outputs, or analysis reports.
- Do not store secrets or local environment files.
- Prefer small, independently executable phase steps.
- Use project-specific validation commands in each step, not global template assumptions.
- Add harness capabilities incrementally and document why each one belongs in the base template.

## Template Evolution Policy

This template should grow by adding durable harness behavior, not by adding one-off project implementation.

Good additions:

- executor options that improve repeatability
- stronger phase metadata validation
- reusable planning/review skills
- portable hooks with clear opt-in behavior
- documentation that clarifies how to adapt the template

Avoid:

- framework-specific app code
- product-specific API integrations
- generated phase output
- dependency lockfiles unless the template intentionally becomes a packaged tool
- validation commands that assume a specific target stack

## Commands

Validate the template-level Python executor syntax:

```bash
python3 -m py_compile scripts/create_phase.py scripts/execute.py scripts/report_phase.py scripts/validate_phase.py
```

Validate a phase:

```bash
python3 scripts/validate_phase.py {phase-name}
```

Report a phase:

```bash
python3 scripts/report_phase.py {phase-name}
```

Run a phase:

```bash
python3 scripts/execute.py {phase-name}
```

Preview a phase without invoking Codex:

```bash
python3 scripts/execute.py {phase-name} --dry-run
```

Run a phase and push its branch:

```bash
python3 scripts/execute.py {phase-name} --push
```

Run stricter opt-in hook checks:

```bash
HARNESS_HOOK_PROFILE=strict .githooks/pre-commit
```
