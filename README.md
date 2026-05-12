# Codex Harness Template

Minimal template for running structured Codex implementation work through phase and step files.

This repository contains only the harness pieces. It does not include a web app, npm project, product implementation, provider integration, or completed demo phase.

## What Is Included

```text
.agents/skills/harness/SKILL.md   # Harness planning and execution workflow
.agents/skills/review/SKILL.md    # Review workflow for local changes
.codex/config.toml                # Codex hook feature flags
.codex/hooks.json                 # Hook registration
.codex/hooks/tdd-guard.sh         # Optional implementation edit guard
.githooks/pre-commit              # Template validation hook
docs/PRD.md                       # Product requirements template
docs/ARCHITECTURE.md              # Architecture template
docs/ADR.md                       # Decision record template
docs/HARNESS_TEMPLATE_SUMMARY.md  # Template usage guide
docs/TEMPLATE_EVOLUTION.md        # Personalization roadmap
phases/index.json                 # Phase registry
scripts/create_phase.py           # Phase scaffold generator
scripts/validate_phase.py         # Phase metadata validator
scripts/report_phase.py           # Phase status reporter
scripts/execute.py                # Codex phase executor
```

## Basic Flow

1. Fill in `docs/PRD.md`, `docs/ARCHITECTURE.md`, and `docs/ADR.md` for the target project.
2. Generate a phase scaffold:

```bash
python3 scripts/create_phase.py example-phase --steps project-setup,core-domain,final-review
```

3. Fill in the generated step files.
4. Validate the phase metadata:

```bash
python3 scripts/validate_phase.py {phase-name}
```

5. Preview what the executor would run:

```bash
python3 scripts/execute.py {phase-name} --dry-run
```

6. Check phase status when needed:

```bash
python3 scripts/report_phase.py {phase-name}
```

7. Run the phase executor:

```bash
python3 scripts/execute.py {phase-name}
```

To push the resulting branch:

```bash
python3 scripts/execute.py {phase-name} --push
```

## Requirements

- Git repository initialized before running `scripts/execute.py`.
- Codex CLI available as `codex`.
- Python 3.

`scripts/execute.py` creates or checks out `feat-{phase-name}`, invokes `codex exec` for each pending step, updates phase metadata, and commits code changes separately from harness metadata.

Use `--dry-run` to validate metadata and inspect the target branch, next pending step, step prompt path, and files the executor would read. Dry-run mode does not invoke Codex, checkout branches, write timestamps, or create output files.

Use `scripts/report_phase.py` to summarize phase status without opening JSON manually. The report shows step counts, the next pending step, latest completed summary, blocker/error details, and existing output artifact paths.

## Template Validation

```bash
.githooks/pre-commit
```

The optional pre-commit hook checks Python syntax, runs script unit tests, and validates JSON files.

## Growing Your Own Harness

Use [docs/TEMPLATE_EVOLUTION.md](docs/TEMPLATE_EVOLUTION.md) as the working map for evolving this base template. Keep the base lean, add one capability at a time, and record stable decisions in `docs/ADR.md`.
