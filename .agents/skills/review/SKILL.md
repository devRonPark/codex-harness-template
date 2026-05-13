---
name: review
description: "Use when reviewing local changes in a project that uses this Codex Harness Template. Checks AGENTS.md, docs/ARCHITECTURE.md, docs/ADR.md, phase metadata, tests, guardrails, and buildability where applicable."
---

# Harness Project Review

Use this skill to review changes against the project's local contracts.
The review goal is to decide whether a harness step or template change is
complete enough to stop, not to expand the work opportunistically.

## Review Stance

Review findings-first. Prioritize concrete defects, regressions, scope drift,
missing validation, and metadata errors. Do not lead with praise or a broad
summary.

This rubric borrows the useful shape of evidence-heavy agent harness reviews:
severity-ranked findings, explicit verification, residual risks, and clear
recommendations. Keep the implementation product-neutral and lightweight.

## Inputs To Read

Before reviewing changes, read:

- `AGENTS.md`
- `docs/ARCHITECTURE.md`
- `docs/ADR.md`
- relevant `phases/{phase-name}/index.json`
- relevant `phases/{phase-name}/step{N}.md`

Then inspect changed files with Git when the repository has Git metadata.

## Severity Rubric

Use these severities consistently:

| Severity | Meaning | Examples |
| --- | --- | --- |
| `P0` | Blocks safe completion. Must be fixed before accepting the step. | Executor cannot run, phase JSON is invalid, required status fields are corrupt, secrets or generated caches are introduced, destructive changes are present. |
| `P1` | Makes the result untrustworthy. Fix before marking complete unless explicitly accepted by the user. | Acceptance criteria were not run or are missing, the requested feature is incomplete, step scope is exceeded, phase metadata lies about completion, product-neutral policy is violated. |
| `P2` | Important maintainability or follow-up issue. Fix if it is in scope or cheap; otherwise record as residual risk. | Docs and behavior diverge, error messages are unclear, validation coverage is thin, unnecessary refactoring obscures the change. |
| `P3` | Minor polish. Do not block completion by default. | Small wording issues, formatting cleanup, non-critical output clarity, optional organization improvements. |

Completion rule:

- Any `P0` or unresolved `P1` means the reviewed change is not done.
- `P2` findings can be fixed now or recorded as residual risk.
- `P3` findings should not cause scope creep unless the user asks for polish.
- If there are no `P0` or `P1` findings and validation evidence is adequate,
  the review should allow the work to stop.

## Checklist

Check these items:

1. **Architecture compliance**: Do changed files follow `docs/ARCHITECTURE.md`?
2. **Decision compliance**: Do changes stay within accepted decisions in `docs/ADR.md`?
3. **Step scope**: Did the change stay within the active step's instructions?
4. **Tests and validation**: Were the step acceptance criteria run or clearly blocked?
5. **Guardrails**: Do changes avoid violating `AGENTS.md` critical rules?
6. **Phase metadata**: Is `phases/{phase-name}/index.json` updated with the right status and summary/error/blocker field?
7. **Repository hygiene**: Are generated caches, build outputs, secrets, and local-only files excluded?
8. **Stop condition**: Is there a concrete reason to keep changing the work, or is it complete by the rubric?

Run validation commands when appropriate for the requested review scope. If a command cannot be run, state that clearly.

## Output

For code review requests, lead with concrete findings ordered by severity and include file/line references. If there are no findings, say so explicitly.

Use this structure:

1. **Findings**
   - List only actionable defects.
   - Prefix each finding with `P0`, `P1`, `P2`, or `P3`.
   - Include file and line references when available.
   - Include a reproduction command or observed failure when relevant.
2. **Open Questions**
   - Include only decisions that affect correctness or scope.
   - Omit the section when there are none.
3. **Residual Risks**
   - Note meaningful risks that remain after the review.
   - Distinguish unverified risk from confirmed defects.
4. **Verification**
   - List commands run and their result.
   - List commands not run and why.
5. **Checklist**
   - Include the table below for harness reviews.
6. **Recommendations**
   - Suggest the smallest next action.
   - Do not turn optional improvements into blockers.

Checklist table:

| Item | Result | Notes |
| --- | --- | --- |
| Architecture compliance | pass/fail | {detail} |
| Decision compliance | pass/fail | {detail} |
| Step scope | pass/fail | {detail} |
| Tests and validation | pass/fail | {detail} |
| Guardrails | pass/fail | {detail} |
| Phase metadata | pass/fail | {detail} |
| Repository hygiene | pass/fail | {detail} |
| Stop condition | pass/fail | {detail} |

If there are violations, propose concrete fixes.

## Do Not

- Do not request unrelated features as review findings. Reason: review should
  prevent scope creep.
- Do not require framework-specific commands in this product-neutral template.
  Reason: target projects define their own validation commands.
- Do not mark work complete when validation evidence is missing. Reason:
  unverified completion is a harness failure, not a cosmetic issue.
