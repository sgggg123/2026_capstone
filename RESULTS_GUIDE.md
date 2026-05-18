# 결과 해석 가이드 — 비트코인 안전자산 가설 (Baur & Lucey 2010)

## 1. 검증 프레임워크

**Baur & Lucey (2010) Safe-Haven 3조건** — 본 프로젝트가 채택한 통합 판정 틀.

| 조건 | 방법론 | 통과 기준 | 산출 파일 |
|---|---|---|---|
| **C1** | 이벤트 스터디 (MacKinlay 1997) | 이벤트창 ±17일 BTC CAR ≥ 0 (음수+유의면 위험자산) | `event_study_car_bh.csv`, `event_study_placebo.csv` |
| **C2** | 분위수 회귀 (Koenker & Bassett 1978) | τ=0.05 극단 하락 시 SP500 β ≤ 0 (시장과 반대로) | `quantile_results_bh.csv` |
| **C3** | GARCH-X (Engle 2002) | 지정학 변수(GPR) γ 비유의 (변동성 증가 없음) | `garch_gamma_results.csv` |

**판정 규칙**: 3조건 모두 통과 → **Safe Haven**, 2/3 → Weak Haven, 1/3 → Diversifier, 0/3 → Risky Asset.

다중비교 보정은 **Benjamini-Hochberg FDR (1995)** α=0.05 — 6이벤트 동시 검정이라 단순 p-value 사용 시 1종 오류 누적.

## 2. 6개 지정학 이벤트별 최종 판정

| 이벤트 | C1 | C2 | C3 | 점수 | **판정** |
|---|---|---|---|---|---|
| 호르무즈 위기 (2019-06-13) | ✅ | ✅ | ✅ | 3/3 | **Safe Haven** |
| 솔레이마니 암살 (2020-01-03) | ✅ | ❌ | ✅ | 2/3 | Weak Haven |
| 러-우 전쟁 (2022-02-24) | ✅ | ❌ | ✅ | 2/3 | Weak Haven |
| 이스라엘-하마스 (2023-10-07) | ✅ | ❌ | ✅ | 2/3 | Weak Haven |
| 이스라엘-이란 충돌 (2024-04-01) | ✅ | ❌ | ✅ | 2/3 | Weak Haven |
| 미-이스라엘-이란 (2026-02-28) | ✅ | ❌ | ✅ | 2/3 | Weak Haven |

→ **공통 시사점**: BTC는 평균/변동성 관점에선 지정학 충격에 둔감(C1·C3 통과)하나, **극단 하락 시(τ=0.05) 시장과 동조**(C2 실패) → 부분적 위험자산 특성.

## 3. 방법론별 상세 해석

### 3-1. 이벤트 스터디 (C1)

- 추정창 [-120, -26] 95거래일 시장 모델 (BTC ~ SP500 OLS) → 정상 수익률 추정
- 이벤트창 [-17, +17] 35일 CAR 계산
- Bootstrap 5000회 + t-test (BMP)
- **6이벤트 모두 BTC CAR이 BH-FDR 보정 후 통계적 비유의** (즉 0과 구분 안 됨)
- **Placebo 검정** (가짜 이벤트일 200회): 5/6 이벤트 p > 0.05 → 실제 이벤트가 가짜와 구분 안 됨

→ 결론: 단기 평균 수익률 관점에서 BTC는 지정학 이벤트에 **둔감**. 안전자산 특성도 명확히 없고, 위험자산 특성도 명확히 없음.

### 3-2. 분위수 회귀 (C2)

- 모델: `Q_τ(BTC) = α + β·SP500_z + γ·GPR_custom_z`
- τ 격자: [0.01, 0.025, 0.05, 0.10, 0.20, 0.25, 0.50, 0.75, 0.90, 0.95] — 광역
- 핵심 τ: 0.05 (극단 하락), 0.10 (강한 하락), 0.50 (평상시 비교)
- 표준오차: HAC (Newey-West, bandwidth = 4·(n/100)^(2/9))

**전체 합산 결과 (1827행, τ=0.05):**
- SP500+GPR 모델: β(SP500) = +0.0178 (p < 0.001) → **유의한 양수 → ❌ Risky Asset (시장 동조)**
- Gold+GPR 모델: β(Gold) = +0.0060 (p < 0.001) → 금과도 동조

**이벤트별 (CORE_TAUS 기준 BH-FDR 보정):**
- 156건 중 24건 보정 후 유의
- 5개 이벤트에서 SP500 β 양수 유의 → 극단 하락 시 BTC도 함께 하락
- 호르무즈만 C2 통과 (관측 표본 부족도 영향)

→ 결론: BTC는 **극단 시장 하락(주식 하위 5%) 시 시장과 동조하며 같이 하락**. 진정한 의미의 Safe Haven은 아님.

### 3-3. GARCH-X (C3)

