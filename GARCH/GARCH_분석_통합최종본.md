# GARCH 분석 통합최종본 정리

분석 파일: `GARCH_분석_통합최종본.ipynb`  
사용 데이터: `master_data.csv`  
분석 표본: 1,821거래일  
정리 기준: GARCH-X 분석 + 이벤트 더미 강건성 검증 + EGARCH 강건성 검증

## 1. 통합본 전체 흐름

요약: 하나의 GARCH 분석 안에서 강건성 검증을 단계적으로 확장한 구조

| 단계 | 내용 | 역할 |
|---|---|---|
| Step 1~7 | GARCH-X 기본 분석 | 주 분석, Model1~Model5 비교 |
| Step 8 | 분산 처리 방식 강건성 | clip vs strict 결과 비교 |
| Step 9 | 이벤트 더미 강건성 검증 | 이벤트별 구조 차이 통제 가능성 확인 |
| Step 10 | EGARCH 강건성 검증 | 비대칭 변동성 구조에서도 결론 유지 여부 확인 |
| Step 11 | 시각화 | GARCH/EGARCH 결과 그래프화 |
| Step 12 | 결과 저장 | CSV/PNG 저장 |
| Step 13 | 최종 종합 결론 | 전체 분석 결론 하나로 정리 |

## 2. 기본 GARCH-X 모형

### 2.1 평균 방정식

```text
r(t) = mu + e(t)
```

### 2.2 분산 방정식

```text
h(t) = omega
     + alpha * e(t-1)^2
     + beta * h(t-1)
     + gamma * X(t-1)
```

| 변수 | 의미 |
|---|---|
| `h(t)` | t시점 BTC 조건부 분산 |
| `omega` | 기본 변동성 수준 |
| `alpha` | 전일 충격이 현재 변동성에 미치는 영향 |
| `beta` | 과거 변동성이 현재까지 이어지는 지속성 |
| `alpha+beta` | 변동성 충격의 지속 정도 |
| `gamma` | 외생변수 효과, 예: GPR, VIX, Fear&Greed |

## 3. GARCH-X 기본 분석 결과

### 3.1 모델 비교

| 순위 | 모델 | 설명 | AIC | BIC | LogLik | alpha+beta |
|---:|---|---|---:|---:|---:|---:|
| 1 | Model3 | VIX + Fear&Greed | 9578.710 | 9617.260 | -4782.355 | 0.9961 |
| 2 | Model4 | 공식 GPR + 시장심리 | 9580.390 | 9624.447 | -4782.195 | 0.9975 |
| 3 | Model5 | 커스텀 GPR + 시장심리 | 9580.417 | 9624.474 | -4782.208 | 0.9960 |
| 4 | Model2 | 커스텀 GPR 단독 | 9582.402 | 9615.445 | -4785.201 | 0.9937 |
| 5 | Model1 | 공식 GPR 단독 | 9582.517 | 9615.560 | -4785.259 | 0.9937 |

해석: GARCH-X 기본 분석에서는 `Model3: VIX + Fear&Greed`가 AIC 기준 최적, GPR 관련 변수를 추가한 Model4, Model5는 AIC 기준으로 Model3보다 개선되지 않음.

### 3.2 외생변수 gamma 결과

| 모델 | 변수 | gamma | p-value | 해석 |
|---|---|---:|---:|---|
| Model1 | GPR_zscore_scaled | -0.0045 | 0.9602 | 비유의 |
| Model2 | GPR_custom_scaled | 0.0263 | 0.7346 | 비유의 |
| Model3 | VIX_scaled | -0.0231 | 0.8007 | 비유의 |
| Model3 | fear_greed_lag1_scaled | 0.1573 | 0.0375 | 유의, 변동성 증가 |
| Model4 | GPR_zscore_scaled | 0.0440 | 0.5833 | 비유의 |
| Model4 | VIX_scaled | -0.0304 | 0.7315 | 비유의 |
| Model4 | fear_greed_lag1_scaled | 0.1667 | 0.0324 | 유의, 변동성 증가 |
| Model5 | GPR_custom_scaled | 0.0364 | 0.5962 | 비유의 |
| Model5 | VIX_scaled | -0.0247 | 0.7875 | 비유의 |
| Model5 | fear_greed_lag1_scaled | 0.1615 | 0.0339 | 유의, 변동성 증가 |

