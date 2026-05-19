"""
02_event_study_sensitivity.py — Event Study 윈도우 sensitivity 분석

수정 사항:
1) [C1] EVENT_WINDOW = [3, 5, 10, 17] 4개 값으로 동일 분석 반복
   - 팀원 원본은 ±17 → ±3 으로 일방 축소. 본 스크립트는 4개 윈도우 비교 표 산출.
   - 가장 안정적인 윈도우 식별 + 결과 robustness 검증.
2) 모델 사양은 팀원 v4 유지: BTC=MM(NASDAQ), Gold/DXY=CMRM, TLT/NASDAQ=MM(SP500)
3) 검정: BMP(SAR) + Circular Block Bootstrap (block=5, n_boot=5000)

입력:  Edit_mj/master_data.csv, Edit_mj/returns.csv
출력:  _review/results/event_study_sensitivity.csv  (이벤트×자산×윈도우)
       _review/results/event_study_summary.csv     (윈도우별 BTC 결론 요약)
"""

import os, warnings
warnings.filterwarnings('ignore')

import numpy as np
import pandas as pd
from scipy import stats
from statsmodels.regression.linear_model import OLS
from statsmodels.tools import add_constant

REPO = '/mnt/d/project/2026_capstone'
OUT  = f'{REPO}/_review/results'
os.makedirs(OUT, exist_ok=True)

# ============================================================
# 1. 데이터 로드
# ============================================================
print('=' * 70)
print('Event Study 윈도우 sensitivity 분석')
print('=' * 70)

master = pd.read_csv(f'{REPO}/Edit_mj/master_data.csv')
master['date'] = pd.to_datetime(master['date'])
ret_all = pd.read_csv(f'{REPO}/Edit_mj/returns.csv')
ret_all['date'] = pd.to_datetime(ret_all['date'])

EVENT_DATES = {
    'hormuz'          : '2019-06-13',
    'soleimani': '2020-01-03',
    'russia_ukraine_war': '2022-02-24',
    'israel_hamas_war'           : '2023-10-07',
    'israel_iran_war'            : '2024-04-01',
    'us_israel_iran_war'         : '2026-02-28',
}
EVENT_LABELS = {
    'hormuz'          : '호르무즈 위기',
    'soleimani': '솔레이마니 암살',
    'russia_ukraine_war': '러-우 전쟁',
    'israel_hamas_war'           : '이스라엘-하마스',
    'israel_iran_war'            : '이스라엘-이란 충돌',
    'us_israel_iran_war'         : '미-이스라엘-이란',
}
ASSETS = ['BTC', 'Gold', 'TLT', 'DXY', 'NASDAQ']
ASSET_BENCHMARKS = {'BTC': 'NASDAQ', 'Gold': 'SP500', 'TLT': 'SP500', 'DXY': 'SP500', 'NASDAQ': 'SP500'}
CMRM_ASSETS = ['Gold', 'DXY']

EST_START = -120
EST_END   = -26

# ============================================================
# 2. 정상 수익률 추정 + AR 산출
# ============================================================
def estimate_normal_return(est_df, asset):
    if asset not in est_df.columns:
        return None
    y = est_df[asset].dropna()
    if asset in CMRM_ASSETS:
        return {'model': 'CMRM', 'mu': y.mean(), 'alpha': 0, 'beta': 0,
                'sigma': y.std(), 'n': len(y)}
    market = ASSET_BENCHMARKS[asset]
    if market not in est_df.columns:
        return None
    combined = pd.concat([y, est_df[market]], axis=1).dropna()
    if len(combined) < 20:
        return None
    y_sync = combined.iloc[:, 0]
    X_sync = add_constant(combined.iloc[:, 1])
    res = OLS(y_sync, X_sync).fit()
    return {
        'model': f'MM({market})',
        'alpha': res.params.iloc[0],
        'beta' : res.params.iloc[1],
        'sigma': float(np.sqrt(res.mse_resid)),
        'r2'   : res.rsquared,
        'n'    : len(y_sync),
    }

