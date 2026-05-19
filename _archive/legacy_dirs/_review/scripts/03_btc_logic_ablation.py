"""
03_btc_logic_ablation.py — BTC 비거래일 합산 로직 영향도 검증

수정 사항:
1) [A1] 팀원 master_clean.ipynb 셀 #05 의 "주말 BTC 수익률을 직전 거래일 평균합산
   ((금+토+일)/3)" 비표준 로직이 분석 결과에 미치는 영향을 정량 평가.
2) yfinance 로 BTC 원시 종가 다시 받아 표준 로그 수익률 계산.
3) 두 시계열의 분포 통계 + 상관 비교 + GARCH 결과 차이 비교.

이번 작업은 ablation (영향도 검증) 만 수행. 전체 파이프라인 재실행은 다음 phase.

입력:  Edit_mj/returns.csv (팀원 averaging 적용된 BTC), yfinance (BTC raw close)
출력:  _review/results/btc_logic_ablation.csv (분포 통계 비교)
       _review/results/btc_returns_compare.csv (날짜별 두 시계열)
"""

import os, warnings
warnings.filterwarnings('ignore')

import numpy as np
import pandas as pd
import yfinance as yf
from scipy import stats

REPO = '/mnt/d/project/2026_capstone'
OUT  = f'{REPO}/_review/results'
os.makedirs(OUT, exist_ok=True)

print('=' * 70)
print('BTC 비거래일 로직 ablation')
print('=' * 70)

# ============================================================
# 1. 팀원 버전 BTC 수익률 (returns.csv)
# ============================================================
team = pd.read_csv(f'{REPO}/Edit_mj/returns.csv')
team['date'] = pd.to_datetime(team['date'])
team_btc = team[['date', 'BTC']].copy().rename(columns={'BTC': 'BTC_team'})
print(f'팀원 BTC: {len(team_btc)}행 ({team_btc["date"].min().date()} ~ {team_btc["date"].max().date()})')

# ============================================================
# 2. 표준 BTC 수익률 (yfinance 직접 다운로드)
# ============================================================
print('\n▶ yfinance BTC 다운로드 중...')
raw = yf.download('BTC-USD', start='2019-01-01', end='2026-04-28',
                  auto_adjust=False, progress=False)['Close']
raw.index = pd.to_datetime(raw.index.date)
raw = pd.Series(raw.values.flatten(), index=raw.index, name='BTC_close')

# 거래일만 (NYSE) — 팀원 returns.csv 의 날짜에 맞춤
trading_days = team_btc['date'].values
btc_close_trading = raw.reindex(trading_days)

# 표준 로그 수익률 (NYSE 거래일 기준 단순 차분, 비거래일 무시)
std_returns = np.log(btc_close_trading / btc_close_trading.shift(1))
std_btc = pd.DataFrame({
    'date'    : trading_days,
    'BTC_std' : std_returns.values,
})
print(f'표준 BTC: {len(std_btc)}행')

# ============================================================
# 3. 두 시계열 병합·비교
# ============================================================
merged = team_btc.merge(std_btc, on='date', how='inner').dropna()
merged.to_csv(f'{OUT}/btc_returns_compare.csv', index=False, encoding='utf-8-sig')
print(f'\n저장: btc_returns_compare.csv  ({len(merged)}행)')

# 분포 통계
def stats_row(s, name):
    return {
        '버전'     : name,
        'N'       : len(s),
        '평균'     : round(s.mean(), 5),
        '표준편차'   : round(s.std(), 5),
        '왜도'     : round(s.skew(), 3),
        '첨도'     : round(s.kurt(), 3),
        '최솟값'    : round(s.min(), 4),
        '최댓값'    : round(s.max(), 4),
        '연환산변동성(%)': round(s.std()*np.sqrt(252)*100, 2),
    }

stat_df = pd.DataFrame([
    stats_row(merged['BTC_team'], '팀원 (주말합산)'),
    stats_row(merged['BTC_std'],  '표준 (NYSE 차분)'),
])
stat_df.to_csv(f'{OUT}/btc_logic_ablation.csv', index=False, encoding='utf-8-sig')