해석: `GPR_custom`은 단독 모형과 시장심리 통제 모형 모두에서 비유의, `Fear&Greed`는 Model3, Model4, Model5에서 반복적으로 유의

## 4. 한계점 수정 및 검증 결과

### 4.1 alpha/beta 및 t-stat 문제

`alpha` 하한을 `0.01`로 설정해 alpha 추정값이 0에 붙는 문제 완화

-> 실제 추정값은 주요 모델에서 약 `0.072~0.081` 수준으로 도출되어 0 경계 수렴 문제는 완화

기존 Hessian 기반 표준오차 계산에서 `alpha`, `beta`의 SE가 `0.0000`으로 계산되어 t-stat이 `N/A` 또는 비정상 출력되는 문제 완화

-> 추정값을 제약 없는 변환 파라미터 공간에서 Hessian을 계산하고, delta method로 원래 파라미터의 표준오차를 복원

```text
원 파라미터 직접 Hessian
→ 변환 파라미터 공간 Hessian
→ delta method로 원 파라미터 SE 복원
```

| 모델 | alpha SE | alpha t | beta SE | beta t |
|---|---:|---:|---:|---:|
| Model3 | 0.0187 | 3.890 | 0.0174 | 52.925 |
| Model5 | 0.0188 | 3.869 | 0.0175 | 52.708 |

해석: 기존의 `SE=0`, `N/A(경계)` 문제는 개선되었으나 beta t-stat이 여전히 큰 것은 수치 오류라기보다 `alpha+beta`가 1에 가까운 near-IGARCH 구조, 즉 BTC 변동성 지속성이 강하게 추정된 결과로 해석

### 4.2 omega 과적합 가능성

`omega=0`에 가까워지면 기본 변동성 없이 다른 항목만으로 변동성을 설명하려는 과적합 발생 가능

-> `omega` 하한을 `0.05`로 두고, 이 값이 과도한 제약인지 확인하기 위해 민감도 검정

| omega 하한 | Model3 AIC | omega 추정값 |
|---:|---:|---:|
| 0.0001 | 9578.710 | 0.3817 |
| 0.01 | 9578.710 | 0.3817 |
| 0.05 | 9578.710 | 0.3817 |

해석: omega 하한을 바꿔도 결과가 동일,`0.05` 하한은 결과를 왜곡하는 강한 제약이 아님.

### 4.3 Hessian 수치 미분 오차

Hessian: 로그우도 함수가 최적점 주변에서 얼마나 휘어져 있는지를 나타내는 2차 미분 행렬 

GARCH-X에서는 Hessian의 역행렬을 이용해 표준오차를 계산

```text
Covariance matrix ≈ inverse(Hessian)
SE = sqrt(diagonal of Covariance matrix)
t-stat = estimate / SE
p-value = t-stat 기반 계산
```

기존에도`numdifftools Richardson`은 적용되었으나 bounds가 있는 원 파라미터 공간에서 Hessian을 직접 계산해 alpha/beta SE가 불안정

-> 변환 파라미터 Hessian + delta method로 SE를 복원하여 수치적 안정성을 개선

### 4.4 국소최적해 가능성

GARCH MLE는 초기값에 따라 다른 해에 수렴할 수 있으므로, 전체 모델에 대해 다중 초기값 10개를 적용

```text
alpha 초기값: 0.05, 0.08, 0.10, 0.15, 0.20
beta 초기값 : 0.80, 0.90
총 10개 초기값
```

각 모델을 10개 초기값으로 반복 추정한 뒤 최저 AIC 결과를 채택, 변환 파라미터 방식에서도 기존 결과와 동일한 최적해가 나와 국소최적해 문제는 완화된 것으로 판단

## 5. 이벤트 더미 강건성 검증

이벤트 더미: 이벤트별 구조 차이를 통제했을 때도 결론이 크게 달라지는지 확인하기 위한 강건성 검증

기준 이벤트는 `hormuz_crisis`, 나머지 이벤트를 0/1 더미로 추가

```text
h(t) = omega
     + alpha * e(t-1)^2
     + beta * h(t-1)
     + gamma1 * VIX(t-1)
     + gamma2 * FearGreed(t-1)
     + delta1 * event_israel_hamas_war(t-1)
     + delta2 * event_israel_iran(t-1)
     + delta3 * event_russia_ukraine_war(t-1)
     + delta4 * event_soleimani_assassination(t-1)
     + delta5 * event_us_israel_iran(t-1)
```

