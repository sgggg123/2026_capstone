# 통합 검증 보고서: BTC 안전자산 가설 (Baur & Lucey 3조건)

- **일자**: 2026-05-11
- **기준**: Baur & Lucey (2010, Financial Review 45:217-229); Baur & McDermott (2010, JBF 34:1886-1898)
- **카탈로그**: `.claude/references/catalog.json#safe_haven`
- **목적**: 3개 방법론(이벤트 스터디 / DCC-GARCH / 분위회귀)의 결과를 Baur & Lucey 3조건 매트릭스로 통합. 6개 이벤트 각각에 대한 BTC 안전자산 라벨 자동 판정.

> ⚠️ **주의**: 본 보고서는 현재 `_review/results/*.csv`(일부 stale)와 catalog 기준의 추정값 기반. FAIL 4건 코드 수정 후 재실행해서 갱신 필요.

---

## Baur & Lucey (2010) 3조건 정의

| 조건 | 검정 | 안전자산 임계 | 우리 분석 출처 |
|---|---|---|---|
| ① **위기 시 CAR ≥ 0** | Event Study | CAR ≥ 0 (다중비교 보정 후 유의) | `event_study_summary_BTC_CAR.csv` |
| ② **위기 시 SP500 상관 ≤ 0** | DCC-GARCH | 위기창 평균 상관 ≤ 0 | `garch_*.csv`, `_review/results/` |
| ③ **극단 분위 β < 0** | Quantile Regression | β(τ=0.05) < 0, p < 0.05 | `Edit_mj/분위수_회귀.ipynb` |

**라벨 규칙**:
- 3조건 모두 충족 → **Strong Safe Haven**
- ①, ② 충족 + ③ ≈ 0 → **Weak Safe Haven**
- ② 충족 (조건부) → **Hedge** (평균 상관계수 검토 필요)
- ① 미충족 + ② 미충족 → **Risk Asset**
- ③ 단독 충족 → **Conditional Diversifier**

---

## 6개 이벤트 × 3조건 매트릭스 (현재 추정)

| 이벤트 | 날짜 | ① CAR | ② DCC 상관 | ③ β(τ=0.05) | 라벨 | 비고 |
|---|---|---|---|---|---|---|
| `soleimani` | 2020-01-03 | (재실행 필요) | (재실행 필요) | (계산 필요) | TBD | 추정창 95일 FAIL — Event Study 결과 신뢰성 영향 |
| `hormuz` | 2019-06-13 | (재실행 필요) | (재실행 필요) | (계산 필요) | TBD | 동일 |
| `russia_ukraine_war` | 2022-02-24 | (재실행 필요) | (재실행 필요) | (계산 필요) | TBD | 동일 |
| `israel_hamas_war` | 2023-10-07 | (재실행 필요) | (재실행 필요) | (계산 필요) | TBD | 동일 |
| `israel_iran_war` | 2024-04-01 | (재실행 필요) | (재실행 필요) | (계산 필요) | TBD | 동일 |
| `us_israel_iran_war` | 2026-02-28 | (재실행 필요) | (재실행 필요) | (계산 필요) | TBD | 표본 부족 가능 (이벤트 최근) |

> 숫자는 노트북 재실행 + `_review/scripts/02_event_study_sensitivity.py` 재실행 후 자동 채워짐.

---

## 통합 결과의 사전 조건 (현재 위반 사항)

3개 검증 보고서를 종합하면 통합 결론에 **선결 조치**가 필요:

### 이벤트 스터디 (FAIL 4건 — `2026-05-10_event_study.md`)
1. ❌ **추정창 95거래일** → 110일+ 확장 필요
2. ❌ **다중비교 보정 미적용** → Bonferroni α* = 0.05/30 = 0.00167 적용
3. ❌ **Placebo 검증 누락** → 셀 추가
4. ❌ **결과 csv stale** → 재실행

### DCC-GARCH (FAIL 2건 — `2026-05-11_dcc_garch.md`)
1. ❌ **seed 미고정** (민정최종, 한계점개선) → `np.random.seed(42)` 추가
2. ⚠ ADF / Ljung-Box 진단 추가 권장

### 분위회귀 (FAIL 1건 — `2026-05-11_quantile_reg.md`)
1. ❌ **seed 미고정** → 추가
2. ⚠ 표준오차 방법 명시 (bootstrap 권장)
3. ⚠ Bouri 2017 / Koenker & Bassett 1978 인용 추가

→ **총 7건 FAIL을 처리한 뒤** 위 매트릭스 자동 채워짐.

---

## 통합 검증의 학술적 가치

본 통합 매트릭스는 단일 방법론에 의존하지 않는 **삼각 검증(triangulation)**:

- 방법론 한 가지가 위반돼도 다른 두 가지로 결론 보정 가능
- Baur & Lucey 2010 §3에서 권장하는 **다중 증거 일관성 원칙** 직접 구현
- 6개 이벤트 모두에서 **일관된 패턴** 확인 시 일반화 정당성 확보 (Baur & McDermott 2010 절차)

---

## 시연 활용

`/verify-all` 실행 시 본 통합 보고서가 가장 마지막에 표시됨. Streamlit '🎓 학술 검증' 탭에서도 expander로 펼쳐 볼 수 있음.

**시연 멘트 예시**:
> "이벤트 스터디·GARCH·분위회귀 세 방법론 결과를 Baur & Lucey 2010 3조건으로 통합한 매트릭스입니다.
> 6개 이벤트별로 각 조건을 자동 매핑해서 최종 라벨이 결정되고, 어느 조건이라도 미충족이면
> 'Strong Safe Haven' 라벨이 자동으로 차단됩니다. 즉 학술 정의 위반은 시스템 단에서 원천 봉쇄됩니다."

---

## 다음 단계

1. 위 7건 FAIL 코드 수정
2. 노트북 재실행 → 결과 csv 갱신
3. 본 통합 보고서의 매트릭스 자동 채움
4. `/verify-safe-haven` 실행 → Baur & Lucey 정의 위반 자동 점검
5. 논문 부록에 본 보고서 + 3개 개별 보고서 첨부

## 인용

> Baur & Lucey (2010, Financial Review 45:217-229) safe-haven 표준 정의 (hedge / diversifier / weak / strong); Baur & McDermott (2010, JBF 34:1886-1898) 다국가 검증 절차

```bibtex
@article{baur2010gold,title={Is gold a hedge or a safe haven?},author={Baur, Dirk G and Lucey, Brian M},journal={Financial Review},volume={45},number={2},pages={217--229},year={2010}}
@article{baur2010mcdermott,title={Is gold a safe haven? International evidence},author={Baur, Dirk G and McDermott, Thomas K},journal={JBF},volume={34},number={8},pages={1886--1898},year={2010}}
```

상세 점검 항목: `.claude/references/safe_haven_framework.md`
