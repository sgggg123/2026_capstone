---
name: verify-gpr-hybrid
description: Hybrid GPR(Caldara-Iacoviello 2022 + FinBERT + OECD PCA) 구성 검증. 순환논리, PCA 분산설명비, FinBERT 적합성 점검.
---

# verify-gpr-hybrid

본 프로젝트의 Hybrid GPR 지수가 Caldara-Iacoviello (2022) GPR + FinBERT 보강 + OECD (2008) PCA 합성 표준을 준수하는지 검증한다.

**가장 중요한 점검: 순환논리 배제**.

## 절차

1. catalog.json의 `gpr_hybrid` 섹션 로드.
2. `GPR_custom_analysis.ipynb` (또는 `Edit_mj/GPR_custom_analysis .ipynb`) 분석:
   - PCA 컴포넌트 수: `grep -oE "n_components\s*=\s*([0-9]+)"`
   - PCA 분산설명비: 출력에서 `explained_variance_ratio_` 검색
   - FinBERT 사용: `grep -E "finbert|FinBERT|ProsusAI"` 또는 노트북 셀 텍스트
   - 가중치 학습 데이터 명시: `grep -E "(train|fit|weight).*\b(window|range|period)\b"`

3. **순환논리 점검 (수동 권유)**:
   - EII 가중치 학습이 BTC 변동성을 목적함수로 사용하는지 검색: `grep -E "btc.*loss|btc.*objective|target.*btc"`
   - 학습 데이터 시점이 검증 데이터 시점과 분리되는지 코드 흐름 확인
   - 자동 검출 불가능하면 WARN + 수동 점검 항목 출력

4. `Edit_mj/master_data.csv` 컬럼 점검: `head -1`로 `GPR_custom`, `GPR`, `GPR_zscore`, `mean_tone` 모두 존재 확인.

5. 항목별 판정:

   | 항목 | PASS | WARN | FAIL |
   |---|---|---|---|
   | PCA 분산설명비 | ≥70% | 50~70% | <50% |
   | FinBERT 사용 | 사용 + 도메인 보정 | 사용만 | 일반 BERT 사용 |
   | 가중치 학습/적용 분리 | 코드에서 확인 | 수동 점검 필요 | 동일 데이터 사용 |
   | Caldara-Iacoviello 인용 | 명시 + GPR 지수 사용 | 언급 | 부재 |
   | 컬럼 무결성 | 모두 존재 | 일부 누락 | 핵심 누락 |

6. 보고서 저장 + 한국어 요약. 인용: `Caldara & Iacoviello (2022, AER 112:1194-1225); OECD (2008); Araci (2019) FinBERT`.

## 도구
Read, Bash + grep, Bash + head, Write.