| 모델 | AIC | BIC | LogLik | alpha+beta | 해석 |
|---|---:|---:|---:|---:|---|
| Model3_eventD | 9569.545 | 9635.631 | -4772.773 | 0.9852 | 이벤트 더미 포함 최저 AIC |
| Model5_eventD | 9571.418 | 9643.011 | -4772.709 | 0.9853 | GPR_custom 포함 이벤트 더미 |
| 기존 Model3 | 9578.710 | 9617.260 | -4782.355 | 0.9961 | 기본 주모형 |
| 기존 Model5 | 9580.417 | 9624.474 | -4782.208 | 0.9960 | GPR_custom 포함 기본 모형 |

해석: 이벤트 더미를 추가하면 AIC는 개선되지만 BIC는 악화, 따라서 이벤트 더미 모델은 주모형 대체가 아니라, 이벤트별 구조 차이를 보완했을 때도 결론이 크게 달라지지 않는지 확인하는 강건성 검증으로 해석

## 6. EGARCH 강건성 검증

EGARCH: 비대칭 변동성 구조를 고려해도 GARCH-X의 핵심 결론이 유지되는지 확인하기 위한 강건성 검증

### 6.1 EGARCH-X 분산식

```text
ln h(t) = omega
        + beta * ln h(t-1)
        + alpha * (|z(t-1)| - E|z|)
        + gamma_asym * z(t-1)
        + delta * X(t-1)
```

| 파라미터 | 의미 |
|---|---|
| `alpha` | 충격 크기 효과 |
| `gamma_asym` | 비대칭 효과, 음수면 하락 충격이 변동성을 더 크게 키움 |
| `beta` | log variance 지속성 |
| `delta` | 외생변수 효과, GPR/VIX/Fear&Greed |

### 6.2 EGARCH 모델 비교

| 순위 | 모델 | 설명 | AIC | BIC | LogLik |
|---:|---|---|---:|---:|---:|
| 1 | EGARCH_E3 | VIX + Fear&Greed | 9559.119 | 9603.176 | -4771.559 |
| 2 | EGARCH_E6 | GPR 더미 + VIX + Fear&Greed | 9560.037 | 9609.601 | -4771.018 |
| 3 | EGARCH_E5 | ΔGPR + VIX + Fear&Greed | 9560.607 | 9610.171 | -4771.303 |
| 4 | EGARCH_E4 | GPR_custom + VIX + Fear&Greed | 9560.756 | 9610.320 | -4771.378 |
| 5 | EGARCH_E2 | GPR_zscore 단독 | 9565.077 | 9603.627 | -4775.538 |
| 6 | EGARCH_E1 | GPR_custom 단독 | 9565.481 | 9604.031 | -4775.740 |
| 참고 | GARCH_M3 | GARCH 기준 VIX + Fear&Greed | 9578.710 | 9617.260 | -4782.355 |
| 참고 | GARCH_M2 | GARCH 기준 GPR_custom | 9582.402 | 9615.445 | -4785.201 |

해석: EGARCH 내 최저 AIC 참고 모델은 `EGARCH_E3: VIX + Fear&Greed`, 따라서 EGARCH 구조에서도 GPR_custom보다 Fear&Greed 중심 결론이 유지된다는 보조 근거로 해석

### 6.3 EGARCH 외생변수 p-value

| 모델 | 변수 | 계수 | p-value | 해석 |
|---|---|---:|---:|---|
| EGARCH_E1 | GPR_custom_scaled | 0.0003 | 0.9570 | 비유의 |
| EGARCH_E2 | GPR_zscore_scaled | -0.0033 | 0.5316 | 비유의 |
| EGARCH_E3 | VIX_scaled | -0.0004 | 0.9342 | 비유의 |
| EGARCH_E3 | fear_greed_lag1_scaled | 0.0134 | 0.0193 | 유의, 변동성 증가 |
| EGARCH_E4 | GPR_custom_scaled | 0.0030 | 0.5485 | 비유의 |
| EGARCH_E4 | fear_greed_lag1_scaled | 0.0141 | 0.0168 | 유의, 변동성 증가 |
| EGARCH_E5 | GPR_custom_diff_scaled | 0.0284 | 0.4729 | 비유의 |
| EGARCH_E5 | fear_greed_lag1_scaled | 0.0136 | 0.0165 | 유의, 변동성 증가 |
| EGARCH_E6 | GPR_custom_high | 0.0128 | 0.3025 | 비유의 |
| EGARCH_E6 | fear_greed_lag1_scaled | 0.0144 | 0.0144 | 유의, 변동성 증가 |

