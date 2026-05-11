---
name: review
description: "Use when reviewing local changes in a project that uses this Codex Harness Template. Checks AGENTS.md, docs/ARCHITECTURE.md, docs/ADR.md, phase metadata, tests, guardrails, and buildability where applicable."
---

# Harness Project Review

Use this skill to review changes against the project's local contracts.

## Inputs To Read

Before reviewing changes, read:

- `AGENTS.md`
- `docs/ARCHITECTURE.md`
- `docs/ADR.md`
- relevant `phases/{phase-name}/index.json`
- relevant `phases/{phase-name}/step{N}.md`

Then inspect changed files with Git when the repository has Git metadata.

## Checklist

Check these items:

1. **Architecture compliance**: Do changed files follow `docs/ARCHITECTURE.md`?
2. **Decision compliance**: Do changes stay within accepted decisions in `docs/ADR.md`?
3. **Step scope**: Did the change stay within the active step's instructions?
4. **Tests and validation**: Were the step acceptance criteria run or clearly blocked?
5. **Guardrails**: Do changes avoid violating `AGENTS.md` critical rules?
6. **Phase metadata**: Is `phases/{phase-name}/index.json` updated with the right status and summary/error/blocker field?

Run validation commands when appropriate for the requested review scope. If a command cannot be run, state that clearly.

## Output

For code review requests, lead with concrete findings ordered by severity and include file/line references. If there are no findings, say so explicitly.

Then include this checklist table:

| Item | Result | Notes |
| --- | --- | --- |
| Architecture compliance | pass/fail | {detail} |
| Decision compliance | pass/fail | {detail} |
| Step scope | pass/fail | {detail} |
| Tests and validation | pass/fail | {detail} |
| Guardrails | pass/fail | {detail} |
| Phase metadata | pass/fail | {detail} |

If there are violations, propose concrete fixes.
