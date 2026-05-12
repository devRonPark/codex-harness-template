# Template Evolution Roadmap

This document is the working map for turning this Codex-only base harness into a personal harness over time.

## Current Baseline

The current template is intentionally small:

- Codex-only execution through `scripts/execute.py`
- phase registry in `phases/index.json`
- phase scaffold generation through `scripts/create_phase.py`
- phase metadata validation through `scripts/validate_phase.py`
- read-only executor dry-run through `scripts/execute.py --dry-run`
- phase status reporting through `scripts/report_phase.py`
- optional hook profiles through `.codex/hooks/run-profile.sh`
- self-contained step prompts in `phases/{phase-name}/step{N}.md`
- project contract templates in `docs/`
- Codex skill files in `.agents/skills/`
- optional TDD guard hook
- lightweight pre-commit validation for Python syntax and JSON validity

This is the right base because it has no application framework, no npm dependency, no product API code, and no completed demo phase.

## Design Principles

1. Keep the base product-neutral.
2. Prefer explicit files over hidden behavior.
3. Keep every phase step executable in a fresh Codex session.
4. Add automation only when it removes repeated manual work.
5. Keep hooks portable and easy to disable.
6. Record durable decisions in `docs/ADR.md`.
7. Do not add project code to the base template.

## Extension Points

Use these locations for future customization:

| Area | Path | What To Add |
| --- | --- | --- |
| Planning workflow | `.agents/skills/harness/SKILL.md` | Step design rules, phase conventions, execution policy. |
| Review workflow | `.agents/skills/review/SKILL.md` | Review checklist, metadata checks, project guardrails. |
| Executor behavior | `scripts/execute.py` | CLI flags, dry-run mode, validation, logging, resume behavior. |
| Hooks | `.codex/hooks.json`, `.codex/hooks/` | Opt-in guardrails before edits or commands. |
| Contract templates | `docs/PRD.md`, `docs/ARCHITECTURE.md`, `docs/ADR.md` | Better prompts for project definition. |
| Phase metadata | `phases/index.json` and per-phase `index.json` | Extra fields that help execution or reporting. |

## Recommended Evolution Order

### 1. Add A Phase Scaffolder

Goal: create a command that generates `phases/{phase-name}/index.json` and starter `step{N}.md` files from a small spec.

Why first: phase creation is repetitive, and scaffolding can stay product-neutral.

Status: implemented in `scripts/create_phase.py`.

Possible command:

```bash
python3 scripts/create_phase.py example-phase --steps project-setup,core-domain,final-review
```

### 2. Add Metadata Validation

Goal: validate phase files before execution.

Status: implemented in `scripts/validate_phase.py`.

Checks:

- `phases/index.json` includes the phase.
- each phase has an `index.json`
- step numbers are contiguous from `0`
- each `step{N}.md` exists
- statuses are valid
- completed steps include `summary`
- blocked/error steps include the right reason field

### 3. Add Executor Dry Run

Goal: inspect what would run without invoking Codex.

Status: implemented in `scripts/execute.py --dry-run`.

Command:

```bash
python3 scripts/execute.py example-phase --dry-run
```

Dry run prints:

- target branch
- next pending step
- files that will be read
- validation result
- completed previous step summaries
- Codex execution preview

Dry run does not invoke Codex, checkout or create branches, write timestamps, or create output JSON.

### 4. Add Execution Report

Goal: summarize phase state without reading JSON manually.

Status: implemented in `scripts/report_phase.py`.

Command:

```bash
python3 scripts/report_phase.py example-phase
```

Output:

- completed / pending / blocked / error counts
- latest completed step summary
- next pending step
- blocked reason or error message when present
- existing raw output artifact paths

### 5. Add Optional Hook Profiles

Goal: keep hooks portable while allowing stricter local workflows.

Status: implemented in `.codex/hooks/run-profile.sh`.

Examples:

- `tdd`
- `json-valid`
- `no-secrets`
- `phase-metadata`

Avoid hard-coding framework-specific commands like `npm run lint` in the base template.

Implemented profiles:

- `minimal`: template validation only; this is the default.
- `json-valid`: alias for default template validation, which already includes JSON checks.
- `phase-metadata`: default validation plus every registered phase through `scripts/validate_phase.py`.
- `no-secrets`: default validation plus a lightweight tracked-file secret scan.
- `tdd`: default validation plus Codex pre-edit TDD guard.
- `strict`: phase metadata, no-secrets, and Codex pre-edit TDD guard.

Selection order:

1. `HARNESS_HOOK_PROFILE`
2. `CODEX_HOOK_PROFILE`
3. `.codex/hook-profile.local`
4. `minimal`

### 6. Add Personal Review Rubric

Goal: make `.agents/skills/review/SKILL.md` reflect how you personally want Codex work reviewed.

Good additions:

- severity rubric
- required final checklist
- phase metadata checks
- rules for when to run validation

## Post-Baseline Roadmap

The first six items above form the initial baseline for a product-neutral harness. The next roadmap is tracked in `docs/HARNESS_ADVANCEMENT_ROADMAP.md`.

Recommended next sequence:

1. personal review rubric
2. step template v2
3. phase run ledger
4. executor configuration
5. phase metadata schema
6. worktree isolation
7. dependency-aware parallel execution
8. portable packaging

The roadmap is intentionally ordered from safer sequential workflow improvements toward later parallel execution. Do not start with orchestration or packaging before the review, step, and run-history surfaces are stronger.

## Backlog

- `--max-retries` override for `scripts/execute.py`
- configurable sandbox and approval policy
- optional JSON schema for phase metadata
- example phase stored as documentation, not active phase output

## Keep Out Of The Base

Do not add these unless the template deliberately changes scope:

- Next.js, React, Vite, or other app scaffold
- npm lockfiles
- provider-specific API scripts
- completed product phases
- generated step output JSON
- local reports
- secrets or `.env.local`
- one project's source code

## Decision Log

Use `docs/ADR.md` when a customization becomes part of the base template. Examples:

- choosing whether hooks are opt-in or always-on
- choosing phase metadata schema
- changing executor sandbox defaults
- adding a scaffolding script
- requiring a validation command before execution