해석: EGARCH에서도 GPR 관련 변수는 모두 비유의, 반면 `Fear&Greed`는 EGARCH_E3, E4, E5, E6에서 반복적으로 유의. 따라서 EGARCH 강건성 검증에서도 GARCH-X의 핵심 결론은 유지

### 6.4 EGARCH 비대칭 효과

EGARCH의 `gamma_asym`은 모든 EGARCH 모델에서 비유의

| 모델 | gamma_asym | p-value | 해석 |
|---|---:|---:|---|
| EGARCH_E1 | 0.0047 | 0.7969 | 비유의 |
| EGARCH_E2 | 0.0032 | 0.8643 | 비유의 |
| EGARCH_E3 | -0.0171 | 0.3953 | 비유의 |
| EGARCH_E4 | -0.0183 | 0.3651 | 비유의 |
| EGARCH_E5 | -0.0176 | 0.3797 | 비유의 |
| EGARCH_E6 | -0.0188 | 0.3524 | 비유의 |

해석: 레버리지 효과는 뚜렷하게 유의하지 않음, 따라서 EGARCH는 비대칭 효과 자체를 강하게 입증하기보다는, 비대칭 구조를 허용해도 GPR_custom 비유의 및 Fear&Greed 유의 결론이 유지된다는 강건성 검증우로 해석

## 7. 최종 결론

### 7.1 최종 해석 요약

| 항목 | 최종 판단 |
|---|---|
| 주 분석 기준 | GARCH-X |
| GARCH-X 최적 모델 | Model3, VIX + Fear&Greed |
| GPR_custom 효과 | GARCH/EGARCH 모두 비유의 |
| Fear&Greed 효과 | GARCH/EGARCH 모두 반복적으로 유의 |
| 이벤트 더미 | AIC 개선, BIC 악화 → 강건성 검증 |
| EGARCH | 주모형 대체가 아니라 비대칭 변동성 강건성 검증 |

최종적으로 지정학적 리스크 자체를 나타내는 `GPR_custom`은 BTC 변동성에 대한 독립적 설명력을 확보하지 못했지만 시장 심리 변수인 `Fear&Greed`는 GARCH-X와 EGARCH-X 모두에서 반복적으로 유의하게 나타나 BTC 변동성 설명에 더 안정적인 변수로 판단

### 7.2 최종 한계

| 한계 | 해석 |
|---|---|
| near-IGARCH 구조 | alpha+beta가 1에 가까워 BTC 변동성 지속성이 매우 강하게 추정됨 |
| 이벤트 중심 표본 설계의 trade-off | 지정학 이벤트에 집중하는 대신, 이벤트 간 시계열 연속성은 약화됨 |
| GPR_custom 독립 효과 비유의 | GARCH-X와 EGARCH-X 모두에서 GPR_custom의 독립적 유의성 확보 실패 |

## 8. 생성 파일 설명

| 파일 | 내용 |
|---|---|
| `GARCH_분석_통합최종본.ipynb` | 최종 통합 노트북 |
| `garch_model_comparison.csv` | GARCH 모델별 AIC/BIC/LogLik 비교 |
| `garch_gamma_results.csv` | GARCH 외생변수 gamma 및 p-value 요약 |
| `garch_model_params.csv` | GARCH 전체 파라미터 상세 |
| `garch_event_dummy_comparison.csv` | 이벤트 더미 강건성 검증 결과 |
| `egarch_model_comparison.csv` | EGARCH 강건성 검증 모델 비교 |
| `egarch_exog_coefficients.csv` | EGARCH 외생변수 계수 및 p-value |
| `egarch_step_b3_coefficients_long.csv` | Step 10-3 추정 계수 long format |
| `egarch_step_b3_coefficients_wide.csv` | Step 10-3 추정 계수 wide format |
| `garch_egarch_integrated_summary.csv` | GARCH, 이벤트 더미, EGARCH 통합 요약 |
| `garch_limit_diagnostics.py` | 한계점 수정 가능성 진단용 보조 스크립트 |
| `garch_transformed_se.py` | 변환 파라미터 Hessian + delta method 검증용 스크립트 |
| `garch_gamma_partial_bootstrap.py` | GPR_custom gamma 비유의성의 강건성 확인용 부트스트랩 스크립트 |
