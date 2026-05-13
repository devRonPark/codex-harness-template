# Architecture Decision Records

Record architecture decisions for the target project here. Keep decisions short, explicit, and useful for future Codex steps.

## ADR Template

### ADR-000: Decision Title

**Decision**: State the decision.

**Context**: Explain the pressure, constraint, or problem behind the decision.

**Reasoning**: Explain why this option was selected.

**Tradeoffs**: Explain what this decision makes harder or excludes.

**Status**: Proposed | Accepted | Superseded

### ADR-001: Optional Hook Profiles

**Decision**: Hook profiles are opt-in. The default profile is `minimal`, selected unless `HARNESS_HOOK_PROFILE`, `CODEX_HOOK_PROFILE`, or `.codex/hook-profile.local` specifies another profile.

**Context**: The base template needs portable guardrails, but strict local workflow checks such as TDD enforcement, secret scanning, and phase metadata validation should not be forced on every target project.

**Reasoning**: Environment variables support per-command use, and `.codex/hook-profile.local` supports a durable local preference without committing machine-specific workflow choices.

**Tradeoffs**: Strict checks are not active unless explicitly selected, so users who want stronger defaults must opt in.

**Status**: Accepted

### ADR-002: Findings-First Review Rubric

**Decision**: Harness reviews use a findings-first rubric with `P0`, `P1`, `P2`, and `P3` severities. `P0` and unresolved `P1` findings block completion; `P2` findings may be fixed or recorded as residual risk; `P3` findings do not block completion by default.

**Context**: The template needs a clear stop condition so Codex-driven work does not drift beyond the requested phase or step scope while still preventing unverified or incomplete changes from being marked done.

**Reasoning**: Severity-ranked findings, explicit verification evidence, residual risks, and small recommendations make review outcomes concrete. This borrows the useful review discipline from larger agent harness projects while keeping the base template product-neutral.

**Tradeoffs**: The rubric depends on reviewer judgment and does not automate quality gates. Future template work can add stronger validation only after repeated real usage shows which checks are worth automating.

**Status**: Accepted
