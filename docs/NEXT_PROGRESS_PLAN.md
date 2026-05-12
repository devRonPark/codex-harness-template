# Next Progress Plan

이 문서는 하네스 템플릿을 다음 단계로 발전시키기 위한 작업 순서와 맥락을 보존한다.

목적은 각 단계를 별도 브랜치에서 진행하더라도, 왜 그 작업이 필요한지와 다음 작업자가 무엇을 먼저 확인해야 하는지를 잃지 않도록 하는 것이다.

## Guiding Order

추천 순서는 기본 하네스를 깨지 않고 반복 작업을 줄이는 순서다.

```text
생성 자동화
-> 구조 검증
-> 실행 전 확인
-> 실행 상태 리포트
-> 훅 체계화
-> 개인 품질 기준 강화
```

각 단계는 앞 단계의 결과를 기반으로 한다. 먼저 입력 파일을 안정적으로 만들고, 그 다음 실행 가능 여부를 검증하며, 이후 실행 전후의 운영성을 개선한다.

## Common Branch Context

각 브랜치에서 작업을 시작할 때 먼저 읽을 파일:

- `AGENTS.md`
- `docs/HARNESS_TEMPLATE_SUMMARY.md`
- `docs/TEMPLATE_EVOLUTION.md`
- `docs/NEXT_PROGRESS_PLAN.md`
- 관련 스크립트 또는 스킬 파일

공통 원칙:

- 템플릿 루트에 product-specific application code를 추가하지 않는다.
- 하네스 기능은 product-neutral하게 유지한다.
- phase metadata 변경은 executor, validator, report 도구와 함께 일관성을 확인한다.
- 작업 완료 시 관련 문서와 검증 명령을 함께 갱신한다.
- 브랜치별 변경은 작게 유지하고, 다음 단계가 읽을 수 있는 summary를 남긴다.

## Step 1. Phase Scaffolder

권장 브랜치: `feat-phase-scaffolder`

대상:

- `scripts/create_phase.py`
- `docs/HARNESS_TEMPLATE_SUMMARY.md`
- `docs/TEMPLATE_EVOLUTION.md`

이유:

`phase`와 `step` 파일을 매번 손으로 만들면 실수가 자주 난다. `phases/index.json`, `phases/{phase}/index.json`, `step0.md` 같은 구조는 정형적이라 자동화 효과가 크다.

가장 먼저 만들 가치가 있는 이유는 실행 로직을 건드리지 않고도 생산성이 바로 좋아지기 때문이다. 이 단계는 하네스의 입력 파일을 안정적으로 만드는 작업이다.

현재 메모:

- 이 저장소에는 이미 `scripts/create_phase.py`가 존재한다.
- 이 단계의 후속 작업은 구현 여부 확인, 사용성 보완, 문서와 실제 동작의 일치 검증이 중심이다.

완료 기준:

- phase registry와 phase detail file이 일관되게 생성된다.
- step 번호가 `0`부터 시작한다.
- 생성된 step 파일이 하네스 권장 prompt 구조를 따른다.
- 기본 검증 명령이 통과한다.

## Step 2. Phase Metadata Validator

권장 브랜치: `feat-phase-validator`

대상:

- `scripts/validate_phase.py`
- `scripts/execute.py`
- `docs/HARNESS_TEMPLATE_SUMMARY.md`
- `docs/TEMPLATE_EVOLUTION.md`

이유:

executor가 돌기 전에 phase 구조가 맞는지 검증해야 한다. 예를 들어 `index.json`에는 step 2가 있는데 `step2.md`가 없거나, status가 잘못되어 있으면 실행 중간에 실패한다.

현재 메모:

- 이 저장소에는 `scripts/validate_phase.py`가 추가되었다.
- validator는 실행 전 metadata 오류를 모아서 보여준다.
- 다음 후속 작업은 executor dry-run에서 이 validator를 재사용하는 것이다.

scaffolder 다음에 validator가 필요한 이유는 "잘 만든다"와 "실행 가능한 상태인지 확인한다"가 한 세트이기 때문이다. 이후 executor 기능을 늘릴 때도 validator가 안전망이 된다.

