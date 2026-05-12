# Codex Harness Template Guide

This repository is a product-neutral Codex harness template. It contains the files needed to plan implementation work as phase steps and execute those steps through `codex exec`.

## What This Template Is For

Use this template when you want Codex to implement a project through explicit, reviewable step files instead of a single large prompt.

The template is useful for:

- breaking work into sequential phases
- preserving execution status in JSON
- giving each Codex run enough local context to work independently
- recording step summaries for later steps
- separating code commits from harness metadata commits

## Core Files

| Path | Purpose |
| --- | --- |
| `AGENTS.md` | Template-level operating rules and guardrails. |
| `.agents/skills/harness/SKILL.md` | Workflow for planning phase files and running the harness. |
| `.agents/skills/review/SKILL.md` | Review checklist for validating local changes. |
| `.codex/config.toml` | Enables Codex hooks. |
| `.codex/hooks.json` | Registers hook commands. |
| `.codex/hooks/run-profile.sh` | Dispatches optional hook profiles for Codex hooks and pre-commit. |
| `.codex/hooks/tdd-guard.sh` | Optional pre-edit guard for implementation files. |
| `.githooks/pre-commit` | Lightweight template validation hook. |
| `docs/PRD.md` | Product requirements template for the target project. |
| `docs/ARCHITECTURE.md` | Architecture template for the target project. |
| `docs/ADR.md` | Architecture decision record template. |
| `docs/NEXT_PROGRESS_PLAN.md` | Ordered harness evolution plan for preserving branch-to-branch context. |
| `docs/HARNESS_ADVANCEMENT_ROADMAP.md` | Research-backed roadmap for the next harness improvements. |
| `phases/index.json` | Top-level phase registry. |
| `scripts/create_phase.py` | Phase scaffold generator. |
| `scripts/validate_phase.py` | Phase metadata validator. |
| `scripts/report_phase.py` | Phase status reporter. |
| `scripts/execute.py` | Executor that runs pending phase steps through Codex. |

## Phase Registry

`phases/index.json` starts empty:

```json
{
  "phases": []
}
```

Add a phase when you are ready to plan work. You can edit the JSON manually, but the preferred path is:

```bash
python3 scripts/create_phase.py example-phase --steps project-setup,core-domain,final-review
```

The generated registry entry looks like this:

```json
{
  "phases": [
    {
      "dir": "example-phase",
      "status": "pending"
    }
  ]
}
```

Allowed statuses:

- `pending`
- `completed`
- `error`
- `blocked`

## Phase Detail File

`scripts/create_phase.py` creates `phases/{phase-name}/index.json`:

```json
{
  "project": "Project Name",
  "phase": "example-phase",
  "steps": [
    {
      "step": 0,
      "name": "project-setup",
      "status": "pending"
    },
    {
      "step": 1,
      "name": "core-domain",
      "status": "pending"
    }
  ]
}
```

Rules:

- `phase` must match the directory name.
- `step` values start at `0`.
- `name` values should be short kebab-case slugs.
- New steps start as `pending`.
- Do not add timestamps manually. `scripts/execute.py` records them.

Validate a phase before execution:

```bash
python3 scripts/validate_phase.py example-phase
```

The validator checks registry entries, phase naming, contiguous step numbers, required step prompt files, allowed statuses, and required status detail fields.

Preview a phase without invoking Codex:

```bash
python3 scripts/execute.py example-phase --dry-run
```

Dry-run mode reuses the phase validator, prints the target branch, next pending step, step prompt path, completed step summaries, and files the executor would read. It does not invoke Codex, checkout or create branches, write timestamps, or create output JSON.

Report phase status without opening JSON manually:

```bash
python3 scripts/report_phase.py example-phase
```

The report shows phase status, completed/pending/blocked/error counts, next pending step, latest completed summary, blocker/error details, and existing output artifact paths.

## Step Prompt Format

