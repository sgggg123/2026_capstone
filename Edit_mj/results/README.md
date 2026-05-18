# Edit_mj/results — 3종 본분석 결과 통합 디렉토리

본 폴더는 이벤트 스터디·분위수 회귀·DCC/GARCH 3종 본분석의 **표준 산출 경로**다. 검증프로그램(`.claude/`)이 이 경로의 CSV를 자동으로 잡아 검증한다.

## 정본 입력 데이터

| 항목 | 경로 / 값 |
|---|---|
| 마스터 데이터 | `Edit_mj/GPR_custom_analysis/master_data_generated/master_data.csv` (1827행, 2019-01-02 ~ 2026-04-30) |
| 컬럼 | date, event_name, event_date, GPR_custom, F3_raw, GPR, GPR_zscore, N, mean_tone, BTC, Gold, TLT, DXY, SP500, NASDAQ, VIX, fear_greed, fg_label, fear_greed_lag1 |
| 구조 | 이벤트별 윈도우 + 일별 인덱싱 패널. 결측치 ffill은 이벤트 내에서만 적용(이벤트 간 오염 방지) |

## 이벤트 6종 (1827행 표기 기준)

| 이벤트명 | 행 수 | 기간 |
|---|---|---|
| hormuz_crisis | 182 | 2019-01-02 ~ 2019-09-20 |
| soleimani_assassination | 339 | 2019-09 ~ 2021-01 |
| russia_ukraine_war | 475 | 2021-01-29 ~ 2022-12-15 |
| israel_hamas_war | 260 | 2022-12-19 ~ 2024-01-02 |
| israel_iran | 299 | 2024-01-04 ~ 2025-03-14 |
| us_israel_iran | 272 | 2025-03-17 ~ 2026-04-30 |

## 표준 결과 파일 규격

| 방법론 | 산출 파일 | 컬럼 |
|---|---|---|
| 이벤트 스터디 | `event_study_car.csv` | event_name, window, CAR, t_stat, p_value, boot_p |
| 이벤트 스터디 (Placebo) | `event_study_placebo.csv` | event_name, placebo_window, CAR_placebo, p_value |
| 분위수 회귀 | `quantile_results.csv` | tau, asset, beta_GPR, se, p_value, beta_SP500 |
| DCC-GARCH | `dcc_results.csv` | model, omega, alpha, beta, a, b, loglik, AIC |
| DCC-GARCH (시계열) | `dcc_corr.csv` | date, event_name, rho_BTC_Gold, rho_BTC_SP500 |
| 통합 판정 | `final_judgment.csv` | event_name, method, baur_lucey_cond1, cond2, cond3, verdict |
| 최종 보고서 | `final_report.md` | (서술형) |

## 본분석 노트북 매핑

| 방법론 | 본분석 노트북 | 비고 |
|---|---|---|
| 이벤트 스터디 | `Edit_mj/이벤트_스터디_v2.ipynb` | 1827행 기준 재작업 (MacKinlay 추정창 + 이벤트창 표준) |
| 분위수 회귀 | `Edit_mj/GPR_custom_analysis/master_data_generated/분위수_회귀.ipynb` | 1827행 그대로 사용 |
| DCC/GARCH | `GARCH/GARCH_분석_통합최종본.ipynb` | Model1~5 + EGARCH 강건성 통합본 |
