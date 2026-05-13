# Codex Harness Template Guide

This guide explains how to use this repository as a product-neutral Codex harness and how to adapt it for a new project.

## What This Template Is For

Use this template when you want Codex to implement work through explicit phase files instead of one large prompt.

- Break work into sequential phases
- Preserve execution status in repository files
- Give each Codex run enough local context to work independently
- Record step summaries for later steps
- Separate code commits from harness metadata commits

Do not use the template as an application scaffold. It is a harness, not a starter app.

## Best Practices Borrowed From High-Star Harness READMEs

I sampled GitHub harness-engineering repositories sorted by `Most stars` and used the README patterns that showed up repeatedly in the strongest examples.

- [aden-hive/hive](https://github.com/aden-hive/hive) - about 10.3k stars. Strong front matter: a one-line thesis, a visible hero banner, a "who is it for" section, a "when should you use it" section, and quick links to docs and roadmap.
- [revfactory/harness](https://github.com/revfactory/harness) - about 3.3k stars. Strong structure: banner image, badge strip, one-sentence positioning, overview, category/layer explanation, key features, workflow, installation, plugin structure, and multilingual support.
- [ralfstrobel/agentic-brownfield-coding](https://github.com/ralfstrobel/agentic-brownfield-coding) - 17 stars. Strong onboarding: problem statement, background, system requirements, installation, usage, caution notes, FAQ, and further reading.

Patterns worth copying:

- Lead with a clear promise in the first screen.
- Add a visual element near the top if the project is a tool or workflow.
- Explain who the repo is for and when to use it.
- Put quick start commands before long explanations.
- Show the repository structure or workflow early.
- Separate installation, usage, validation, and extension notes.
- Link outward to deeper docs instead of overloading the README.

## Repository Shape

This template is intentionally small:

- `AGENTS.md` defines operating rules
- `docs/PRD.md`, `docs/ARCHITECTURE.md`, and `docs/ADR.md` define the target project
- `phases/index.json` tracks the phase registry
- `phases/{phase-name}/index.json` tracks step metadata
- `phases/{phase-name}/step{N}.md` holds self-contained step prompts
- `scripts/create_phase.py` creates scaffolds
- `scripts/validate_phase.py` validates metadata
- `scripts/report_phase.py` summarizes phase state
- `scripts/execute.py` runs pending steps through Codex

## Core Workflow

1. Define the target project in `docs/PRD.md`.
2. Define architecture and boundaries in `docs/ARCHITECTURE.md`.
3. Record durable decisions in `docs/ADR.md`.
4. Create a phase entry in `phases/index.json`.
5. Generate a phase scaffold with `scripts/create_phase.py`.
6. Fill in each generated step file.
7. Validate the phase with `scripts/validate_phase.py`.
8. Preview with `scripts/execute.py --dry-run`.
9. Run the phase with `scripts/execute.py`.

## How To Write A Step

Each step should be self-contained.

Include these sections:

- `Read First`
- `Files To Edit`
- `Task`
- `Expected Output`
- `Acceptance Criteria`
- `Evidence`
- `Decision Notes`
- `Recovery`
- `Verification`
- `Do Not`

Good step writing habits:

- Keep one step small enough for one Codex execution.
- List the exact files to read before editing.
- List the files the step is expected to modify.
- Use executable acceptance criteria, not vague success language.
- Require evidence from the validation command or a concrete success observation.
- Write specific "Do not" warnings when a mistake would be costly.

## Validation Commands

Use project-specific validation commands in each phase step.

Base template checks:

```bash
.githooks/pre-commit
```

Template script syntax:

```bash
python3 -m py_compile scripts/create_phase.py scripts/execute.py scripts/report_phase.py scripts/validate_phase.py
```

Common phase checks:

```bash
python3 scripts/validate_phase.py {phase-name}
python3 scripts/execute.py {phase-name} --dry-run
python3 scripts/report_phase.py {phase-name}
python3 scripts/execute.py {phase-name}
```

## README Structure That Works Well

The strongest harness READMEs I sampled follow a similar shape:

- a clear title and visual hero
- a one-line positioning statement
- a short explanation of what it gives you
- quick start commands
- a compact repository map
- explicit validation and execution notes
- links to deeper docs

This repository follows that pattern. The README stays short; this guide carries the details.

## Adapting The Template For A New Project

1. Replace the placeholder project docs in `docs/`.
2. Generate a phase scaffold for the first deliverable.
3. Keep phase steps focused on a single visible outcome.
4. Use `docs/HARNESS_ADVANCEMENT_ROADMAP.md` as the long-term improvement map.
5. Use `docs/NEXT_PROGRESS_PLAN.md` to preserve branch-to-branch handoff context.

## Operational Notes

- Keep the worktree clean before running `scripts/execute.py`.
- Do not commit generated caches, local reports, or raw step output artifacts.
- Treat `stepN-output.json` as a local artifact, not durable history.
- Use hook profiles when you need stricter local checks without changing the base template.

## Where To Go Next

- [README](../README.md)
- [Harness Template Summary](HARNESS_TEMPLATE_SUMMARY.md)
- [Template Evolution Roadmap](TEMPLATE_EVOLUTION.md)
- [Harness Advancement Roadmap](HARNESS_ADVANCEMENT_ROADMAP.md)
