---
name: harness
description: "Use when working with this Codex Harness Template, creating or reviewing phase/step plans, editing phases/* files, or running scripts/execute.py."
---

# Harness Workflow

This repository is a Codex harness template. Use it to turn project work into explicit phase files and execute those steps through Codex.

## A. Explore

Before proposing or writing phase steps, read the project contract files:

- `AGENTS.md`
- `docs/PRD.md`
- `docs/ARCHITECTURE.md`
- `docs/ADR.md`

If these files still contain placeholder content, ask the user for the missing product or architecture details before creating implementation steps.

Use sub-agents only when the user explicitly asks for delegated or parallel agent work.

## B. Discuss

If product scope, architecture, validation commands, or execution order is unclear, present the concrete decision points before writing phase files.

## C. Design Steps

When the user asks for an implementation plan, draft the phase steps first and request feedback before writing files.

Step design rules:

1. Keep each step small enough for one Codex execution.
2. Make each step self-contained; do not rely on prior chat context.
3. List the exact files the execution agent must read first.
4. Specify interfaces, file paths, and constraints; avoid over-prescribing implementation details unless correctness requires it.
5. Use executable acceptance criteria, such as project-specific test/build commands.
6. Write specific warnings in the form "Do not do X. Reason: Y."
7. Use short kebab-case step names.

## D. Create Files

After approval, create or update these files.

### `phases/index.json`

Top-level phase registry:

```json
{
  "phases": [
    {
      "dir": "0-mvp",
      "status": "pending"
    }
  ]
}
```

Rules:

- `dir` is the phase directory name.
- `status` is one of `pending`, `completed`, `error`, or `blocked`.
- Do not add timestamps manually. `scripts/execute.py` records them during execution.

### `phases/{phase-name}/index.json`

Phase detail file:

```json
{
  "project": "<project-name>",
  "phase": "<phase-name>",
  "steps": [
    { "step": 0, "name": "project-setup", "status": "pending" },
    { "step": 1, "name": "core-types", "status": "pending" }
  ]
}
```

Rules:

- `project` should match the project name in `AGENTS.md`.
- `phase` must match the directory name.
- `steps[].step` starts at `0`.
- `steps[].name` is a short kebab-case slug.
- New steps start as `pending`.

Status fields:

| Status | Extra field | Owner |
| --- | --- | --- |
| `completed` | `summary` | Codex session writes the summary; executor writes timestamp. |
| `error` | `error_message` | Codex session writes the message; executor writes timestamp. |
| `blocked` | `blocked_reason` | Codex session writes the reason; executor writes timestamp. |

### `phases/{phase-name}/step{N}.md`

Recommended step prompt:

````markdown
# Step {N}: {name}

## Read First

- `/AGENTS.md`
- `/docs/PRD.md`
- `/docs/ARCHITECTURE.md`
- `/docs/ADR.md`
- {previous-step files if relevant}

## Task

{Concrete implementation instructions. Include file paths, required interfaces, behavioral constraints, and project boundaries.}

## Acceptance Criteria

```bash
{project-specific validation command}
```

## Verification

1. Run the acceptance criteria.
2. Check that the change follows `ARCHITECTURE.md`, `ADR.md`, and `AGENTS.md`.
3. Update `phases/{phase-name}/index.json`:
   - Success: set `status` to `completed` and add `summary`.
   - Failed after reasonable retries: set `status` to `error` and add `error_message`.
   - Needs user input: set `status` to `blocked` and add `blocked_reason`.

## Do Not

- {Specific forbidden action. Reason: specific risk.}
````

## E. Execute

Only execute a phase when the user asks for execution.

```bash
python3 scripts/execute.py {phase-name}
python3 scripts/execute.py {phase-name} --push
```

`scripts/execute.py`:

- creates or checks out `feat-{phase-name}`
- injects `AGENTS.md` and `docs/*.md` into the prompt
- passes completed step summaries to later steps
- retries failed steps up to three times
- records timestamps
- commits implementation changes and harness metadata separately

Recovery:

- For an `error` step, fix the cause, reset the step to `pending`, remove `error_message`, and rerun.
- For a `blocked` step, resolve the blocker, reset the step to `pending`, remove `blocked_reason`, and rerun.
