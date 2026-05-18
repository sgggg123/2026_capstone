# 방법론 인덱스

이 프로젝트에서 사용된 모든 통계 방법론과 학술 표준 레퍼런스 매핑. 단일 truth source는 [`catalog.json`](catalog.json).

| 방법론 | 표준 논문 | 본 프로젝트 구현 | 검증 스킬 | 상세 문서 |
|---|---|---|---|---|
| Event Study | MacKinlay (1997) JEL 35:13-39 | `Edit_mj/이벤트_스터디_v2.ipynb`, `_review/scripts/02_event_study_sensitivity.py` | `/verify-event-study` | [event_study.md](event_study.md) |
| DCC-GARCH | Engle (2002) JBES 20:339-350; Aielli (2013) | `Edit_mj/GARCH_분석.ipynb`, `_review/scripts/01_garch_fixed.py` | `/verify-dcc-garch` | [dcc_garch.md](dcc_garch.md) |
| Quantile Regression | Koenker & Bassett (1978) Econometrica 46:33-50; Bouri (2017) FRL 23:87-95 | `Edit_mj/분위수_회귀.ipynb` | `/verify-quantile-reg` | [quantile_reg.md](quantile_reg.md) |
| Hybrid GPR | Caldara & Iacoviello (2022) AER 112:1194-1225; OECD (2008); Araci (2019) FinBERT | `GPR_custom_analysis.ipynb`, `Edit_mj/master_data.csv` | `/verify-gpr-hybrid` | [hybrid_gpr.md](hybrid_gpr.md) |
| Stationary Bootstrap | Politis & Romano (1994) JASA 89:1303-1313 | 위 노트북 내 bootstrap 셀 | `/verify-bootstrap` | [bootstrap.md](bootstrap.md) |
| Multiple Testing | Benjamini & Hochberg (1995) JRSSB 57:289-300; Bonferroni (1936) | `Edit_mj/이벤트_스터디_v2.ipynb`, `_review/scripts/02_*` | `/verify-multiple-testing` | [multiple_testing.md](multiple_testing.md) |
| Safe-Haven Framework | Baur & Lucey (2010) Financial Review 45:217-229; Baur & McDermott (2010) JBF 34:1886-1898 | `_review/분석방식_전체.md`, `_review/results/btc_logic_ablation.csv` | `/verify-safe-haven` | [safe_haven_framework.md](safe_haven_framework.md) |

## 사용 흐름

1. 분석 진행 중 또는 완료 후 `/verify-all` 실행
2. 각 방법론별 PASS/WARN/FAIL 결과 확인
3. WARN/FAIL 항목은 해당 상세 문서의 "함정" 섹션 참고
4. 결론 진술 시 `/cite-method <name>`으로 인용 첨부

## 통일 이벤트 키 (6개)
`soleimani`, `hormuz`, `russia_ukraine_war`, `israel_hamas_war`, `israel_iran_war`, `us_israel_iran_war`

> COVID-19는 분석 범위 의도적 제외 (지정학 이벤트 아님).