검증 대상 예시:

- `phases/index.json`에 phase entry가 존재한다.
- `phases/{phase}/index.json`이 존재한다.
- `phase` 값이 directory name과 일치한다.
- step 번호가 `0`부터 연속된다.
- 각 `step{N}.md`가 존재한다.
- status 값이 허용 목록에 포함된다.
- `completed` step에는 `summary`가 있다.
- `blocked` step에는 `blocked_reason`이 있다.
- `error` step에는 `error_message`가 있다.

완료 기준:

- 잘못된 phase metadata에 대해 명확한 오류 메시지를 출력한다.
- 정상 phase는 exit code `0`으로 통과한다.
- executor 또는 dry-run이 재사용할 수 있는 검증 경로가 생긴다.

## Step 3. Executor Dry Run

권장 브랜치: `feat-execute-dry-run`

대상:

- `scripts/execute.py`
- `scripts/validate_phase.py`
- `docs/HARNESS_TEMPLATE_SUMMARY.md`
- `docs/TEMPLATE_EVOLUTION.md`

이유:

실제로 Codex를 실행하기 전에 어떤 branch, 어떤 phase, 어떤 step, 어떤 prompt가 실행될지 확인할 수 있어야 한다. 특히 자동 실행 성격이 강한 `codex exec` 흐름에서는 사전 확인이 중요하다.

validator가 먼저 있어야 dry-run이 의미 있다. dry-run은 "검증 결과 + 다음 실행 계획"을 보여주는 역할을 맡는다.

현재 메모:

- `scripts/execute.py`에 `--dry-run`이 추가되었다.
- dry-run은 `validate_phase.validate_phase(...)`를 재사용한다.
- dry-run은 대상 branch, 다음 pending step, step prompt 파일, 이전 completed summary, 읽을 파일, Codex 실행 개요를 출력한다.
- dry-run은 Codex를 호출하지 않고 branch checkout/create, timestamp 기록, output JSON 생성을 하지 않는다.

dry-run에서 보여줄 정보:

- 대상 phase
- checkout 또는 생성될 branch
- 다음 pending step
- step prompt 파일
- 완료된 이전 step summary
- 실행될 `codex exec` 개요
- validation result

완료 기준:

- `python3 scripts/execute.py {phase-name} --dry-run`이 Codex 실행 없이 종료된다.
- phase metadata 검증 결과가 함께 표시된다.
- 다음 실행 대상을 사람이 검토할 수 있을 만큼 구체적으로 출력한다.

## Step 4. Phase Report

권장 브랜치: `feat-phase-report`

대상:

- `scripts/report_phase.py`
- `docs/HARNESS_TEMPLATE_SUMMARY.md`
- `docs/TEMPLATE_EVOLUTION.md`

이유:

phase가 길어지면 JSON을 직접 열어보며 진행 상태를 파악하기 번거롭다. 완료, 대기, 실패, 차단 step 수와 다음 step, 최근 summary를 바로 볼 수 있으면 운영성이 좋아진다.

dry-run 이후에 두는 이유는 실행 전 확인보다 실행 후 또는 중간 상태 파악이 두 번째 문제이기 때문이다. 처음부터 report를 만들 수는 있지만, phase 생성과 실행 안정성이 먼저다.

현재 메모:

- `scripts/report_phase.py`가 추가되었다.
- report는 `validate_phase.validate_phase(...)`를 재사용한다.
- report는 phase status, completed/pending/blocked/error step count, next pending step, latest completed summary, blocked/error detail, existing output artifact path를 출력한다.

리포트에 포함할 정보:

- phase status
- completed / pending / error / blocked step count
- next pending step
- latest completed summary
- blocked reason 또는 error message
- raw output artifact path가 있으면 표시

완료 기준:

- `python3 scripts/report_phase.py {phase-name}` 명령으로 상태 요약을 볼 수 있다.
- 사람이 JSON을 직접 열지 않아도 다음 조치를 판단할 수 있다.
- 잘못된 phase에 대해서는 validator와 일관된 오류를 낸다.

