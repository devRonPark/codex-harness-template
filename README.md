# Codex Harness Template

![Codex Harness Template hero](assets/readme-hero.png)

Minimal base for structured Codex implementation work: define the goal, split it into phase files, validate the metadata, preview the run, and execute each step with durable status tracking.

This repository contains only the harness pieces. It does not include an application scaffold, package manager setup, framework dependency, provider integration, or a completed demo app.

## What This Gives You

- Phase scaffolding with `scripts/create_phase.py`
- Phase metadata validation with `scripts/validate_phase.py`
- Dry-run execution preview with `scripts/execute.py --dry-run`
- Phase status reporting with `scripts/report_phase.py`
- Self-contained step prompts with v2 execution context sections
- Optional hook profiles for stricter local checks
- A review rubric for harness-driven change review

## Use This When

- You want Codex to work through a project in explicit, reviewable steps
- You need per-step execution state in repository files
- You want future agents to resume from durable metadata instead of chat history

## Avoid This When

- You want a framework scaffold or application starter
- You want product-specific API integration in the template itself
- You need a demo app more than a harness

## Quick Start

1. Fill in `docs/PRD.md`, `docs/ARCHITECTURE.md`, and `docs/ADR.md` for the target project.
2. Create a phase scaffold:

```bash
python3 scripts/create_phase.py example-phase --steps project-setup,core-domain,final-review
```

3. Fill in the generated `phases/example-phase/step{N}.md` files.
4. Validate the phase metadata:

```bash
python3 scripts/validate_phase.py example-phase
```

5. Preview the next execution:

```bash
python3 scripts/execute.py example-phase --dry-run
```

6. Check progress when needed:

```bash
python3 scripts/report_phase.py example-phase
```

7. Run the phase:

```bash
python3 scripts/execute.py example-phase
```

## Repository Map

| Path | Purpose |
| --- | --- |
| `AGENTS.md` | Operating rules for harness work. |
| `.agents/skills/harness/SKILL.md` | Planning and execution workflow. |
| `.agents/skills/review/SKILL.md` | Review rubric for harness-driven changes. |
| `.codex/` | Codex hook configuration and profiles. |
| `docs/PRD.md` | Product requirements template. |
| `docs/ARCHITECTURE.md` | Architecture template. |
| `docs/ADR.md` | Decision record template. |
| `docs/HARNESS_TEMPLATE_GUIDE.md` | Detailed guide for using this template. |
| `docs/HARNESS_TEMPLATE_SUMMARY.md` | Concise template summary and step format reference. |
| `docs/HARNESS_ADVANCEMENT_ROADMAP.md` | Next harness improvement roadmap. |
| `docs/NEXT_PROGRESS_PLAN.md` | Handoff-friendly next-step plan. |
| `phases/index.json` | Top-level phase registry. |
| `scripts/create_phase.py` | Phase scaffold generator. |
| `scripts/validate_phase.py` | Phase metadata validator. |
| `scripts/report_phase.py` | Phase status reporter. |
| `scripts/execute.py` | Codex phase executor. |
| `assets/readme-hero.png` | README hero image. |

## Validation And Execution

Run the template checks before execution:

```bash
.githooks/pre-commit
```

`scripts/execute.py` creates or checks out `feat-{phase-name}`, invokes `codex exec` for each pending step, writes phase metadata, and commits code changes separately from harness metadata. Use `--dry-run` to inspect the target branch, next pending step, step prompt path, and the files the executor would read.

The executor expects a clean worktree. Commit, stash, or remove unrelated local changes before running a phase.

## Customizing The Template

1. Replace `docs/PRD.md`, `docs/ARCHITECTURE.md`, and `docs/ADR.md` with project-specific content.
2. Create the first phase in `phases/index.json`.
3. Generate self-contained step files and keep each one small enough for a single Codex execution.
4. Use the guide in [docs/HARNESS_TEMPLATE_GUIDE.md](docs/HARNESS_TEMPLATE_GUIDE.md) for detailed workflow, README patterns, and adaptation notes.

## Related Docs

- [Harness Template Guide](docs/HARNESS_TEMPLATE_GUIDE.md)
- [Harness Template Summary](docs/HARNESS_TEMPLATE_SUMMARY.md)
- [Template Evolution Roadmap](docs/TEMPLATE_EVOLUTION.md)
- [Harness Advancement Roadmap](docs/HARNESS_ADVANCEMENT_ROADMAP.md)
