---
name: verify-safe-haven
description: Baur & Lucey(2010) safe-haven 프레임워크 적용 검증. 용어 정의 일관성, 3조건 적용, 결론 표현 적절성 점검.
---

# verify-safe-haven

최종 판정과 보고서 표현이 Baur & Lucey (2010) 정의를 위반하지 않는지 검증한다. 학술적 정직성을 위한 가장 중요한 검증.

## 절차

1. catalog.json의 `safe_haven` 섹션 로드.
2. 검증 대상 파일:
   - `_review/분석방식_전체.md`
   - `_review/results/btc_logic_ablation.csv`
   - `_review/results/btc_returns_compare.csv`
   - `_review/scripts/03_btc_logic_ablation.py`
   - 기타 보고서 텍스트 (`_review/*.md`)

3. **용어 위반 검색** (자동):
   - "strong safe haven" 단어 + 같은 문단/이벤트에서 β > 0 증거 → FAIL
   - "weak safe haven" + β >> 0 (예: β > 0.5, p < 0.01) → FAIL
   - "hedge" + 평균 상관계수 > 0.3 → WARN
   - 단일 이벤트만으로 "BTC는 X이다" 일반화 → WARN

   ```bash
   grep -nE "(strong|weak)\s*safe\s*haven|safe[-_]?haven" _review/*.md _review/results/*.csv 2>/dev/null
   ```

4. **3조건 일관 적용 점검**:
   - `_review/분석방식_전체.md`에서 ① CAR ≥ 0, ② 위기 시 상관계수, ③ β < 0 (분위) 모두 검토되었는지
   - `_review/results/btc_logic_ablation.csv`에서 7개 이벤트 모두 동일 조건 적용되었는지

5. **위기 정의 일관성**:
   - 위기 분위 q (보통 5%, 10%)가 사전에 명시되었는지
   - 결과 후 q를 변경한 흔적 (코드 주석에 "변경" "수정")

6. 항목별 판정:

   | 항목 | PASS | WARN | FAIL |
   |---|---|---|---|
   | 용어 사용 | 정의 일치 | 모호 | 정의 위반 |
   | 3조건 적용 | 7 이벤트 모두 | 일부 누락 | 단일 이벤트만 |
   | 위기 정의 | 사전 명시 + 일관 | 명시만 | 사후 변경 |
   | 결론 표현 | "증거 부족/지지" | "효과 없음" | "안전자산이다/아니다" 단정 |
   | Baur & Lucey 인용 | 명시 | 언급 | 부재 |

7. 보고서 + 한국어 요약. 인용: `Baur & Lucey (2010, Financial Review 45:217-229); Baur & McDermott (2010, JBF 34:1886-1898)`.

## 도구
Read, Bash + grep, Bash + head, Write.

## 중요
이 스킬이 FAIL 출력하면 학술 정직성 위반 가능성. 절대 무시하지 말 것.