- 5개 모델 (외생변수 조합):
  - Model1: 공식 GPR_zscore
  - Model2: 커스텀 GPR_custom
  - Model3: VIX + Fear&Greed
  - Model4: 공식 GPR + 시장심리
  - Model5: 커스텀 GPR + 시장심리
- Student-t MLE 직접 최적화, multi-init 10개 격자, Richardson Hessian
- 정상성: 모든 모델 α+β < 1 (최대 0.9975) ✓
- ADF 사전검증: 7변수 모두 정상 ✓

**γ 계수 결과 (전체):**
- 공식 GPR: p = 0.96 → 비유의
- 커스텀 GPR: p = 0.73 → 비유의
- VIX: p = 0.80 → 비유의
- **Fear&Greed_lag1: p ≈ 0.03 → 유의 양수** (시장 탐욕 ↑ 시 BTC 변동성 ↑)

**모델 선택**: AIC 최소는 **Model3 (VIX + F&G)**. GPR 변수가 들어가도 AIC 거의 동일 → GPR의 한계 정보량 거의 없음.

**EGARCH 강건성**: 비대칭 변동성 구조에서도 GPR 비유의 결론 유지.

→ 결론: BTC 변동성은 **지정학(GPR)에 무관**하고 **시장 심리(F&G)에 반응**. 변동성 채널 관점에서 GPR이 BTC 위험과 무관하다는 점은 안전자산 가설을 약하게 지지(변동성 폭증 없음)하나, 정보가 없는 것이지 적극적 회피 자산은 아님.

## 4. 종합 결론

1. **BTC는 통계적으로 "디지털 금"이라는 명제를 입증하지 못함**
2. 평균/변동성 채널에선 지정학에 둔감 (이벤트 스터디 + GARCH 둘 다 비유의)
3. **분위수 채널에선 극단 하락 시 시장과 동조** → 위험자산 특성
4. 단 호르무즈 위기는 추정창 부족으로 단독 Safe Haven 판정 — 데이터 한계
5. 다중비교 보정 (BH-FDR) 후 단순 검정의 일부 유의 결과는 거의 사라짐 → 통계적 우연일 가능성

## 5. 한계점

- master_data 1827행은 6개 이벤트 윈도우 중심으로 구성된 패널 → 호르무즈(2019 이전 데이터 부족)에선 추정창 좌측 잘림
- Placebo 검정의 hormuz_crisis 실패는 4번 한계점의 직접 증거
- 분위수 회귀의 이벤트별 표본은 182~475일로 τ=0.01 등 극단 분위수에선 유효 표본 부족 (코드에 ⚠ 표시)
- COVID-19는 의도적으로 제외 (`.claude/references/catalog.json:_meta.scope_note` 참조)

## 6. 산출 파일 매핑 (catalog.json 기준)

| 항목 | 경로 |
|---|---|
| 통합 판정 | `Edit_mj/results/final_judgment.csv`, `final_report.md` |
| BH-FDR 통합 | `Edit_mj/results/multiple_testing_adjusted.csv` |
| 이벤트 스터디 | `event_study_car.csv`, `event_study_car_bh.csv`, `event_study_ar_timeseries.csv`, `event_study_placebo.csv` |
| 분위수 회귀 | `quantile_results.csv`, `quantile_results_bh.csv`, `quantile_robust_{iv,loo,mm}.csv` |
| GARCH 본 | `garch_model_comparison.csv`, `garch_gamma_results.csv`, `garch_model_params.csv`, `garch_event_dummy_comparison.csv`, `garch_conditional_volatility.csv` |
| EGARCH 강건 | `egarch_model_comparison.csv`, `egarch_exog_coefficients.csv`, `egarch_step_b3_coefficients_{long,wide}.csv` |
| GARCH/EGARCH 통합 | `garch_egarch_integrated_summary.csv` |
| ADF 사전검증 | `adf_test.csv` |
| 검증 보고서 | `.claude/verification_reports/cycle_{1,2,3}.md` |

## 7. 인용 (논문 작성용 BibTeX는 `.claude/citations/ready_to_paste.md` 참조)

- MacKinlay, A. C. (1997). Event Studies in Economics and Finance. *Journal of Economic Literature*, 35(1), 13-39.
- Koenker, R., & Bassett, G. (1978). Regression Quantiles. *Econometrica*, 46(1), 33-50.
- Engle, R. F. (2002). Dynamic Conditional Correlation. *JBES*, 20(3), 339-350.
- Baur, D. G., & Lucey, B. M. (2010). Is Gold a Hedge or a Safe Haven? *Financial Review*, 45(2), 217-229.
- Benjamini, Y., & Hochberg, Y. (1995). Controlling the False Discovery Rate. *JRSS B*, 57(1), 289-300.
- Caldara, D., & Iacoviello, M. (2022). Measuring Geopolitical Risk. *American Economic Review*, 112(4), 1194-1225.
- Bouri, E., Molnár, P., Azzi, G., Roubaud, D., & Hagfors, L. I. (2017). On the hedge and safe haven properties of Bitcoin. *Finance Research Letters*, 20, 192-198.
