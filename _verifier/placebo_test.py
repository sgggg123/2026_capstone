"""Placebo Test — 이벤트 스터디 강건성 (catalog red_flag 대응).

각 실제 이벤트일을 임의 K개 가짜 일자로 이동해 CAR 분포를 만들고,
실제 CAR이 가짜 분포 어디에 있는지 percentile + bootstrap p-value 산출.

가짜 일자 선정: 실제 이벤트일 ±N(=120) 거래일 범위 밖, returns.csv 데이터 가용 일자 중 무작위 K(=200)개.

산출: Edit_mj/results/event_study_placebo.csv
컬럼: event_name, real_CAR, placebo_mean_CAR, placebo_std_CAR, percentile_of_real, placebo_p, n_placebo
"""
import sys
from pathlib import Path
import pandas as pd
import numpy as np
from statsmodels.regression.linear_model import OLS
from statsmodels.tools import add_constant

ROOT = Path(__file__).resolve().parent.parent
RESULTS = ROOT / 'Edit_mj' / 'results'
MASTER  = ROOT / 'Edit_mj' / 'GPR_custom_analysis' / 'master_data_generated' / 'master_data.csv'
RETURNS = ROOT / 'Edit_mj' / 'GPR_custom_analysis' / 'master_data_generated' / 'returns.csv'

EVENT_DATES = {
    'hormuz_crisis'          : '2019-06-13',
    'soleimani_assassination': '2020-01-03',
    'russia_ukraine_war'     : '2022-02-24',
    'israel_hamas_war'       : '2023-10-07',
    'israel_iran'            : '2024-04-01',
    'us_israel_iran'         : '2026-02-28',
}
ASSET = 'BTC'        # Safe-Haven 핵심
MARKET = 'SP500'
EST_START = -120     # 추정창 시작 (이벤트 전 거래일)
EST_END   = -26
EVENT_WINDOW = 17    # ±17 거래일 이벤트창
K_PLACEBO = 200      # placebo 가짜 일자 수
BUFFER    = 120      # 실제 이벤트일 ±BUFFER 거래일은 placebo에서 제외
RNG_SEED  = 42


def trading_day_offset(dates: pd.Series, anchor: pd.Timestamp, offset: int) -> pd.Timestamp:
    """anchor 일자에서 거래일 기준 offset만큼 이동한 일자 반환 (없으면 NaT)."""
    sorted_dates = dates.sort_values().reset_index(drop=True)
    pos = sorted_dates.searchsorted(anchor)
    if pos >= len(sorted_dates):
        pos = len(sorted_dates) - 1
    if sorted_dates.iloc[pos] != anchor:
        # anchor가 거래일 아니면 가장 가까운 다음 거래일 인덱스
        pos = max(0, min(pos, len(sorted_dates)-1))
    new_pos = pos + offset
    if new_pos < 0 or new_pos >= len(sorted_dates):
        return pd.NaT
    return sorted_dates.iloc[new_pos]


def compute_car(ret_df: pd.DataFrame, anchor: pd.Timestamp,
                asset: str, market: str,
                est_start: int, est_end: int, evt_win: int) -> float | None:
    """주어진 anchor 일자 기준 CAR을 시장 모델(OLS)로 계산."""
    dates = ret_df['date']
    est_start_d = trading_day_offset(dates, anchor, est_start)
    est_end_d   = trading_day_offset(dates, anchor, est_end)
    evt_start_d = trading_day_offset(dates, anchor, -evt_win)
    evt_end_d   = trading_day_offset(dates, anchor, evt_win)
    if pd.isna(est_start_d) or pd.isna(est_end_d) or pd.isna(evt_start_d) or pd.isna(evt_end_d):
        return None

    est = ret_df[(ret_df['date'] >= est_start_d) & (ret_df['date'] <= est_end_d)].dropna(subset=[asset, market])
    evt = ret_df[(ret_df['date'] >= evt_start_d) & (ret_df['date'] <= evt_end_d)].dropna(subset=[asset, market])
    if len(est) < 30 or len(evt) < (evt_win + 1):
        return None
    try:
        X = add_constant(est[market].values)
        y = est[asset].values
        model = OLS(y, X).fit()
        a, b = model.params
        expected = a + b * evt[market].values
        ar = evt[asset].values - expected
        return float(np.sum(ar))
    except Exception:
        return None


