# Harness Advancement Roadmap

This document records the next roadmap for improving the Codex Harness Template after the current baseline. It is based on the current repository state and external workflow examples from other agent-harness projects.

The goal is not to turn this template into a full application framework. The goal is to keep it product-neutral while improving repeatability, verification, resumability, and eventually safe parallel execution.

## Current Baseline

The template already includes the first layer of harness automation:

- phase scaffolding through `scripts/create_phase.py`
- phase metadata validation through `scripts/validate_phase.py`
- executor dry-run preview through `scripts/execute.py --dry-run`
- phase status reporting through `scripts/report_phase.py`
- optional hook profiles through `.codex/hooks/run-profile.sh`
- self-contained phase step prompts under `phases/{phase-name}/step{N}.md`
- product contract templates in `docs/PRD.md`, `docs/ARCHITECTURE.md`, and `docs/ADR.md`

This baseline should stay small. Future work should add durable harness behavior, not product-specific implementation code.

## External Patterns Reviewed

The most useful external examples point in the same direction: persist state in files, keep work units small, preserve handoff context, and make verification explicit.

| Source | Pattern To Borrow | Notes |
| --- | --- | --- |
| [OpenAI Cookbook: Codex Exec Plans](https://cookbook.openai.com/articles/codex_exec_plans/) | Living execution plans with progress, decisions, discoveries, validation, and recovery notes. | Strong fit for improving step templates and handoff quality. |
| [ninjaa/openai-codex-exec-plan](https://github.com/ninjaa/openai-codex-exec-plan) | One task maps to one self-contained ExecPlan folder. | Useful for naming and cleanup conventions. |
| [applied-artificial-intelligence/claude-code-toolkit](https://github.com/applied-artificial-intelligence/claude-code-toolkit) | `explore -> plan -> next -> ship`, file-based state, session handoffs, quality gates, git checkpoints. | Strong fit for run ledgers, resumability, and step-level checkpoints. |
| [badlogic/claude-commands](https://github.com/badlogic/claude-commands) | Todo-to-task state machine with `task.md`, `analysis.md`, branch or worktree isolation. | Good reference for keeping workflows small and portable. |
| [wshobson/agents](https://github.com/wshobson/agents) | Focused plugins, progressive disclosure, composable workflow units. | Good boundary check against loading too much context by default. |
| [barkain/claude-code-workflow-orchestration](https://github.com/barkain/claude-code-workflow-orchestration) | Dependency-aware phases, waves, parallel execution, soft hook nudges. | Useful later, after the sequential harness is better instrumented. |
| [WorldFlowAI/everything-claude-code](https://github.com/worldflowai/everything-claude-code) | Cross-platform hooks, setup detection, agents/skills/hooks/rules separation. | Useful when packaging and portability become priorities. |
| [agentsmd/agents.md](https://github.com/agentsmd/agents.md) | `AGENTS.md` as a predictable agent-facing project guide. | Confirms the current template's `AGENTS.md` centered design. |

## Roadmap Principles

1. Preserve product neutrality.
2. Prefer explicit files over hidden process state.
3. Keep the default path sequential and simple.
4. Add metadata only when scripts and docs use it consistently.
5. Make every step resumable from repository files alone.
6. Make validation observable with commands and evidence.
7. Treat parallel execution as a later capability, not a default mode.

## Recommended Roadmap

### 1. Personal Review Rubric

Goal: make `.agents/skills/review/SKILL.md` reflect the desired review standard for harness-driven work.

Status: implemented. The review skill now defines a `P0` to `P3` severity
rubric, findings-first output, verification evidence, residual risks, and a
stop condition for deciding when work is complete enough to stop.

Scope:

- add a small severity rubric, such as `P0`, `P1`, `P2`, `P3`
- check step scope, acceptance criteria, validation evidence, phase metadata, and product-neutral policy
- keep the review output findings-first
- require reviewers to report which validation commands they ran or could not run

Why next: the harness can now create, validate, preview, report, and guard phases. The next quality gap is a consistent human/agent review standard.

Acceptance:

- review skill names the highest-risk harness failures explicitly
- review responses prioritize actionable findings over summaries
- no framework-specific commands are added to the base template

### 2. Step Template v2

Goal: make each generated `step{N}.md` stronger as a self-contained execution unit.

Scope:

- add optional sections for `Expected Output`, `Evidence`, `Decision Notes`, and `Recovery`
- clarify that each step must include exact validation commands and success observations
- keep the template short enough that agents still follow it

Why: ExecPlan-style living documents work because they preserve progress, decisions, and surprises. The harness does not need a large monolithic ExecPlan, but each step should carry enough recovery context for a fresh Codex execution.

Acceptance:

- `scripts/create_phase.py` generates the updated step skeleton
- harness docs describe the section purpose
- existing tests for generated phase structure still pass

### 3. Phase Run Ledger

Goal: record execution attempts as append-only structured events.

Scope:

- add `phases/{phase-name}/events.jsonl`
- record step attempt start, step attempt end, exit code, status transition, duration, and validation command summary when available
- extend `scripts/report_phase.py` to show recent attempts and retry history

Why: current output JSON preserves raw Codex output, but there is no concise timeline of what happened. A ledger improves debugging, handoffs, and later automation.

Acceptance:

- executor appends one event per important transition
- report output includes latest attempt context without requiring raw output inspection
- ledger writes are additive and safe to inspect manually

### 4. Executor Configuration

Goal: make executor behavior configurable without editing `scripts/execute.py`.

Scope:

- add CLI flags for `--max-retries`, `--timeout`, `--sandbox`, `--approval-policy`, and `--no-commit`
- optionally add `.codex/harness.json` for local defaults
- ensure dry-run prints the effective configuration

Why: retry count, timeout, sandbox, approval policy, and commit behavior are operating choices. Hard-coding them makes the harness less reusable across projects.

Acceptance:

- default behavior remains unchanged
- dry-run displays effective executor settings
- tests cover defaults and at least one override

### 5. Phase Metadata Schema

Goal: make phase metadata contracts explicit and easier to extend.

Scope:

- add a JSON Schema for `phases/index.json`
- add a JSON Schema for `phases/{phase-name}/index.json`
- keep `scripts/validate_phase.py` as the user-facing validator

Why: metadata will become more important once ledgers, dependency fields, or executor settings are introduced. A schema keeps the contract visible.

Acceptance:

- schema files are documented
- validator and tests stay aligned with the schema
- no third-party runtime dependency is required unless deliberately accepted in `docs/ADR.md`

### 6. Worktree Isolation

Goal: optionally run phases or isolated steps in separate git worktrees.

Scope:

- add an opt-in `--worktree` mode
- create predictable worktree paths outside the template root or under a gitignored local directory
- document cleanup and orphan detection

Why: branch-only execution is simple, but worktrees make parallel experiments and recovery safer. This should stay opt-in until the sequential executor is well instrumented.

Acceptance:

- default executor behavior remains branch-based
- worktree mode refuses to proceed when cleanup would be ambiguous
- report output includes worktree location when one is active

### 7. Dependency-Aware Parallel Execution

Goal: allow independent steps to run in waves only when metadata proves they are safe to parallelize.

Scope:

- add optional `depends_on` or `wave` metadata to phase steps
- update validator to reject invalid dependencies
- add a dry-run view that shows execution waves
- run parallel execution only behind an explicit flag

Why: other orchestration projects show that parallel execution is useful, but it increases merge and ownership risk. The harness should first make dependencies explicit and auditable.

Acceptance:

- sequential execution remains the default
- dry-run explains why each step is in its wave
- conflicting write scopes or missing dependencies are treated as validation errors when parallel mode is requested

### 8. Portable Packaging

Goal: make the harness easy to reuse in new repositories without copying stale or local files.

Scope:

- add an installer or copy script for the product-neutral harness files
- document which files are template-owned and which are project-owned
- keep packaging optional and dependency-light

Why: once the harness stabilizes, reuse should be easy. Packaging should not come before the core workflow is clear.

Acceptance:

- a new repository can receive the harness files predictably
- local files such as `.codex/hook-profile.local`, generated caches, and run artifacts are excluded
- packaging behavior is documented in `README.md`

## Deferred Or Rejected For Now

These ideas should stay out of the base template unless the template scope deliberately changes:

- application scaffolds such as Next.js, React, Vite, FastAPI, or Rails
- provider-specific API integration
- npm, pnpm, yarn, or lockfile assumptions
- default framework-specific validation commands
- always-on parallel execution
- generated Codex output artifacts committed as examples
- local session history indexes

## Near-Term Execution Order

The next two implementation branches should stay small:

1. `feat-step-template-v2`
   - update `scripts/create_phase.py`
   - update step prompt docs
   - add tests for generated template content

2. `feat-phase-run-ledger`
   - add append-only execution events
   - extend report output
   - add tests for event creation and reporting

After those two, revisit executor configuration and schema validation with the benefit of real usage data.
