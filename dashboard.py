"""2026 캡스톤 — BTC 안전자산 가설 검증 대시보드 (Phase 4 신규)

실행: pip install streamlit plotly && python3 -m streamlit run dashboard.py

데이터: Edit_mj/results/*.csv (Phase 1 본분석 + Phase 3 자가 피드백 결과)
"""
import os
from pathlib import Path
import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px

st.set_page_config(
    page_title="BTC 안전자산 가설 (1827행 정본)",
    page_icon="₿",
    layout="wide",
    initial_sidebar_state="expanded",
)

ROOT = Path(__file__).resolve().parent
RESULTS = ROOT / 'Edit_mj' / 'results'

# 1827행 정본 표기
EVENT_LABEL = {
    'hormuz_crisis'          : '호르무즈 위기',
    'soleimani_assassination': '솔레이마니 암살',
    'russia_ukraine_war'     : '러-우 전쟁',
    'israel_hamas_war'       : '이스라엘-하마스',
    'israel_iran'            : '이스라엘-이란 충돌',
    'us_israel_iran'         : '미-이스라엘-이란',
}
EVENT_DATE = {
    'hormuz_crisis'          : '2019-06-13',
    'soleimani_assassination': '2020-01-03',
    'russia_ukraine_war'     : '2022-02-24',
    'israel_hamas_war'       : '2023-10-07',
    'israel_iran'            : '2024-04-01',
    'us_israel_iran'         : '2026-02-28',
}
ASSET_COLORS = {
    "BTC": "#F7931A", "Gold": "#FFD700", "SP500": "#1976D2",
    "NASDAQ": "#7B1FA2", "TLT": "#388E3C", "DXY": "#E64A19",
}
VERDICT_COLOR = {
    "Safe Haven":  "#2E7D32",
    "Weak Haven":  "#558B2F",
    "Diversifier": "#F9A825",
    "Risky Asset": "#C62828",
}


@st.cache_data
def load_csv(name):
    p = RESULTS / name
    if not p.exists():
        return None
    return pd.read_csv(p)


# ── 헤더 ─────────────────────────────────────────────────────
st.title("₿ BTC 안전자산 가설 검증 대시보드")
st.caption("1827행 정본 master_data · 6개 지정학 이벤트 · 3종 본분석 + BH-FDR 다중비교 보정 + Placebo")

# 사이드바
st.sidebar.header("탐색")
section = st.sidebar.radio(
    "섹션",
    ["통합 판정", "이벤트 스터디", "분위수 회귀", "GARCH", "원 데이터·검증 보고서"],
)
st.sidebar.divider()
st.sidebar.markdown("**6개 이벤트**")
for k, v in EVENT_LABEL.items():
    st.sidebar.caption(f"• {v} ({EVENT_DATE[k]})")

# ══════════════════════════════════════════════════════
# 1. 통합 판정
# ══════════════════════════════════════════════════════
if section == "통합 판정":
    st.header("최종 통합 판정 (Baur & Lucey 2010 3조건)")
    fj = load_csv('final_judgment.csv')
    if fj is None:
        st.error("final_judgment.csv 없음 — `python3 _verifier/final_judgment.py` 먼저 실행")
    else:
        # KPI
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Safe Haven", int((fj['verdict']=='Safe Haven').sum()), help="3/3 통과")
        col2.metric("Weak Haven", int((fj['verdict']=='Weak Haven').sum()), help="2/3 통과")
        col3.metric("Diversifier", int((fj['verdict']=='Diversifier').sum()), help="1/3 통과")
        col4.metric("Risky Asset", int((fj['verdict']=='Risky Asset').sum()), help="0/3 통과")

        st.divider()

        # 히트맵 (이벤트 × 조건)
        st.subheader("이벤트 × 조건 매트릭스")
        cond_cols = ['C1_event_study_pass','C2_quantile_reg_pass','C3_garch_pass']
        mat = fj[cond_cols].astype(int).values
        fig = go.Figure(data=go.Heatmap(
            z=mat,
            x=['C1 이벤트 스터디', 'C2 분위수 회귀 (τ=0.05)', 'C3 GARCH (GPR γ)'],
            y=fj['event_label'].tolist(),
            text=[[('✅' if v else '❌') for v in row] for row in mat],
            texttemplate='%{text}',
            colorscale=[[0, '#C62828'], [1, '#2E7D32']],
            showscale=False,
        ))
        fig.update_layout(height=380, margin=dict(l=10, r=10, t=10, b=10))
        st.plotly_chart(fig, use_container_width=True)

        # 표
        st.subheader("이벤트별 상세")
        display = fj[['event_label','C1_detail','C2_detail','C3_detail','score','verdict']].copy()
        display.columns = ['이벤트', 'C1 상세 (이벤트 스터디)', 'C2 상세 (분위수 회귀)', 'C3 상세 (GARCH)', '점수', '판정']
        def color_verdict(v):
            c = VERDICT_COLOR.get(v, '#888')
            return f'background-color: {c}; color: white; font-weight: bold;'
        styled = display.style.applymap(color_verdict, subset=['판정'])
        st.dataframe(styled, use_container_width=True, hide_index=True)

        st.divider()
        report = (RESULTS / 'final_report.md')
        if report.exists():
            with st.expander("📄 final_report.md (전체)", expanded=False):
                st.markdown(report.read_text(encoding='utf-8'))

