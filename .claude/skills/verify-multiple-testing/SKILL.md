---
name: verify-multiple-testing
description: 다중비교 보정(Bonferroni / BH-FDR) 적용 검증. 검정 가족 정의, 보정 강도, 결과 해석 적절성 점검.
---

# verify-multiple-testing

다중 검정 보정이 사전 등록된 검정 가족(family)에 일관되게 적용되었는지 검증한다.

## 절차

1. catalog.json의 `multiple_testing` 섹션 로드.
2. source_files 분석:
   - 보정 적용 위치: `grep -E "bonferroni|alpha_star|alpha_bonf|fdr|FDR|benjamini"`
   - 검정 수 m 명시: `grep -E "(7\s*\*\s*7|49|n_tests|m\s*=)"`
   - α* 산식: `grep -E "0.05\s*/\s*49|alpha\s*/\s*"`

3. 결과 csv (`_review/results/event_study_summary_*.csv`)에서 보정 후 컬럼 (`p_bonf`, `p_fdr`, `sig_bonf`, `sig_fdr`) 존재 확인.

4. 항목별 판정:

   | 항목 | PASS | WARN | FAIL |
   |---|---|---|---|
   | 보정 적용 | Bonferroni 또는 BH-FDR | 언급만 | 미적용 |
   | family 정의 | 코드/주석에 명시 (m=49 등) | 추론 가능 | 모호 |
   | α* 산식 | 명시적 계산 | 하드코딩만 | 부재 |
   | 결과 컬럼 | sig_bonf 또는 sig_fdr | 일부만 | 미보고 |
   | 결과 해석 | "유의 증거 부족" 표현 | 중립 | "효과 없음" 단정 |

5. 결과 해석 검증:
   - `_review/분석방식_전체.md`나 결과 보고서 텍스트에서 "BTC는 안전자산이 아니다" 단정 표현 검색
   - Bonferroni 적용 후 FAIL 결과를 "효과 없음"으로 해석하면 WARN

6. 보고서 + 한국어 요약. 인용: `Benjamini & Hochberg (1995, JRSSB 57:289-300); Bonferroni (1936)`.

## 도구
Read, Bash + grep, Bash + head, Write.