def main():
    rng = np.random.default_rng(RNG_SEED)
    if not RETURNS.exists():
        print(f'❌ {RETURNS} 없음'); return 1
    ret = pd.read_csv(RETURNS)
    ret.columns = [c.strip() for c in ret.columns]
    if 'Date' in ret.columns:
        ret = ret.rename(columns={'Date':'date'})
    ret['date'] = pd.to_datetime(ret['date'])
    for c in [ASSET, MARKET]:
        if c in ret.columns:
            ret[c] = pd.to_numeric(ret[c], errors='coerce')
    ret = ret.dropna(subset=[ASSET, MARKET]).sort_values('date').reset_index(drop=True)
    all_dates = ret['date']
    print(f'✓ returns: {len(ret)}행 ({all_dates.min().date()} ~ {all_dates.max().date()})')

    rows = []
    for event, ed in EVENT_DATES.items():
        anchor_real = pd.Timestamp(ed)
        real_car = compute_car(ret, anchor_real, ASSET, MARKET, EST_START, EST_END, EVENT_WINDOW)
        if real_car is None:
            print(f'⚠️ {event}: real CAR 계산 실패 (데이터 부족)')
            rows.append({'event_name': event, 'real_CAR': None, 'placebo_mean_CAR': None,
                         'placebo_std_CAR': None, 'percentile_of_real': None,
                         'placebo_p': None, 'n_placebo': 0})
            continue

        # 가용 가짜 일자: 실제일 ±BUFFER 거래일 밖
        ev_pos = all_dates.searchsorted(anchor_real)
        excl_lo = max(0, ev_pos - BUFFER)
        excl_hi = min(len(all_dates) - 1, ev_pos + BUFFER)
        # 또한 추정창+이벤트창이 모두 dataset 안에 들어가야 함
        min_pos = abs(EST_START) + 5
        max_pos = len(all_dates) - EVENT_WINDOW - 5
        candidates = [i for i in range(min_pos, max_pos + 1) if i < excl_lo or i > excl_hi]
        if len(candidates) < K_PLACEBO:
            k = len(candidates)
        else:
            k = K_PLACEBO
        picks = rng.choice(candidates, size=k, replace=False)

        placebo_cars = []
        for i in picks:
            fake_anchor = all_dates.iloc[int(i)]
            car_f = compute_car(ret, fake_anchor, ASSET, MARKET, EST_START, EST_END, EVENT_WINDOW)
            if car_f is not None:
                placebo_cars.append(car_f)
        placebo_cars = np.array(placebo_cars)
        if len(placebo_cars) == 0:
            print(f'⚠️ {event}: placebo CAR 모두 실패')
            rows.append({'event_name': event, 'real_CAR': real_car, 'placebo_mean_CAR': None,
                         'placebo_std_CAR': None, 'percentile_of_real': None,
                         'placebo_p': None, 'n_placebo': 0})
            continue

        pct = float((placebo_cars < real_car).mean())  # 실제 CAR의 좌측 percentile
        p_two = 2 * min(pct, 1 - pct)                  # two-sided placebo p
        rows.append({
            'event_name': event,
            'real_CAR': real_car,
            'placebo_mean_CAR': float(placebo_cars.mean()),
            'placebo_std_CAR':  float(placebo_cars.std(ddof=1)),
            'percentile_of_real': pct,
            'placebo_p': p_two,
            'n_placebo': int(len(placebo_cars)),
        })
        print(f'  {event}: real_CAR={real_car:+.4f} | placebo_mean={placebo_cars.mean():+.4f}±{placebo_cars.std():.4f} | percentile={pct:.3f} | p={p_two:.4f} | n={len(placebo_cars)}')

    out = RESULTS / 'event_study_placebo.csv'
    pd.DataFrame(rows).to_csv(out, index=False, encoding='utf-8-sig')
    print(f'\n✅ {out.name} 저장 ({len(rows)}행)')


if __name__ == '__main__':
    sys.exit(main() or 0)
