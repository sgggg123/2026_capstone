---
name: verify-quantile-reg
description: 분위회귀(Koenker & Bassett 1978, Bouri 2017) 절차 검증. τ 임계값, 분위 크로싱, 표준오차 종류를 점검한다.
---

# verify-quantile-reg

본 프로젝트의 분위회귀가 Koenker & Bassett (1978) 표준 + Bouri (2017) Bitcoin 적용 절차를 따르는지 검증한다.

## 절차

1. catalog.json의 `quantile_reg` 섹션 로드.
2. source_files (`Edit_mj/분위수_회귀.ipynb`, `test/분위수_회귀.ipynb`) 분석:
   - τ 값: `grep -oE "(tau|TAU|quantile)\s*=\s*\[?([0-9.,\s]+)\]?"`로 추출
   - 표준오차 방법: `grep -E "bootstrap|sandwich|Powell|kernel"` 검출
   - 라이브러리: `grep -E "QuantReg|quantreg|statsmodels"` (statsmodels.QuantReg 표준)
   - 다중공선성: `grep -E "VIF|variance_inflation"`

3. τ 검증:
   - τ ∈ {0.05, 0.10, 0.50}: PASS
   - τ ∈ {0.01, 0.05, 0.10, 0.50, 0.90, 0.95}: PASS (양측)
   - τ < 0.01 또는 τ > 0.99 단독: WARN (꼬리 표본 부족)
   - τ 정의 부재: FAIL

4. 분위 크로싱: 결과 출력에서 β 추정치를 추출해 단조성 확인. 추출 실패 시 WARN(수동 점검 권유).

5. 항목별 판정:

   | 항목 | PASS | WARN | FAIL |
   |---|---|---|---|
   | τ 임계 | {0.05, 0.10} 포함 | τ 값 정당화 부족 | 부재 또는 극단 |
   | 표준오차 | bootstrap 또는 Powell | 미명시 | OLS sandwich 사용 |
   | 분위 크로싱 | 단조성 확인됨 | 추출 불가 | 크로싱 발견 |
   | 라이브러리 | statsmodels.QuantReg | 커스텀 + 검증 | 커스텀 + 무검증 |
   | Bouri 2017 인용 | 명시 | 언급 | 부재 |

6. 보고서 저장 + 한국어 요약. 인용: `Koenker & Bassett (1978, Econometrica 46:33-50); Bouri 외 (2017, FRL 23:87-95)`.

## 도구
Read, Bash + grep, Write.