def normal_return_t(row_dict, params):
    if params['model'] == 'CMRM':
        return params['mu']
    market = params['model'][3:-1]
    r_mkt = row_dict.get(market)
    if r_mkt is None or pd.isna(r_mkt):
        return np.nan
    return params['alpha'] + params['beta'] * r_mkt

def get_estimation_data(event_date_str, returns_df):
    ed = pd.Timestamp(event_date_str)
    idx = returns_df[returns_df['date'] >= ed].index
    if len(idx) == 0:
        return pd.DataFrame()
    ei = idx[0]
    s = max(0, ei + EST_START)
    e = max(0, ei + EST_END)
    if s > e:
        return pd.DataFrame()
    return returns_df.iloc[s:e+1].copy()

# 추정기간 데이터 + 모델 미리 계산 (윈도우 무관)
print('\n▶ 추정기간 모델 적합 (이벤트별)')
estimation_data = {}
models_per_event = {}
for ev, dt in EVENT_DATES.items():
    est = get_estimation_data(dt, ret_all)
    estimation_data[ev] = est
    models_per_event[ev] = {}
    for asset in ASSETS:
        models_per_event[ev][asset] = estimate_normal_return(est, asset)
    n = len(est)
    print(f'  {ev:<28} 추정기간 {n}일')

# ============================================================
# 3. 검정 함수 (BMP + Block Bootstrap)
# ============================================================
def ttest_car_bmp(ar_series, est_ar_series):
    ar = ar_series.dropna()
    est_ar = est_ar_series.dropna()
    T = len(ar)
    if T < 3 or len(est_ar) < 10:
        return np.nan, np.nan, np.nan
    sigma_est = est_ar.std()
    if sigma_est == 0:
        return float(ar.sum()), 0, 1.0
    sar = ar / sigma_est
    sar_mean, sar_std = sar.mean(), sar.std()
    if sar_std == 0:
        return float(ar.sum()), 0, 1.0
    t_stat = sar_mean / (sar_std / np.sqrt(T))
    p_val = (1 - stats.t.cdf(np.abs(t_stat), df=T-1)) * 2
    return float(ar.sum()), float(t_stat), float(p_val)

def bootstrap_block_car(ar_series, est_ar_series, n_boot=5000, block_size=5, seed=42):
    rng = np.random.default_rng(seed)
    ar = ar_series.dropna().values
    est = est_ar_series.dropna().values
    T = len(ar)
    if T < 3 or len(est) < T:
        return np.nan
    actual = ar.sum()
    boot_cars = []
    n_blocks = T // block_size + 1
    for _ in range(n_boot):
        sampled = []
        for _ in range(n_blocks):
            start = rng.integers(0, len(est))
            block = [est[(start + i) % len(est)] for i in range(block_size)]
            sampled.extend(block)
        sampled = sampled[:T]
        boot_cars.append(np.sum(sampled))
    boot_cars = np.array(boot_cars)
    p = np.mean(np.abs(boot_cars - boot_cars.mean()) >= np.abs(actual - boot_cars.mean()))
    return float(p)

# ============================================================
# 4. 윈도우별 분석 루프
# ============================================================
WINDOWS = [3, 5, 10, 17]

