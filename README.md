# Codex Harness Template

Minimal template for running structured Codex implementation work through phase and step files.

This repository contains only the harness pieces. It does not include a web app, npm project, product implementation, provider integration, or completed demo phase.

## What Is Included

```text
.agents/skills/harness/SKILL.md   # Harness planning and execution workflow
.agents/skills/review/SKILL.md    # Review workflow for local changes
.codex/config.toml                # Codex hook feature flags
.codex/hooks.json                 # Hook registration
.codex/hooks/run-profile.sh       # Optional hook profile dispatcher
.codex/hooks/tdd-guard.sh         # Optional implementation edit guard
.githooks/pre-commit              # Template validation hook
docs/PRD.md                       # Product requirements template
docs/ARCHITECTURE.md              # Architecture template
docs/ADR.md                       # Decision record template
docs/HARNESS_TEMPLATE_SUMMARY.md  # Template usage guide
docs/TEMPLATE_EVOLUTION.md        # Personalization roadmap
docs/HARNESS_ADVANCEMENT_ROADMAP.md  # Next improvement roadmap
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
- Clean worktree before running `scripts/execute.py`; commit, stash, or remove unrelated local changes first.
- Codex CLI available as `codex`.
- Python 3.

`scripts/execute.py` creates or checks out `feat-{phase-name}`, invokes `codex exec` for each pending step, updates phase metadata, and commits code changes separately from harness metadata.
The executor refuses to start from a dirty worktree and stages only the changed paths it observes during the run instead of using a repository-wide `git add -A`.

Use `--dry-run` to validate metadata and inspect the target branch, next pending step, step prompt path, and files the executor would read. Dry-run mode does not invoke Codex, checkout branches, write timestamps, or create output files.

Use `scripts/report_phase.py` to summarize phase status without opening JSON manually. The report shows step counts, the next pending step, latest completed summary, blocker/error details, and existing output artifact paths.

## Review Rubric

Use `.agents/skills/review/SKILL.md` when reviewing harness-driven changes. The
rubric keeps reviews findings-first and assigns `P0` to `P3` severities:

- `P0` and unresolved `P1` findings block completion.
- `P2` findings can be fixed now or recorded as residual risk.
- `P3` findings are polish and should not expand scope by default.

The review output records verification evidence, residual risks, and a small
harness checklist so a step can stop when the requested scope is complete and
validated.

## Template Validation

```bash
.githooks/pre-commit
```

The optional pre-commit hook checks Python syntax, runs script unit tests, and validates JSON files.

## Hook Profiles

Hook profiles keep stricter local workflow checks opt-in. The default `minimal` profile runs the template validation above and does not block Codex edits.

Select a profile per command:

```bash
HARNESS_HOOK_PROFILE=phase-metadata .githooks/pre-commit
HARNESS_HOOK_PROFILE=strict .githooks/pre-commit
```

For Codex pre-edit hooks, `tdd` and `strict` enable `.codex/hooks/tdd-guard.sh`:

```bash
HARNESS_HOOK_PROFILE=tdd codex
```

For a local default, put one profile name in `.codex/hook-profile.local`. That file is ignored by git.

Profiles:

- `minimal`: Python syntax, script unit tests, and JSON validity.
- `json-valid`: alias for the default template validation.
- `phase-metadata`: default validation plus registered phase metadata validation.
- `no-secrets`: default validation plus a lightweight tracked-file secret scan.
- `tdd`: default validation, plus Codex pre-edit TDD guard.
- `strict`: default validation, phase metadata validation, secret scan, and Codex pre-edit TDD guard.

## Growing Your Own Harness

Use [docs/TEMPLATE_EVOLUTION.md](docs/TEMPLATE_EVOLUTION.md) as the working map for evolving this base template. Keep the base lean, add one capability at a time, and record stable decisions in `docs/ADR.md`.

Use [docs/HARNESS_ADVANCEMENT_ROADMAP.md](docs/HARNESS_ADVANCEMENT_ROADMAP.md) for the next research-backed improvement sequence after the current baseline.
