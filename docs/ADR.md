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