# ══════════════════════════════════════════════════════
# 2. 이벤트 스터디
# ══════════════════════════════════════════════════════
elif section == "이벤트 스터디":
    st.header("이벤트 스터디 — MacKinlay 1997 (±17일, Bootstrap 5000회, BH-FDR + Placebo)")
    es = load_csv('event_study_car_bh.csv')
    if es is None:
        es = load_csv('event_study_car.csv')
    if es is None:
        st.error("event_study_car_bh.csv 없음")
    else:
        # 자산 필터
        assets = sorted(es['asset'].dropna().unique())
        sel_asset = st.multiselect("자산 선택", assets, default=['BTC'])
        sub = es[es['asset'].isin(sel_asset)].copy()
        sub['event_label'] = sub['event'].map(EVENT_LABEL).fillna(sub['event'])

        # CAR 바 그래프 (자산별 그룹)
        fig = px.bar(
            sub, x='event_label', y='CAR', color='asset',
            color_discrete_map=ASSET_COLORS,
            barmode='group',
            title='이벤트별 CAR (±17일)',
        )
        fig.add_hline(y=0, line_color='black', line_width=1)
        fig.update_layout(xaxis_title='이벤트', yaxis_title='Cumulative Abnormal Return')
        st.plotly_chart(fig, use_container_width=True)

        # 통계 표
        st.subheader("CAR + 검정 결과")
        pcol = 'p_norm_bh' if 'p_norm_bh' in sub.columns else next((c for c in ['p_t','p_norm','p'] if c in sub.columns), None)
        keep = ['event_label','asset','CAR','t_stat','p_norm','p_boot']
        if pcol and pcol not in keep:
            keep.append(pcol)
        if 'sig_bh' in sub.columns:
            keep.append('sig_bh')
        keep = [c for c in keep if c in sub.columns]
        st.dataframe(sub[keep].round(4), use_container_width=True, hide_index=True)

        # Placebo
        pl = load_csv('event_study_placebo.csv')
        if pl is not None:
            st.divider()
            st.subheader("Placebo 검정 (실제 vs 가짜 이벤트일 200회)")
            pl['event_label'] = pl['event_name'].map(EVENT_LABEL).fillna(pl['event_name'])
            st.dataframe(pl[['event_label','real_CAR','placebo_mean_CAR','placebo_std_CAR','percentile_of_real','placebo_p','n_placebo']].round(4),
                         use_container_width=True, hide_index=True)
            st.caption("placebo_p > 0.05 → 실제 이벤트가 가짜 일자와 통계적으로 구분되지 않음 (이벤트 효과 약함)")

