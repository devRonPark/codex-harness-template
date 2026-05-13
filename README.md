# Codex Harness Template

![Codex Harness Template hero](assets/readme-hero.png)

구조화된 Codex 구현 작업을 위한 최소 템플릿입니다. 목표를 정의하고, 작업을 phase 파일로 나누고, 메타데이터를 검증한 뒤, 실행을 미리 보고, 각 step을 영속적인 상태 추적으로 실행합니다.

이 저장소에는 하네스 구성요소만 들어 있습니다. 애플리케이션 스캐폴드, 패키지 관리자 설정, 프레임워크 의존성, provider 통합, 완성된 데모 앱은 포함하지 않습니다.

## 제공 기능

- `scripts/create_phase.py`로 phase scaffold 생성
- `scripts/validate_phase.py`로 phase 메타데이터 검증
- `scripts/execute.py --dry-run`으로 실행 미리보기
- `scripts/report_phase.py`로 phase 상태 리포트
- v2 실행 컨텍스트 섹션이 포함된 self-contained step prompt
- 더 엄격한 로컬 검사를 위한 선택적 hook profile
- 하네스 기반 변경 검토용 review rubric

## 이런 경우에 사용

- Codex에게 명시적이고 검토 가능한 step 단위로 일을 시키고 싶을 때
- step별 실행 상태를 저장소 파일에 남기고 싶을 때
- 다음 에이전트가 채팅 기록이 아니라 영속 메타데이터에서 이어받게 하고 싶을 때

## 이런 경우에는 사용하지 않음

- 프레임워크 스캐폴드나 앱 스타터가 필요할 때
- 템플릿 안에 product-specific API 통합이 필요할 때
- 데모 앱이 하네스보다 더 중요한 경우

## 빠른 시작

1. 대상 프로젝트의 `docs/PRD.md`, `docs/ARCHITECTURE.md`, `docs/ADR.md`를 채웁니다.
2. phase scaffold를 생성합니다.

```bash
python3 scripts/create_phase.py example-phase --steps project-setup,core-domain,final-review
```

3. 생성된 `phases/example-phase/step{N}.md` 파일을 채웁니다.
4. phase 메타데이터를 검증합니다.

```bash
python3 scripts/validate_phase.py example-phase
```

5. 다음 실행을 미리 봅니다.

```bash
python3 scripts/execute.py example-phase --dry-run
```

6. 진행 상태를 확인합니다.

```bash
python3 scripts/report_phase.py example-phase
```

7. phase를 실행합니다.

```bash
python3 scripts/execute.py example-phase
```

## 저장소 구성

| 경로 | 용도 |
| --- | --- |
| `AGENTS.md` | 하네스 작업을 위한 운영 규칙 |
| `.agents/skills/harness/SKILL.md` | planning 및 execution workflow |
| `.agents/skills/review/SKILL.md` | harness 변경 검토 기준 |
| `.codex/` | Codex hook 설정과 profile |
| `docs/PRD.md` | product requirements 템플릿 |
| `docs/ARCHITECTURE.md` | architecture 템플릿 |
| `docs/ADR.md` | decision record 템플릿 |
| `docs/HARNESS_TEMPLATE_GUIDE.md` | 이 템플릿의 상세 가이드 |
| `docs/HARNESS_TEMPLATE_SUMMARY.md` | 간단한 요약과 step 형식 참고문서 |
| `docs/HARNESS_ADVANCEMENT_ROADMAP.md` | 다음 하네스 개선 로드맵 |
| `docs/NEXT_PROGRESS_PLAN.md` | handoff용 다음 단계 계획 |
| `phases/index.json` | 최상위 phase registry |
| `scripts/create_phase.py` | phase scaffold 생성기 |
| `scripts/validate_phase.py` | phase 메타데이터 검증기 |
| `scripts/report_phase.py` | phase 상태 리포터 |
| `scripts/execute.py` | Codex phase 실행기 |
| `assets/readme-hero.png` | README hero 이미지 |

## 검증과 실행

실행 전에 템플릿 검사를 돌립니다.

```bash
.githooks/pre-commit
```

`scripts/execute.py`는 `feat-{phase-name}` 브랜치를 만들거나 체크아웃하고, 각 pending step마다 `codex exec`를 호출하며, phase 메타데이터를 기록하고, 코드 변경과 하네스 메타데이터를 분리해서 커밋합니다. `--dry-run`으로 대상 브랜치, 다음 pending step, step prompt 경로, executor가 읽을 파일을 확인할 수 있습니다.

executor는 clean worktree를 기대합니다. phase를 실행하기 전에 관련 없는 로컬 변경은 commit, stash, 또는 제거해야 합니다.

## 템플릿 커스터마이징

1. `docs/PRD.md`, `docs/ARCHITECTURE.md`, `docs/ADR.md`를 프로젝트 전용 내용으로 교체합니다.
2. `phases/index.json`에 첫 phase를 추가합니다.
3. self-contained step 파일을 생성하고, 각 step은 한 번의 Codex 실행으로 끝날 정도로 작게 유지합니다.
4. 세부 workflow와 README 패턴, 적응 노트는 [docs/HARNESS_TEMPLATE_GUIDE.md](docs/HARNESS_TEMPLATE_GUIDE.md)를 참고합니다.

## 관련 문서

- [Harness Template Guide](docs/HARNESS_TEMPLATE_GUIDE.md)
- [Harness Template Summary](docs/HARNESS_TEMPLATE_SUMMARY.md)
- [Template Evolution Roadmap](docs/TEMPLATE_EVOLUTION.md)
- [Harness Advancement Roadmap](docs/HARNESS_ADVANCEMENT_ROADMAP.md)