## Step 5. Hook Profiles

권장 브랜치: `feat-hook-profiles`

대상:

- `.codex/hooks.json`
- `.codex/hooks/`
- `.githooks/pre-commit`
- `docs/HARNESS_TEMPLATE_SUMMARY.md`
- `docs/TEMPLATE_EVOLUTION.md`

이유:

현재는 TDD guard가 켜져 있고 pre-commit은 템플릿 검증만 한다. 시간이 지나면 `no-secrets`, `json-valid`, `phase-metadata`, `tdd` 같은 훅을 선택적으로 켜고 끄고 싶어질 가능성이 크다.

이 작업을 너무 일찍 만들면 과설계가 된다. 어떤 검증이 실제로 자주 필요한지 몇 번 사용해본 뒤 profile로 묶는 것이 낫다.

후보 profile:

- `minimal`: 기본 템플릿 검증만 수행
- `phase-metadata`: phase JSON과 step 파일 구조 검증
- `tdd`: implementation edit 전 TDD guard 적용
- `strict`: secrets, JSON, metadata, template validation을 함께 수행

현재 메모:

- `.codex/hooks/run-profile.sh`가 profile dispatch를 담당한다.
- profile 선택 우선순위는 `HARNESS_HOOK_PROFILE`, `CODEX_HOOK_PROFILE`, `.codex/hook-profile.local`, `minimal`이다.
- Codex `PreToolUse` hook은 기본 `minimal`에서는 blocking하지 않고, `tdd` 또는 `strict`에서만 기존 TDD guard를 실행한다.
- `.githooks/pre-commit`은 profile runner를 호출한다.
- `phase-metadata`, `no-secrets`, `strict`는 기본 template validation 위에 opt-in 검사를 추가한다.

완료 기준:

- hook profile의 목적과 켜는 방법이 문서화된다.
- 기본 동작은 product-neutral하고 portable하게 유지된다.
- framework-specific validation command를 기본 profile에 넣지 않는다.

## Step 6. Personal Review Rubric

권장 브랜치: `feat-review-rubric`

대상:

- `.agents/skills/review/SKILL.md`
- `docs/TEMPLATE_EVOLUTION.md`
- 필요하면 `docs/HARNESS_TEMPLATE_SUMMARY.md`

이유:

하네스가 반복 사용되면 "원하는 Codex 결과물의 기준"이 생긴다. 예를 들어 step scope 위반, 테스트 부족, phase metadata 누락, 불필요한 리팩터링 같은 것을 어떤 심각도로 볼지 정해야 한다.

마지막에 두는 이유는 실제 사용 경험이 쌓여야 좋은 rubric이 나오기 때문이다. 처음부터 리뷰 규칙을 촘촘하게 만들면 현실과 안 맞는 체크리스트가 되기 쉽다.

리뷰 항목 후보:

- step scope를 벗어난 변경
- acceptance criteria 미실행 또는 누락
- phase metadata status/summary 누락
- product-neutral 원칙 위반
- generated cache 또는 local-only file 추가
- 불필요한 리팩터링
- 문서와 실제 동작 불일치

완료 기준:

- review skill이 findings-first review 형식을 유지한다.
- severity 기준이 구체적이다.
- 하네스 작업에서 반복적으로 발생한 실제 문제를 반영한다.

## Handoff Template

각 브랜치 작업을 마칠 때 다음 내용을 PR description, commit message, 또는 별도 메모에 남긴다.

```markdown
## Handoff

- Branch:
- Step:
- Status:
- Changed files:
- Validation run:
- Important decisions:
- Follow-up for next branch:
```

## Current Priority

다음으로 이어갈 우선순위는 `Step 6. Personal Review Rubric`이다.

`Step 1. Phase Scaffolder`, `Step 2. Phase Metadata Validator`, `Step 3. Executor Dry Run`, `Step 4. Phase Report`, `Step 5. Hook Profiles`는 현재 저장소에 존재한다. 다음 작업자는 `.agents/skills/review/SKILL.md`를 중심으로 personal review rubric을 강화하는 것이 자연스럽다.
