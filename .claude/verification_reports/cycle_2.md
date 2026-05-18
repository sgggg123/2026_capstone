# Verification Report — cycle 2

- 일자: 2026-05-18 03:14:54
- catalog: `.claude/references/catalog.json` (v1.2)
- 검증 방법론: 3개

## 요약

| 방법론 | 종합 | PASS | WARN | FAIL |
|---|---|---:|---:|---:|
| event_study | ⚠️ WARN | 5 | 3 | 0 |
| dcc_garch | ✅ PASS | 14 | 0 | 0 |
| quantile_reg | ⚠️ WARN | 6 | 2 | 0 |

## event_study — WARN

- **paper**: MacKinlay, A. C. (1997). Event Studies in Economics and Finance. Journal of Economic Literature, 35(1), 13-39.

### 소스 파일
- ✅ `Edit_mj/이벤트_스터디_v2.ipynb` — all cells ok

### 추출된 파라미터
- `est_window`: [('EST_START', '120'), ('EST_START', '120')]
- `event_window`: [('EVENT_WINDOW', '17'), ('EVENT_WINDOW', '3'), ('EVENT_WINDOW', '3')]
- `est_function`: ['get_estimation_data(', 'estimation_data', 'get_estimation_data(', 'estimation_data', 'estimation_data', 'estimation_data', 'estimation_data', 'estimation_data', 'estimation_data']
- `est_end`: [('EST_END', '26'), ('EST_END', '26')]
- `n_boot`: [('N_BOOT', '5000'), ('n_boot', '5000')]

### Red Flag 자동 판정
- ✅ **PASS** — Bootstrap 미사용 (t-test 단독)
  - pattern matched: bootstrap
- ⚠️ **WARN** — Placebo 검증 누락
  - missing patterns: ['placebo|pseudo[_\\s]event']
- ⚠️ **WARN** — 다중비교 보정 누락 (Bonferroni 또는 BH-FDR)
  - missing patterns: ['bonferroni|benjamini|hochberg|fdr|BH[-_]']
- ⚠️ **WARN** — est_window < 100 거래일
  - 추정창 길이 95일 (< 100)

### 결과 파일
- ✅ `Edit_mj/results/event_study_car.csv` — 31줄 (3878B)
- ✅ `Edit_mj/results/event_study_ar_timeseries.csv` — 211줄 (33467B)
- ✅ `Edit_mj/results/event_study_placebo.csv` — 7줄 (634B)

## dcc_garch — PASS

- **paper**: Engle, R. F. (2002). Dynamic Conditional Correlation: A Simple Class of Multivariate GARCH Models. Journal of Business & Economic Statistics, 20(3), 339-350.

### 소스 파일
- ✅ `GARCH/GARCH_분석_통합최종본.ipynb` — all cells ok

### 추출된 파라미터
- `alpha_beta_sum`: [('alpha', 'beta'), ('alpha', 'beta'), ('alpha', 'beta'), ('alpha', 'beta'), ('a', 'beta')]
- `garch_order`: [('1', '1'), ('1', '1'), ('1', '1'), ('1', '1'), ('1', '1')]
- `n_init`: None
- `omega_lower`: None

### Red Flag 자동 판정
- ✅ **PASS** — α + β >= 1 (비정상)
  - 모든 모델 α+β < 1 (max=0.9975)
- ✅ **PASS** — ADF 사전검증 미수행
  - pattern matched: adfuller|adf_test|ADF
- ✅ **PASS** — 잔차 진단(Ljung-Box) 미수행
  - pattern matched: ljung[_\s]?box|acorr_ljungbox
- ✅ **PASS** — 단일 초기값 MLE (지역 최솟값 위험)
  - pattern matched: multi[_\s]?init|n_init|n_starts|grid_search|격자
- ✅ **PASS** — seed 미고정 (재현 불가)
  - pattern matched: np\.random\.seed|random_state\s*=\s*[0-9]|RANDOM_SEED

### 결과 파일
- ✅ `Edit_mj/results/garch_model_comparison.csv` — 6줄 (580B)
- ✅ `Edit_mj/results/garch_gamma_results.csv` — 11줄 (1004B)
- ✅ `Edit_mj/results/garch_model_params.csv` — 36줄 (5475B)
- ✅ `Edit_mj/results/garch_conditional_volatility.csv` — 1822줄 (130534B)
- ✅ `Edit_mj/results/garch_event_dummy_comparison.csv` — 5줄 (574B)
- ✅ `Edit_mj/results/egarch_model_comparison.csv` — 9줄 (589B)
- ✅ `Edit_mj/results/egarch_exog_coefficients.csv` — 17줄 (1236B)
- ✅ `Edit_mj/results/garch_egarch_integrated_summary.csv` — 18줄 (1517B)

## quantile_reg — WARN

- **paper**: Koenker, R., & Bassett, G. (1978). Regression Quantiles. Econometrica, 46(1), 33-50.

### 소스 파일
- ✅ `Edit_mj/GPR_custom_analysis/master_data_generated/분위수_회귀.ipynb` — all cells ok

### 추출된 파라미터
- `tau`: [('TAUS', '0.01, 0.025, 0.05, 0.10, 0.20, 0.25, 0.50, 0.75, 0.90, 0.95'), ('CORE_TAUS', '0.05, 0.10, 0.50')]
- `n_boot`: None
- `tau_single`: None

### Red Flag 자동 판정
- ⚠️ **WARN** — τ < 0.05 또는 τ > 0.95 (꼬리 표본 부족)
  - τ 꼬리 표본 부족 위험: [0.01, 0.025]
- ✅ **PASS** — 표준오차가 OLS sandwich (분위회귀에 부적합)
  - pattern matched: HAC|newey[_\s]?west|hac_se|bootstrap
- ⚠️ **WARN** — 다중비교 보정 누락
  - missing patterns: ['bonferroni|benjamini|hochberg|fdr|BH[-_]']

### 결과 파일
- ✅ `Edit_mj/results/quantile_results.csv` — 421줄 (44789B)
- ✅ `Edit_mj/results/quantile_robust_iv.csv` — 21줄 (1755B)
- ✅ `Edit_mj/results/quantile_robust_loo.csv` — 13줄 (1446B)
- ✅ `Edit_mj/results/quantile_robust_mm.csv` — 21줄 (2112B)
