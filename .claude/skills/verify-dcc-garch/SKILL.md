---
name: verify-dcc-garch
description: DCC-GARCH(Engle 2002, Aielli 2013) 절차 준수 여부 검증. 정상성, 잔차 진단, MLE 다중 초기값, ADF 사전검증, cDCC 보정을 점검한다.
---

# verify-dcc-garch

본 프로젝트의 DCC-GARCH 구현이 Engle (2002) 및 Aielli (2013) 표준을 준수하는지 검증한다.

## 절차

1. `.claude/references/catalog.json`의 `dcc_garch` 섹션 로드.
2. `.claude/references/dcc_garch.md` 체크리스트 확인.
3. source_files (`Edit_mj/GARCH_분석.ipynb`, `test/GARCH_분석.ipynb`, `_review/scripts/01_garch_fixed.py`) 분석:
   - GARCH order: `param_regex.garch_order`로 추출
   - α + β 합계: 결과 csv (`_review/results/garch_*.csv`)에서 alpha, beta 컬럼 확인 → 합 < 1 ?
   - DCC a + b: 동일하게 < 1 ?
   - ADF 검정 코드: `grep -E "adfuller|ADF|adf_test"`
   - Ljung-Box: `grep -E "ljungbox|Ljung|acorr"`
   - MLE 초기값: `grep -E "x0|init|starts"`로 다중 초기값 여부
   - cDCC 보정: `grep -E "cDCC|aielli|Aielli"`

4. 항목별 판정:

   | 항목 | PASS | WARN | FAIL |
   |---|---|---|---|
   | GARCH α+β | <1 | 0.99~1.0 (경계) | ≥1 |
   | DCC a+b | <1 | 경계 | ≥1 |
   | ADF 사전검증 | 코드 존재 + 결과 보고 | 코드만 | 부재 |
   | Ljung-Box | 잔차 + 잔차² 모두 | 잔차만 | 부재 |
   | MLE 다중초기값 | ≥5 | 2~4 | 단일 |
   | Aielli 2013 cDCC | 적용 또는 미적용 사유 | 언급만 | 무관심 |

5. 보고서 저장: `.claude/verification_reports/YYYY-MM-DD_dcc_garch.md`
6. 한국어 요약 출력 + 인용 첨부.

## 출력 형식
verify-event-study와 동일 패턴. 끝에 `참조: Engle (2002, JBES 20:339-350); Aielli (2013, JBES 31:282-299)`.

## 도구
Read, Bash + grep, Bash + cut/head, Write. 외부 호출 없음.