# ══════════════════════════════════════════════════════
# 3. 분위수 회귀
# ══════════════════════════════════════════════════════
elif section == "분위수 회귀":
    st.header("분위수 회귀 — Koenker & Bassett 1978 (HAC SE, BH-FDR)")
    qr = load_csv('quantile_results_bh.csv')
    if qr is None:
        qr = load_csv('quantile_results.csv')
    if qr is None:
        st.error("quantile_results 없음")
    else:
        col1, col2 = st.columns(2)
        # τ 필터
        tau_col = next((c for c in qr.columns if c.strip() in ('τ','tau')), 'τ')
        tau_vals = sorted(qr[tau_col].astype(float).unique())
        sel_taus = col1.multiselect("τ 선택", [f'{t:.3f}' for t in tau_vals], default=['0.050','0.100','0.500'])
        sel_taus_f = [float(t) for t in sel_taus]
        sub = qr[qr[tau_col].astype(float).round(3).isin([round(t,3) for t in sel_taus_f])].copy()

        # 변수 필터
        if '변수' in sub.columns:
            vars_avail = sorted(sub['변수'].dropna().unique())
            sel_vars = col2.multiselect("변수", vars_avail, default=['SP500_z','Gold_z','GPR_custom_z'])
            sub = sub[sub['변수'].isin(sel_vars)]

        # β plot
        bcol = next((c for c in sub.columns if c.strip() in ('β','beta')), 'β')
        if bcol in sub.columns and '이벤트' in sub.columns:
            fig = px.scatter(
                sub, x=tau_col, y=bcol, color='이벤트', symbol='변수' if '변수' in sub.columns else None,
                hover_data=['모델'] if '모델' in sub.columns else None,
                title='β 계수 (이벤트별 × τ별 × 변수별)',
            )
            fig.add_hline(y=0, line_color='black', line_width=1, line_dash='dash')
            st.plotly_chart(fig, use_container_width=True)

        st.subheader("결과 표 (선택 τ)")
        st.dataframe(sub.round(5), use_container_width=True, hide_index=True)

# ══════════════════════════════════════════════════════
# 4. GARCH
# ══════════════════════════════════════════════════════
elif section == "GARCH":
    st.header("GARCH-X — Engle 2002 (Student-t MLE, multi-init, ADF·Ljung-Box)")
    comp = load_csv('garch_model_comparison.csv')
    gamma = load_csv('garch_gamma_results.csv')
    adf = load_csv('adf_test.csv')

    if comp is not None:
        st.subheader("5개 모델 비교 (AIC/BIC, α+β, 수렴)")
        st.dataframe(comp, use_container_width=True, hide_index=True)
    if gamma is not None:
        st.subheader("외생변수 γ 계수")
        st.dataframe(gamma.round(4), use_container_width=True, hide_index=True)
        st.caption("γ > 0 유의 → 변동성 증가 (위험자산), γ < 0 유의 → 변동성 감소 (haven)")
    if adf is not None:
        st.subheader("ADF 정상성 검증 (사전)")
        st.dataframe(adf.round(6), use_container_width=True, hide_index=True)

    # EGARCH 강건성
    eg = load_csv('egarch_model_comparison.csv')
    if eg is not None:
        with st.expander("EGARCH 강건성 검증 (비대칭 변동성)"):
            st.dataframe(eg, use_container_width=True, hide_index=True)

# ══════════════════════════════════════════════════════
# 5. 원 데이터·검증 보고서
# ══════════════════════════════════════════════════════
else:
    st.header("원 데이터 · 검증 보고서")
    st.subheader("master_data (1827행)")
    master = pd.read_csv(ROOT / 'Edit_mj' / 'GPR_custom_analysis' / 'master_data_generated' / 'master_data.csv')
    master['date'] = pd.to_datetime(master['date'])
    st.caption(f"기간: {master['date'].min().date()} ~ {master['date'].max().date()} · {len(master)}행")

    # 이벤트별 BTC + Gold 시계열
    fig = go.Figure()
    for ev in EVENT_LABEL:
        sub = master[master['event_name'] == ev].sort_values('date')
        if len(sub) == 0: continue
        fig.add_trace(go.Scatter(x=sub['date'], y=sub['BTC'].cumsum(), name=EVENT_LABEL[ev], mode='lines'))
    fig.update_layout(title='이벤트별 BTC 누적 수익률', xaxis_title='Date', yaxis_title='Cumulative log return')
    st.plotly_chart(fig, use_container_width=True)

    # 검증 보고서들
    st.subheader("검증 사이클 보고서")
    reports_dir = ROOT / '.claude' / 'verification_reports'
    cycles = sorted(reports_dir.glob('cycle_*.md'))
    if cycles:
        chosen = st.selectbox("사이클", [c.name for c in cycles], index=len(cycles)-1)
        st.markdown((reports_dir / chosen).read_text(encoding='utf-8'))
    else:
        st.info("verification_reports/ 비어있음")

st.divider()
st.caption("© 2026 캡스톤 | 팀명: 분석많이된다 | catalog.json v1.4 + verifier.py cycle 3 ALL PASS")