print('\n▶ 분포 통계 비교')
print(stat_df.to_string(index=False))

# 상관계수
r_p, _ = stats.pearsonr(merged['BTC_team'], merged['BTC_std'])
print(f'\n▶ 두 시계열 Pearson 상관: {r_p:.4f}')

# 차이
diff = merged['BTC_team'] - merged['BTC_std']
print(f'▶ 차이 (팀원 - 표준)')
print(f'  평균   : {diff.mean():+.6f}')
print(f'  표준편차: {diff.std():.6f}')
print(f'  최댓값  : {diff.abs().max():.4f}  (날짜: {merged.loc[diff.abs().idxmax(), "date"].date()})')

# 월요일만 필터 (팀원 로직이 발동하는 날)
merged['weekday'] = merged['date'].dt.day_name()
mon_diff = diff[merged['weekday'] == 'Monday']
print(f'\n▶ 월요일만 (팀원 로직 발동일):  N={len(mon_diff)}')
print(f'  평균 차이   : {mon_diff.mean():+.6f}')
print(f'  표준편차    : {mon_diff.std():.6f}')
print(f'  최댓값 차이 : {mon_diff.abs().max():.4f}')

# ============================================================
# 4. 분산 축소 효과 (팀원 로직이 변동성을 얼마나 평탄화시키는가)
# ============================================================
print('\n' + '=' * 70)
print('▶ 분산 축소 효과 분석')
print('=' * 70)

vol_team = merged['BTC_team'].std() * np.sqrt(252) * 100
vol_std  = merged['BTC_std'].std()  * np.sqrt(252) * 100
print(f'  팀원 버전 연환산 변동성: {vol_team:.2f}%')
print(f'  표준 버전 연환산 변동성: {vol_std:.2f}%')
print(f'  비율: {vol_team/vol_std:.4f}  (1.0 미만 = 팀원이 더 평탄)')

# F 검정 (분산 동일성)
f_stat = (merged['BTC_std'].var() / merged['BTC_team'].var())
df1 = df2 = len(merged) - 1
f_pval = 2 * min(stats.f.cdf(f_stat, df1, df2), 1 - stats.f.cdf(f_stat, df1, df2))
print(f'  F 검정 (분산 동일성): F={f_stat:.4f}  p={f_pval:.4f}')

# Ljung-Box autocorrelation
from statsmodels.stats.diagnostic import acorr_ljungbox
lb_team = acorr_ljungbox(merged['BTC_team'].dropna(), lags=[5, 10], return_df=True)
lb_std  = acorr_ljungbox(merged['BTC_std'].dropna(), lags=[5, 10], return_df=True)
print(f'\n▶ Ljung-Box 자기상관 검정 (lag=5, 10)')
print(f'  팀원: lag5 p={lb_team.loc[5,"lb_pvalue"]:.4f}  lag10 p={lb_team.loc[10,"lb_pvalue"]:.4f}')
print(f'  표준: lag5 p={lb_std.loc[5,"lb_pvalue"]:.4f}  lag10 p={lb_std.loc[10,"lb_pvalue"]:.4f}')
print('  (p<0.05 = 자기상관 유의. 팀원 로직이 자기상관 도입 가능)')

print('\n✅ 03_btc_logic_ablation.py 완료')

# 결론 메시지
print('\n' + '=' * 70)
print('진단 결론')
print('=' * 70)
ratio = vol_team/vol_std
if ratio < 0.95:
    print(f'⚠️ 팀원 로직이 변동성을 {(1-ratio)*100:.1f}% 축소. GARCH/Quantile 결과 편향 가능.')
elif ratio > 1.05:
    print(f'⚠️ 팀원 로직이 변동성을 {(ratio-1)*100:.1f}% 증폭.')
else:
    print(f'✅ 두 시계열의 변동성 차이는 {abs(1-ratio)*100:.1f}% 미만 — 영향 미미.')