Each generated step lives at `phases/{phase-name}/step{N}.md`.

Recommended structure:

````markdown
# Step {N}: {step-name}

## Read First

- `/AGENTS.md`
- `/docs/PRD.md`
- `/docs/ARCHITECTURE.md`
- `/docs/ADR.md`
- {files created or changed by previous steps}

## Task

Describe the concrete implementation work. Include file paths, required interfaces, constraints, and expected behavior.

## Acceptance Criteria

```bash
{project-specific validation command}
```

## Verification

1. Run the acceptance criteria.
2. Check architecture and ADR compliance.
3. Update `phases/{phase-name}/index.json`:
   - success: `status: completed` plus `summary`
   - unrecoverable failure: `status: error` plus `error_message`
   - needs user input: `status: blocked` plus `blocked_reason`

## Do Not

- Add unrelated features. Reason: keep the step independently reviewable.
- Change files outside the step scope unless required by the acceptance criteria.
````

## Running A Phase

Initialize Git before executing a phase. The executor creates or checks out `feat-{phase-name}`.

Preview the next execution first:

```bash
python3 scripts/execute.py {phase-name} --dry-run
```

Check current phase status:

```bash
python3 scripts/report_phase.py {phase-name}
```

```bash
python3 scripts/execute.py {phase-name}
```

Push after completion:

```bash
python3 scripts/execute.py {phase-name} --push
```

## What The Executor Does

`scripts/execute.py`:

- supports `--dry-run` for read-only validation and execution preview
- checks for `phases/{phase-name}/index.json`
- creates or checks out `feat-{phase-name}`
- injects `AGENTS.md` and `docs/*.md` into each step prompt
- sends completed step summaries to later steps
- invokes `codex exec` for the next pending step
- stores raw step output as `phases/{phase-name}/step{N}-output.json`
- retries failed steps up to three times
- records timestamps
- commits code changes and harness metadata separately
- updates `phases/index.json` when the phase completes, errors, or blocks

## Template Validation

```bash
.githooks/pre-commit
```

## Hook Profiles

Hook profiles are opt-in wrappers around portable checks. The default profile is `minimal`, which keeps the base template behavior lightweight:

- Python syntax for harness scripts
- script unit tests
- JSON validity for repository JSON files

Select a profile for one command:

```bash
HARNESS_HOOK_PROFILE=phase-metadata .githooks/pre-commit
HARNESS_HOOK_PROFILE=strict .githooks/pre-commit
```

You can also set `CODEX_HOOK_PROFILE` for Codex-specific use, or put one profile name in `.codex/hook-profile.local` for a local default. `.codex/hook-profile.local` is intentionally ignored by git.

Available profiles:

| Profile | Behavior |
| --- | --- |
| `minimal` | Runs template validation only. This is the default. |
| `json-valid` | Alias for the default template validation, which includes JSON validation. |
| `phase-metadata` | Runs template validation and validates every phase registered in `phases/index.json`. |
| `no-secrets` | Runs template validation and scans tracked text files for obvious secret patterns. |
| `tdd` | Runs template validation; Codex pre-edit hooks also run `.codex/hooks/tdd-guard.sh`. |
| `strict` | Enables phase metadata validation, secret scan, and Codex pre-edit TDD guard. |

## Adapting The Template

For a new project:

1. Replace `docs/PRD.md`, `docs/ARCHITECTURE.md`, and `docs/ADR.md`.
2. Update `AGENTS.md` with project-specific rules.
3. Create a phase entry and step files.
4. Execute only after the phase plan is reviewed.

Keep this repository clean: do not add generated caches, dependency directories, build outputs, local reports, or secrets.

For the next improvement sequence, read `docs/HARNESS_ADVANCEMENT_ROADMAP.md`. It keeps the current baseline separate from future work such as review rubrics, richer step templates, run ledgers, executor configuration, schema validation, worktree isolation, and later parallel execution.