results_rows = []
for window in WINDOWS:
    print(f'\n{"="*70}\n▶ EVENT_WINDOW = ±{window} 거래일\n{"="*70}')
    for ev, dt in EVENT_DATES.items():
        ev_ts = pd.Timestamp(dt)
        sub = master[master['event_name'] == ev].sort_values('date').copy()
        # 이벤트 ±window 거래일
        ev_idx = sub[sub['date'] >= ev_ts].index
        if len(ev_idx) == 0:
            continue
        center = sub.index.get_loc(ev_idx[0])
        s = max(0, center - window)
        e = min(len(sub), center + window + 1)
        win = sub.iloc[s:e].copy()
        win['day_offset'] = range(s - center, e - center)

        for asset in ASSETS:
            params = models_per_event[ev].get(asset)
            if params is None:
                continue
            # AR 계산
            ar = []
            for _, row in win.iterrows():
                exp = normal_return_t(row.to_dict(), params)
                if pd.isna(exp) or pd.isna(row[asset]):
                    ar.append(np.nan)
                else:
                    ar.append(row[asset] - exp)
            ar = pd.Series(ar)

            # 추정기간 AR (검정용)
            est = estimation_data[ev]
            est_normal = est.apply(lambda r: normal_return_t(r.to_dict(), params), axis=1)
            est_ar = est[asset] - est_normal

            car, t_bmp, p_bmp = ttest_car_bmp(ar, est_ar)
            p_block = bootstrap_block_car(ar, est_ar, n_boot=5000, block_size=5, seed=42)

            # 분류
            sig5 = (p_bmp < 0.05) and (p_block < 0.05)
            if sig5 and car > 0:
                label = 'Safe Haven'
            elif sig5 and car < 0:
                label = 'Risky Asset'
            elif (p_bmp < 0.10 or p_block < 0.10):
                label = 'Marginal'
            else:
                label = 'Non-Sig'

            results_rows.append({
                'window'  : window,
                'event'   : ev,
                'event_label': EVENT_LABELS[ev],
                'asset'   : asset,
                'model'   : params['model'],
                'CAR'     : round(car, 4),
                'p_BMP'   : round(p_bmp, 4),
                'p_block' : round(p_block, 4),
                'label'   : label,
            })

        # BTC 결과만 한 줄로 출력
        btc = next((r for r in results_rows
                    if r['window']==window and r['event']==ev and r['asset']=='BTC'), None)
        if btc:
            print(f'  {EVENT_LABELS[ev]:<14}  BTC  CAR={btc["CAR"]:+.4f}  p_BMP={btc["p_BMP"]:.4f}  '
                  f'p_block={btc["p_block"]:.4f}  → {btc["label"]}')

# ============================================================
# 5. 결과 저장
# ============================================================
df = pd.DataFrame(results_rows)
df.to_csv(f'{OUT}/event_study_sensitivity.csv', index=False, encoding='utf-8-sig')
print(f'\n저장: event_study_sensitivity.csv  ({len(df)}행)')

# 윈도우별 BTC 만 요약
btc = df[df['asset']=='BTC'].copy()
summary = btc.pivot_table(index='event_label', columns='window',
                          values='CAR', aggfunc='first').round(4)
summary.to_csv(f'{OUT}/event_study_summary_BTC_CAR.csv', encoding='utf-8-sig')

label_summary = btc.pivot_table(index='event_label', columns='window',
                                 values='label', aggfunc='first')
label_summary.to_csv(f'{OUT}/event_study_summary_BTC_label.csv', encoding='utf-8-sig')

print('\n▶ BTC CAR 윈도우별 요약 (양수면 상승, 음수면 하락)')
print(summary.to_string())
print('\n▶ BTC 분류 윈도우별 요약')
print(label_summary.to_string())

# ============================================================
# 6. Robustness 메시지
# ============================================================
print('\n' + '=' * 70)
print('▶ Robustness 진단 (윈도우 변경 시 결론 안정성)')
print('=' * 70)
for ev in EVENT_DATES:
    sub = btc[btc['event']==ev].sort_values('window')
    if len(sub) < 4:
        continue
    labels = sub['label'].tolist()
    cars = sub['CAR'].tolist()
    sign_changes = sum(1 for i in range(1,len(cars)) if np.sign(cars[i]) != np.sign(cars[i-1]))
    label_unique = len(set(labels))
    stability = '✅ 안정' if (sign_changes==0 and label_unique<=2) else '⚠️ 불안정'
    print(f'  {EVENT_LABELS[ev]:<14}  CAR 부호 전환={sign_changes}  분류 고유={label_unique}/{len(labels)}  {stability}')
    print(f'    CARs: {cars}  Labels: {labels}')

print('\n✅ 02_event_study_sensitivity.py 완료')
