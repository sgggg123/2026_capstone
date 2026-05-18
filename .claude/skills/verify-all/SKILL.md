---
name: verify-all
description: 7개 검증 스킬을 의존성 순서로 순차 실행하고 종합 PASS/WARN/FAIL 매트릭스를 생성한다.
---

# verify-all

전체 학술 검증을 한 번에 수행한다. 이 스킬은 오케스트레이터로, 7개 개별 검증 스킬을 호출한다.

## 사전 무결성 점검

1. `.claude/references/catalog.json` 존재 + JSON 파싱 가능: 실패 시 즉시 중단
   ```bash
   python3 -c "import json; json.load(open('.claude/references/catalog.json'))"
   ```
2. 7개 method 키 (`event_study, dcc_garch, quantile_reg, gpr_hybrid, bootstrap, multiple_testing, safe_haven`) 모두 존재
3. 각 method의 `source_files`가 실제 디스크에 존재

이 단계 실패 시: "❌ 카탈로그 무결성 실패" 한 줄 + 구체 오류 출력 후 중단.

## 실행 순서 (의존성 고려)

| 순서 | 스킬 | 의존성 |
|---|---|---|
| 1 | `/verify-gpr-hybrid` | 입력 데이터 무결성 (다른 검증의 전제) |
| 2 | `/verify-bootstrap` | 이벤트 스터디·DCC가 사용 |
| 3 | `/verify-event-study` | bootstrap 사용 |
| 4 | `/verify-dcc-garch` | bootstrap 사용 |
| 5 | `/verify-quantile-reg` | 독립 |
| 6 | `/verify-multiple-testing` | event_study 결과 사용 |
| 7 | `/verify-safe-haven` | 위 모든 결과 통합 |

## 종합 보고

각 스킬의 출력을 받아 다음 매트릭스로 정리:

```
=== 학술 검증 종합 결과 (2026-05-10) ===

방법론               PASS  WARN  FAIL
─────────────────────────────────────
1. GPR Hybrid          4     1     0
2. Bootstrap           5     0     0
3. Event Study         5     1     1
4. DCC-GARCH           4     1     1
5. Quantile Reg        4     1     0
6. Multiple Testing    4     0     1
7. Safe-Haven          5     0     0
─────────────────────────────────────
총합                  31     4     3

❌ 즉시 조치 필요 (FAIL 3건):
- Event Study: Placebo 검증 셀 부재 → reports/...event_study.md
- DCC-GARCH: α+β = 1.02 (비정상) → reports/...dcc_garch.md
- Multiple Testing: BH-FDR 결과 컬럼 누락 → reports/...multiple_testing.md

⚠️ 검토 권유 (WARN 4건):
- ...

✅ 통과 (31건): 상세는 .claude/verification_reports/2026-05-10_*.md
```

저장: `.claude/verification_reports/YYYY-MM-DD_full.md` (위 매트릭스 포함)

## 사용 시나리오
- 분석 코드 변경 직후
- 보고서/논문 제출 전
- 새 이벤트 추가 후
- 팀원 작업 머지 전

## 도구
Read (catalog.json), Bash (skill 실행 로직), Write (종합 보고서).
