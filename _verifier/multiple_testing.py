"""다중비교 보정 (Benjamini-Hochberg FDR) 후처리.

대상:
  1. Edit_mj/results/event_study_car.csv  → BH-FDR 적용 후 sig_bh 컬럼 추가
  2. Edit_mj/results/quantile_results.csv → CORE_TAUS=[0.05, 0.10, 0.50]에 BH-FDR 적용

산출:
  Edit_mj/results/multiple_testing_adjusted.csv (통합 보정 결과)
  Edit_mj/results/event_study_car_bh.csv      (이벤트 스터디 보정본)
  Edit_mj/results/quantile_results_bh.csv     (분위수 회귀 보정본)

기준: Benjamini & Hochberg (1995) FDR α=0.05.
"""
import sys
from pathlib import Path
import pandas as pd
import numpy as np

ROOT = Path(__file__).resolve().parent.parent
RESULTS = ROOT / 'Edit_mj' / 'results'
ALPHA = 0.05
CORE_TAUS = [0.05, 0.10, 0.50]


def bh_fdr(pvals: np.ndarray, alpha: float = 0.05) -> tuple[np.ndarray, np.ndarray]:
    """Benjamini-Hochberg FDR adjusted p-values.
    Returns (adjusted_p, rejected_mask)
    """
    p = np.asarray(pvals, dtype=float)
    n = len(p)
    if n == 0:
        return np.array([]), np.array([], dtype=bool)
    order = np.argsort(p)
    ranked = p[order]
    # BH adjusted p = min over k>=i of (n*p_k / k)
    adj = ranked * n / np.arange(1, n + 1)
    # enforce monotonicity
    adj_mono = np.minimum.accumulate(adj[::-1])[::-1]
    adj_mono = np.clip(adj_mono, 0, 1)
    # reorder
    adj_back = np.empty_like(adj_mono)
    adj_back[order] = adj_mono
    rejected = adj_back < alpha
    return adj_back, rejected


def adjust_event_study():
    src = RESULTS / 'event_study_car.csv'
    if not src.exists():
        print(f'⚠ {src} 없음, 스킵'); return None
    df = pd.read_csv(src)
    # p-value 컬럼 후보
    pcol = next((c for c in ['p_norm','p_t','p','p_value'] if c in df.columns), None)
    if pcol is None:
        print(f'⚠ {src}에 p-value 컬럼 없음 (cols={list(df.columns)})'); return None

    # BTC만 (Safe-Haven 가설 핵심)
    mask = df['asset'] == 'BTC' if 'asset' in df.columns else slice(None)
    btc = df[mask].copy()
    if len(btc) == 0:
        print('⚠ BTC 행 없음'); return None
    adj, rej = bh_fdr(btc[pcol].fillna(1).values, ALPHA)
    btc[f'{pcol}_bh'] = adj
    btc['sig_bh'] = rej

    # 전체로도 (모든 자산)
    df_all = df.copy()
    adj_all, rej_all = bh_fdr(df_all[pcol].fillna(1).values, ALPHA)
    df_all[f'{pcol}_bh'] = adj_all
    df_all['sig_bh'] = rej_all

    out = RESULTS / 'event_study_car_bh.csv'
    df_all.to_csv(out, index=False, encoding='utf-8-sig')
    print(f'✓ {out.name}: {len(df_all)}행, BH 유의={rej_all.sum()}건 (BTC만: {rej.sum()}건)')

    return df_all[['event','asset',pcol,f'{pcol}_bh','sig_bh']].copy().assign(method='event_study')


def adjust_quantile_reg():
    src = RESULTS / 'quantile_results.csv'
    if not src.exists():
        print(f'⚠ {src} 없음, 스킵'); return None
    df = pd.read_csv(src)
    # 컬럼명에서 p_value 찾기
    pcol = next((c for c in df.columns if c.strip() in ('p','p_value','p값','p_β','p_β_Z')), None)
    if pcol is None:
        # 한글 컬럼 또는 한자 p
        cand = [c for c in df.columns if 'p' == c.strip().lower() or c.strip() == 'p']
        pcol = cand[0] if cand else None
    if pcol is None:
        print(f'⚠ p-value 컬럼 자동 매칭 실패 (cols={list(df.columns)}), "p" 컬럼 사용 시도')
        pcol = 'p' if 'p' in df.columns else None
    if pcol is None:
        return None

    # CORE_TAUS만 + SP500_z(또는 Gold_z) 행만
    tau_col = next((c for c in df.columns if c.strip() in ('τ','tau')), None)
    if tau_col is None:
        print(f'⚠ τ 컬럼 없음'); return None
    df_core = df[df[tau_col].astype(float).round(3).isin([round(t,3) for t in CORE_TAUS])].copy()
    if len(df_core) == 0:
        print('⚠ CORE_TAUS에 해당하는 행 없음'); return None
    adj, rej = bh_fdr(df_core[pcol].fillna(1).values, ALPHA)
    df_core[f'{pcol}_bh'] = adj
    df_core['sig_bh'] = rej

    # 전체에도
    df_all = df.copy()
    adj_all, rej_all = bh_fdr(df_all[pcol].fillna(1).values, ALPHA)
    df_all[f'{pcol}_bh'] = adj_all
    df_all['sig_bh'] = rej_all

    out = RESULTS / 'quantile_results_bh.csv'
    df_all.to_csv(out, index=False, encoding='utf-8-sig')
    print(f'✓ {out.name}: {len(df_all)}행, BH 유의={rej_all.sum()}건 (CORE_TAUS만: {rej.sum()}건)')

    # 통합 보고용 슬라이스 (event_col 통일)
    keep_cols = [c for c in df_core.columns if c in ('범위','이벤트','모델',tau_col,'변수',pcol,f'{pcol}_bh','sig_bh')]
    slim = df_core[keep_cols].copy()
    slim['method'] = 'quantile_reg'
    return slim


def main():
    print('=== Multiple Testing (BH-FDR) Post-processing ===')
    es = adjust_event_study()
    qr = adjust_quantile_reg()

    # 통합 보고서
    combined_rows = []
    if es is not None:
        for _, r in es.iterrows():
            combined_rows.append({
                'method': 'event_study',
                'identifier': f'{r["event"]} × {r["asset"]}',
                'p_raw': r[es.columns[2]],  # p
                'p_bh': r[es.columns[3]],   # p_bh
                'sig_bh': bool(r['sig_bh']),
            })
    if qr is not None:
        tau_col = next((c for c in qr.columns if c.strip() in ('τ','tau')), 'τ')
        for _, r in qr.iterrows():
            event_part = r.get('이벤트', r.get('범위', '?'))
            model_part = r.get('모델', '?')
            var_part   = r.get('변수', '?')
            p_raw_col = qr.columns[-4]  # 대략
            p_bh_col  = qr.columns[-3]
            combined_rows.append({
                'method': 'quantile_reg',
                'identifier': f'{event_part} × {model_part} × τ={r[tau_col]} × {var_part}',
                'p_raw': r[p_raw_col],
                'p_bh': r[p_bh_col],
                'sig_bh': bool(r['sig_bh']),
            })
    if combined_rows:
        out = RESULTS / 'multiple_testing_adjusted.csv'
        pd.DataFrame(combined_rows).to_csv(out, index=False, encoding='utf-8-sig')
        print(f'✓ {out.name}: {len(combined_rows)}건')
        n_sig = sum(1 for r in combined_rows if r['sig_bh'])
        print(f'  BH-FDR α=0.05 통과: {n_sig}건')


if __name__ == '__main__':
    main()
