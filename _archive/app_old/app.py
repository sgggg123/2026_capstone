"""
2026_capstone — 비트코인 안전자산 가설 검증 대시보드 (수정판)

팀원 fbghkdrb/2026_capstone repo 의 분석을 바탕으로 4가지 critical 결함을 수정한 버전.
- B1: GARCH 라이브러리 교체 (커스텀 MLE → arch.arch_model)
- B2/B3: alpha=0, omega=0 경계 수렴 해소 (다중 초기값 + bound 강화)
- C1: Event Study 윈도우 sensitivity (±3, ±5, ±10, ±17)
- A1: BTC 비거래일 합산 로직 영향도 검증

실행:  pip install streamlit plotly
       cd /mnt/d/project/2026_capstone && python3 -m streamlit run app.py
"""
import os
import json
import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px

st.set_page_config(
    page_title="BTC 안전자산 가설 (수정판)",
    page_icon="₿",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── 색상 ─────────────────────────────────────────────────────
ASSET_COLORS = {
    "BTC": "#F7931A", "Gold": "#FFD700", "SP500": "#1976D2",
    "NASDAQ": "#7B1FA2", "TLT": "#388E3C", "DXY": "#E64A19",
}
LABEL_COLORS = {
    "Safe Haven": "#2E7D32",
    "Risky Asset": "#C62828",
    "Marginal":   "#F9A825",
    "Non-Sig":    "#757575",
}
EVENT_LABELS = {
    'hormuz'             : '호르무즈 위기',
    'soleimani'          : '솔레이마니 암살',
    'russia_ukraine_war' : '러-우 전쟁',
    'israel_hamas_war'   : '이스라엘-하마스',
    'israel_iran_war'    : '이스라엘-이란 충돌',
    'us_israel_iran_war' : '미-이스라엘-이란',
}
EVENT_DATES = {
    'hormuz'             : '2019-06-13',
    'soleimani'          : '2020-01-03',
    'russia_ukraine_war' : '2022-02-24',
    'israel_hamas_war'   : '2023-10-07',
    'israel_iran_war'    : '2024-04-01',
    'us_israel_iran_war' : '2026-02-28',
}

REPO = os.path.dirname(os.path.abspath(__file__))
RESULTS = f'{REPO}/_review/results'

# ── 데이터 로드 ──────────────────────────────────────────────
@st.cache_data
def load_all():
    master  = pd.read_csv(f'{REPO}/Edit_mj/master_data.csv')
    master['date'] = pd.to_datetime(master['date'])
    returns = pd.read_csv(f'{REPO}/Edit_mj/returns.csv')
    returns['date'] = pd.to_datetime(returns['date'])

    es      = pd.read_csv(f'{RESULTS}/event_study_sensitivity.csv')
    es_car  = pd.read_csv(f'{RESULTS}/event_study_summary_BTC_CAR.csv', index_col=0)
    es_lbl  = pd.read_csv(f'{RESULTS}/event_study_summary_BTC_label.csv', index_col=0)

    g_arch  = pd.read_csv(f'{RESULTS}/garch_arch_lib.csv')
    g_cmp_a = pd.read_csv(f'{RESULTS}/garch_arch_lib_compare.csv')
    g_cust  = pd.read_csv(f'{RESULTS}/garch_custom_fixed.csv')
    g_cmp_b = pd.read_csv(f'{RESULTS}/garch_custom_compare.csv')

    btc_abl = pd.read_csv(f'{RESULTS}/btc_logic_ablation.csv')
    btc_cmp = pd.read_csv(f'{RESULTS}/btc_returns_compare.csv')
    btc_cmp['date'] = pd.to_datetime(btc_cmp['date'])

    return master, returns, es, es_car, es_lbl, g_arch, g_cmp_a, g_cust, g_cmp_b, btc_abl, btc_cmp

master, returns, es, es_car, es_lbl, g_arch, g_cmp_a, g_cust, g_cmp_b, btc_abl, btc_cmp = load_all()

# ── 사이드바 ──────────────────────────────────────────────────
st.sidebar.title("₿ BTC 안전자산 가설 (수정판)")
st.sidebar.markdown("**원본 repo**: `fbghkdrb/2026_capstone`\n\n**수정 phase**: critical 4건")
st.sidebar.markdown("---")
page = st.sidebar.radio("페이지", [
    "🏠 개요 & 결론",
    "🔬 Event Study (윈도우 sensitivity)",
    "📊 GARCH 변동성 (수정판)",
    "🧪 BTC 비거래일 로직 ablation",
    "📋 수정 사항 요약",
    "📚 방법론·수식",
    "🎓 학술 검증",
])

# ════════════════════════════════════════════════════════════
# 1. 개요 & 결론
# ════════════════════════════════════════════════════════════
if page == "🏠 개요 & 결론":
    st.title("비트코인은 디지털 안전자산인가?")
    st.markdown("""
> **연구 질문**: 지정학적 위기 상황(2019~2026 6개 이벤트)에서 BTC는 금(Gold)처럼 안전자산으로 기능하는가?

**판정 기준 — Baur & Lucey (2010)**
- ① **위기 시 BTC 초과수익(CAR) ≥ 0, 통계적으로 유의**
- ② BTC-SP500 상관계수가 위기 시 ≤ 0
- ③ 하락 분위(τ ≤ 0.10) 에서 BTC 의 SP500 회귀계수 β < 0
""")
    st.markdown("---")

    # ── 핵심 수치 ──
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("이벤트 수", "6개")
    c2.metric("표본 거래일", f"{len(master)}일")
    c3.metric("분석 기간", "2019~2026")
    c4.metric("수정 항목", "4 critical", help="B1 GARCH, B2/B3 경계수렴, C1 윈도우, A1 BTC 로직")

    st.markdown("---")
    st.subheader("📌 이벤트별 BTC 결론 (윈도우 ±10 거래일 기준)")

    # ±10 일 결과 카드
    es10 = es[(es['window']==10) & (es['asset']=='BTC')].set_index('event')
    cols = st.columns(3)
    for i, ev in enumerate(EVENT_DATES):
        if ev not in es10.index:
            continue
        row = es10.loc[ev]
        label = row['label']
        color = LABEL_COLORS.get(label, "#666")
        with cols[i % 3]:
            st.markdown(f"""
            <div style='padding:14px;border-radius:10px;background:{color}18;
                        border:2px solid {color};margin-bottom:10px'>
                <b style='color:{color};font-size:15px'>{EVENT_LABELS[ev]}</b><br>
                <span style='font-size:11px;color:#888'>{EVENT_DATES[ev]}</span><br>
                <span style='font-size:13px'>CAR <b>{row['CAR']:+.4f}</b></span><br>
                <span style='font-size:11px'>p_BMP={row['p_BMP']:.3f} | p_block={row['p_block']:.3f}</span><br>
                <b style='font-size:14px;color:{color}'>{label}</b>
            </div>""", unsafe_allow_html=True)

    st.markdown("---")
    st.subheader("🎯 핵심 결론")
    st.error("""
    **BTC 는 일관된 안전자산이 아니다.**

    - **이스라엘-하마스 (2023-10-07)** 만 윈도우 ±17 일에서 Safe Haven 분류 (CAR=+0.328, p=0.012). 그러나
      윈도우를 ±3, ±5, ±10 으로 줄이면 효과 사라짐 → **결론이 윈도우에 의존**.
    - 다른 5개 이벤트는 모든 윈도우에서 일관되게 Non-Sig 또는 Marginal.
    - GARCH 분석에서 **VIX(시장공포)가 BTC 변동성에 강한 양의 영향** (γ=+7.56, p<0.001) — 지정학 리스크
      자체보다 시장 공포 채널이 더 직접적.
    """)

# ════════════════════════════════════════════════════════════
# 2. Event Study sensitivity
# ════════════════════════════════════════════════════════════
elif page == "🔬 Event Study (윈도우 sensitivity)":
    st.title("Event Study — 윈도우 sensitivity 분석")
    st.markdown("""
    팀원 원본은 ±25 → ±17 → ±3 으로 윈도우를 일방적으로 축소. 결과가 윈도우에 의존하는지 검증하기 위해
    **±3, ±5, ±10, ±17** 4개 윈도우로 동일 분석을 반복.

    **모델**:
    - BTC: Market Model (NASDAQ 벤치마크)
    - Gold, DXY: CMRM (평균수익률 모델)
    - TLT, NASDAQ: Market Model (SP500 벤치마크)
    - 검정: BMP (Standardized AR) + Circular Block Bootstrap (block=5, n_boot=5000)
    """)

    asset = st.selectbox("자산", ["BTC", "Gold", "TLT", "DXY", "NASDAQ"])

    sub = es[es['asset']==asset].copy()
    sub['event_label'] = sub['event'].map(EVENT_LABELS)

    # ── 1) CAR 히트맵 ──
    st.subheader(f"{asset} CAR (윈도우 × 이벤트)")
    pivot = sub.pivot_table(index='event_label', columns='window', values='CAR', aggfunc='first')
    pivot = pivot[[3, 5, 10, 17]]
    fig = go.Figure(data=go.Heatmap(
        z=pivot.values, x=[f"±{w}" for w in pivot.columns], y=pivot.index,
        colorscale='RdYlGn', zmid=0, text=pivot.round(3).values,
        texttemplate='%{text}', textfont={"size": 12}, colorbar=dict(title="CAR"),
    ))
    fig.update_layout(height=400, xaxis_title="이벤트 윈도우", yaxis_title="이벤트")
    st.plotly_chart(fig, use_container_width=True)

    # ── 2) 분류 라벨 표 ──
    st.subheader(f"{asset} 분류 결과 (Baur & Lucey 2010 기준)")
    pivot_lbl = sub.pivot_table(index='event_label', columns='window', values='label', aggfunc='first')
    pivot_lbl = pivot_lbl[[3, 5, 10, 17]]
    pivot_lbl.columns = [f"±{w}" for w in pivot_lbl.columns]
    st.dataframe(pivot_lbl, use_container_width=True)

    # ── 3) p-value 표 ──
    st.subheader(f"{asset} p-value")
    sub['p_min'] = sub[['p_BMP','p_block']].min(axis=1)
    pivot_p = sub.pivot_table(index='event_label', columns='window', values='p_min', aggfunc='first').round(4)
    pivot_p = pivot_p[[3, 5, 10, 17]]
    pivot_p.columns = [f"±{w}" for w in pivot_p.columns]
    st.dataframe(pivot_p.style.background_gradient(cmap='RdYlGn_r', vmin=0, vmax=0.2),
                 use_container_width=True)

    # ── 4) Robustness 진단 ──
    st.markdown("---")
    st.subheader("🔍 Robustness 진단")
    diag_rows = []
    for ev in EVENT_DATES:
        s = sub[sub['event']==ev].sort_values('window')
        if len(s) < 4: continue
        cars = s['CAR'].tolist()
        labels = s['label'].tolist()
        sign_changes = sum(1 for i in range(1, len(cars)) if np.sign(cars[i]) != np.sign(cars[i-1]))
        unique_labels = len(set(labels))
        diag_rows.append({
            '이벤트': EVENT_LABELS[ev],
            'CAR 부호 전환': sign_changes,
            '분류 종류': f"{unique_labels}/4",
            '안정성': '✅ 안정' if (sign_changes==0 and unique_labels<=2) else '⚠️ 불안정',
        })
    st.dataframe(pd.DataFrame(diag_rows), use_container_width=True, hide_index=True)

    if asset == "BTC":
        st.warning("""
        **⚠️ 이스라엘-하마스 결론은 윈도우에 의존**: ±17일에서 Safe Haven, ±10일에서 Marginal,
        ±3·±5일에서 Non-Sig. 즉 윈도우 길이에 따라 분류가 달라지므로 robust 한 결론이 아님.
        """)

# ════════════════════════════════════════════════════════════
# 3. GARCH (수정판)
# ════════════════════════════════════════════════════════════
elif page == "📊 GARCH 변동성 (수정판)":
    st.title("GARCH 분석 — 수정판")
    st.markdown("""
    **수정 사항 (B1 + B2 + B3)**

    1. **[B1]** 팀원 원본은 `arch.arch_model` 을 import 만 하고 실제로는 `scipy.optimize.minimize` 로
       커스텀 MLE 작성 → 표준오차 부정확. **수정**: ① arch 라이브러리 표준 구현 (HARX-GARCH-StudentsT) +
       ② 커스텀 MLE 도 보존하되 다중 초기값 grid search + bound 강화로 경계 수렴 해소.
    2. **[B2]** alpha 가 1e-6 하한에 경계 수렴 → 의미 없는 t-stat. **수정**: 다중 초기값(α₀=0.05~0.20)
       + bound `(1e-3, 0.5)`.
    3. **[B3]** omega 가 0 으로 수렴해 모델 정의 위배. **수정**: bound `(returns.var()*0.01, var_y*5)` 강제.
    """)

    method = st.radio("분석 방법", [
        "[A] arch 라이브러리 (mean equation X)",
        "[B] custom MLE FIXED (variance equation X)",
    ])

    if method.startswith("[A]"):
        df = g_arch
        cmp = g_cmp_a
        st.info("**모델 정의**: $r_t = \\mu + \\sum_k \\gamma_k X_{k,t} + \\epsilon_t$, $\\sigma_t^2 = \\omega + \\alpha\\epsilon_{t-1}^2 + \\beta\\sigma_{t-1}^2$, $\\epsilon \\sim t_\\nu$. 외생변수가 평균방정식에 들어감 (arch 라이브러리 GARCH-X 미지원).")
    else:
        df = g_cust
        cmp = g_cmp_b
        st.info("**모델 정의 (팀원 원본 유지)**: $\\sigma_t^2 = \\omega + \\alpha\\epsilon_{t-1}^2 + \\beta\\sigma_{t-1}^2 + \\sum_k \\gamma_k X_{k,t-1}$. 외생변수가 분산방정식에 들어감 (지정학 리스크 → BTC 변동성 직접 영향).")

    # 모델 비교 표
    st.subheader("모델 적합도 비교 (AIC 오름차순)")
    st.dataframe(cmp, use_container_width=True, hide_index=True)

    # γ 계수 표
    st.subheader("외생변수 γ 계수 + p-value")
    df_show = df[['model', 'variable', 'coef', 'p_value', 'sig']].copy()
    if 'se' in df.columns:
        df_show.insert(3, 'se', df['se'])
    st.dataframe(df_show, use_container_width=True, hide_index=True)

    # γ 막대그래프 (방법 B 만 SE 가 있어 95% CI 표시 가능)
    st.subheader("γ 계수 + 95% CI 시각화")
    df = df.copy()
    se_vals = df['se'].fillna(0) if 'se' in df.columns else pd.Series(0, index=df.index)
    df['display'] = df['model'] + " | " + df['variable']
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=df['display'], y=df['coef'],
        error_y=dict(type='data', array=1.96 * se_vals, visible=bool((se_vals > 0).any())),
        marker_color=['#C62828' if p<0.05 else ('#F9A825' if p<0.10 else '#757575')
                       for p in df['p_value']],
        text=df['sig'], textposition='outside',
    ))
    fig.add_hline(y=0, line_color='black', line_width=0.8)
    has_ci = bool((se_vals > 0).any())
    title_suffix = " (95% CI 표시)" if has_ci else " (방법 A 는 SE 미저장 — CI 생략)"
    fig.update_layout(height=420, xaxis_title="모델 | 변수", yaxis_title="γ 계수",
                      title="유의성: <span style='color:#C62828'>p<0.05</span> | <span style='color:#F9A825'>p<0.10</span> | <span style='color:#757575'>비유의</span>" + title_suffix)
    fig.update_xaxes(tickangle=-30)
    st.plotly_chart(fig, use_container_width=True)

    # 경계 수렴 진단
    st.markdown("---")
    st.subheader("✅ 경계 수렴 해소 검증")
    diag = cmp[['model', 'alpha', 'beta', 'omega']].copy()
    diag['α 진단'] = diag['alpha'].apply(lambda x: '✅ 정상' if x > 1e-2 else '⚠️ 경계')
    diag['ω 진단'] = diag['omega'].apply(lambda x: '✅ 정상' if x > 1e-3 else '⚠️ 0 근처')
    st.dataframe(diag, use_container_width=True, hide_index=True)

    if method.startswith("[B]"):
        st.success("""
        **🎯 새로운 발견 (팀원 원본에서 묻혔던 결과)**

        - **B3 모델 (VIX + F&G)**: VIX γ=+3.50, **p=0.040** ✱
          → 시장 공포(VIX) 가 BTC 변동성에 양의 영향이 통계적으로 유의.
        - **B4 모델 (공식 GPR + VIX + F&G)**: VIX γ=+7.56, **p=0.001** ✱✱✱ / 공식 GPR γ=−4.91 (borderline 음의 영향)
          → 시장 공포 통제 시 공식 GPR 은 오히려 BTC 변동성을 낮추는 방향.

        **팀원 원본은 alpha=0 경계 수렴으로 이 효과들을 p=0.82 로 잘못 측정했음.** 경계 수렴 해소가 결과를 완전히 바꿨다.
        """)

# ════════════════════════════════════════════════════════════
# 4. BTC 비거래일 로직 ablation
# ════════════════════════════════════════════════════════════
elif page == "🧪 BTC 비거래일 로직 ablation":
    st.title("BTC 비거래일 합산 로직 영향도 검증")
    st.markdown("""
    **수정 사항 (A1)**

    팀원 `master_data_결측치제거_v1.ipynb` 셀 #05 는 비표준 BTC 처리 로직을 사용:
    > 월요일 BTC 수익률 = (금 + 토 + 일) / 3 평균합산

    이 로직이 분포·자기상관·변동성에 미치는 영향을 정량 평가.
    """)

    st.subheader("두 시계열 분포 통계 비교")
    st.dataframe(btc_abl, use_container_width=True, hide_index=True)

    # 분포 시각화
    st.subheader("수익률 분포 비교 (Kernel Density)")
    fig = go.Figure()
    fig.add_trace(go.Histogram(x=btc_cmp['BTC_team'], name='팀원 (주말합산)',
                                opacity=0.6, marker_color='#F7931A', nbinsx=80, histnorm='probability density'))
    fig.add_trace(go.Histogram(x=btc_cmp['BTC_std'], name='표준 (NYSE 차분)',
                                opacity=0.6, marker_color='#1976D2', nbinsx=80, histnorm='probability density'))
    fig.update_layout(barmode='overlay', height=380, xaxis_title="일별 로그수익률",
                      yaxis_title="밀도", xaxis=dict(range=[-0.15, 0.15]))
    st.plotly_chart(fig, use_container_width=True)

    # 시계열 차이
    st.subheader("일별 차이 시계열 (팀원 − 표준)")
    btc_cmp['diff'] = btc_cmp['BTC_team'] - btc_cmp['BTC_std']
    fig2 = go.Figure()
    fig2.add_trace(go.Scatter(x=btc_cmp['date'], y=btc_cmp['diff'],
                              mode='lines', line=dict(color='#E91E63', width=0.8)))
    fig2.add_hline(y=0, line_color='black', line_width=0.6)
    fig2.update_layout(height=320, xaxis_title="날짜", yaxis_title="수익률 차이")
    st.plotly_chart(fig2, use_container_width=True)

    st.markdown("---")
    st.error("""
    **🔴 진단 결론**

    - 팀원 로직이 BTC **연환산 변동성을 15.5% 축소** (62.86% → 53.13%).
    - F-검정 p<0.0001 → 분산 차이 통계적으로 매우 유의.
    - Ljung-Box: 표준 BTC 는 lag10 자기상관이 유의(p=0.017). 팀원 로직이 이를 평탄화해서 자기상관 구조까지 왜곡.

    **영향**: GARCH·Quantile 결과가 모두 편향됐을 가능성. 표준 종가차분 방식으로 master_data 재생성 후 전체 파이프라인 재실행 필요 (Phase 2 다음 단계).
    """)

# ════════════════════════════════════════════════════════════
# 5. 수정 사항 요약
# ════════════════════════════════════════════════════════════
elif page == "📋 수정 사항 요약":
    st.title("수정 사항 종합 요약")
    st.markdown("""
    팀원 `fbghkdrb/2026_capstone` repo 의 분석에서 식별된 18개 후보 중 critical 4건을 수정.
    나머지 14건은 medium / low 우선순위.
    """)

    summary = pd.DataFrame([
        {"ID":"B1", "분류":"GARCH", "결함":"arch.arch_model 미사용, 커스텀 MLE 직접 작성",
         "수정":"arch 라이브러리 표준 구현 + 커스텀 MLE FIXED 양쪽 비교",
         "효과":"표준오차 신뢰성 확보. AIC 1087.02 (커스텀 FIXED), 1089.07 (arch lib)"},
        {"ID":"B2", "분류":"GARCH", "결함":"alpha=1e-6 경계 수렴 → t-stat=5000 같은 무의미 수치",
         "수정":"bound (1e-3, 0.5) + 다중 초기값 grid search 8회",
         "효과":"alpha=0.058~0.179 정상 추정"},
        {"ID":"B3", "분류":"GARCH", "결함":"omega=0 수렴, 분산 정의 위배",
         "수정":"bound (var_y*0.01, var_y*5) 강제 + 다중 초기값",
         "효과":"omega=12.66~13.41 정상 추정 + VIX γ p=0.040* 발견"},
        {"ID":"C1", "분류":"Event Study", "결함":"윈도우 ±25 → ±3 으로 일방 축소, 결과 희석",
         "수정":"±3, ±5, ±10, ±17 4개 윈도우 sensitivity",
         "효과":"이스라엘-하마스 Safe Haven 분류가 윈도우 의존이라는 진단 확보"},
        {"ID":"A1", "분류":"데이터", "결함":"BTC 주말 수익률을 월요일에 평균합산 (비표준)",
         "수정":"yfinance BTC 원시 종가 + NYSE 차분 표준 로그수익률 비교",
         "효과":"15.5% 변동성 축소·자기상관 왜곡 정량화"},
    ])
    st.dataframe(summary, use_container_width=True, hide_index=True)

    st.markdown("---")
    st.subheader("미수정 항목 (medium / low priority)")
    st.markdown("""
    | 분류 | ID | 항목 | 우선 |
    |---|---|---|---|
    | GARCH | B4 | GJR-GARCH / EGARCH 비대칭성 추가 | 🟡 medium |
    | GARCH | B5 | Hessian SE → BHHH-OPG sandwich 교체 | 🟡 |
    | GARCH | B6 | 표본 210 → returns.csv 1838 사용 + dummy interaction | 🟡 |
    | Event | C2 | NASDAQ 분석 자산 제외 (R²=0.85+로 의미 없음) | 🟡 |
    | Event | C3 | 35건 검정 → Bonferroni / FDR 보정 | 🟡 |
    | Event | C4 | Block size 3·5·7 sensitivity | 🟢 |
    | Quant | D1 | β_τ vs β_0.50 Wald 검정 추가 | 🟡 |
    | Quant | D3 | 이벤트별 회귀 폐지, returns.csv + dummy 사용 | 🟡 |
    | GPR | E1 | F1~F5 Vuong test 모델 선정 정당화 | 🟢 |
    | EDA | F1 | 이벤트 정의 통일 (5→6개) | 🟢 |
    """)

# ════════════════════════════════════════════════════════════
# 6. 방법론 · 수식
# ════════════════════════════════════════════════════════════
elif page == "📚 방법론·수식":
    st.title("방법론 · 수식")

    st.header("1. Event Study")
    st.latex(r"AR_t = R_t - E[R_t \mid \Omega_{t-}]")
    st.latex(r"CAR(t_1, t_2) = \sum_{t=t_1}^{t_2} AR_t")
    st.markdown("""
    - **추정 기간**: 이벤트 전 [-120, -26] 거래일 (95~120일)
    - **이벤트 윈도우**: ±3, ±5, ±10, ±17 거래일 sensitivity
    - **정상 수익률 모델**:
      - BTC: Market Model with NASDAQ 벤치마크 — $R_{BTC,t} = \\alpha + \\beta R_{NASDAQ,t} + \\epsilon_t$
      - Gold·DXY: CMRM (단순 평균) — $E[R_t] = \\bar{R}$
      - TLT·NASDAQ: Market Model with SP500
    - **검정**:
      - **BMP** (Boehmer-Musumeci-Poulsen): SAR = AR / σ_est, t = mean(SAR) / (std(SAR)/√T)
      - **Circular Block Bootstrap**: block=5, n_boot=5000, 추정기간 AR 에서 블록 샘플링
    """)

    st.header("2. GARCH-X")
    st.subheader("2-A) arch 라이브러리 (mean equation X)")
    st.latex(r"r_t = \mu + \sum_{k=1}^{K} \gamma_k X_{k,t} + \epsilon_t")
    st.latex(r"\sigma_t^2 = \omega + \alpha \epsilon_{t-1}^2 + \beta \sigma_{t-1}^2")
    st.latex(r"\epsilon_t \sim t_\nu")

    st.subheader("2-B) 커스텀 MLE (variance equation X) — 팀원 모델")
    st.latex(r"\sigma_t^2 = \omega + \alpha \epsilon_{t-1}^2 + \beta \sigma_{t-1}^2 + \sum_{k=1}^{K} \gamma_k X_{k,t-1}")
    st.markdown("""
    **수정**:
    - bound: $\\alpha \\in (10^{-3}, 0.5)$, $\\beta \\in (10^{-4}, 0.999)$, $\\omega \\in (\\hat{\\sigma}^2 \\cdot 0.01, \\hat{\\sigma}^2 \\cdot 5)$, $\\nu \\in (2.5, 30)$
    - 초기값: 8회 grid search, 최저 NLL 채택
    - SE: Hessian 수치미분 + sandwich 근사
    """)

    st.header("3. Quantile Regression (팀원 원본 유지)")
    st.latex(r"Q_\tau(R_{BTC,t} \mid X_t) = \alpha_\tau + \beta_\tau \cdot SP500_t^z + \gamma_\tau \cdot GPR_{custom,t}^z")
    st.markdown("""
    - 분위수: τ ∈ {0.05, 0.10, 0.25, 0.50, 0.75, 0.90, 0.95}
    - **Safe Haven 조건**: τ ≤ 0.10 에서 β_τ < 0, p < 0.05
    - 표준오차: vcov='robust' (Huber-White)
    - 최소 표본: min_n = 30 (effective_n = n×τ ≥ 5 경고)
    """)

    st.header("4. 다중 검정 보정 (미적용, 향후 과제)")
    st.markdown("""
    Event Study: 6 이벤트 × 5 자산 × 4 윈도우 = **120건 검정**.
    Bonferroni α* = 0.05 / 120 = 0.000417.
    또는 Benjamini-Hochberg FDR 적용 권장.
    """)

# ════════════════════════════════════════════════════════════
# 7. 학술 검증
# ════════════════════════════════════════════════════════════
elif page == "🎓 학술 검증":
    st.title("🎓 학술 검증 시스템")
    st.caption("`.claude/references/catalog.json` 표준 대비 자동 점검 결과")
    st.markdown("""
    이 페이지는 우리 분석 코드가 학술 표준 절차(MacKinlay 1997, Engle 2002, Koenker & Bassett 1978,
    Caldara & Iacoviello 2022, Politis & Romano 1994, Benjamini & Hochberg 1995, Baur & Lucey 2010)에
    부합하는지 자동 점검한 결과를 표시합니다.
    """)
    st.markdown("---")

    import glob
    REPO_ROOT = os.path.dirname(os.path.abspath(__file__))
    reports_dir = os.path.join(REPO_ROOT, '.claude', 'verification_reports')
    catalog_path = os.path.join(REPO_ROOT, '.claude', 'references', 'catalog.json')

    # ── 카탈로그 메타 ──
    if os.path.exists(catalog_path):
        with open(catalog_path, encoding='utf-8') as f:
            catalog = json.load(f)
        methods = [k for k in catalog if not k.startswith('_')]

        st.subheader("📚 학술 표준 카탈로그")
        cat_rows = []
        for m in methods:
            cat_rows.append({
                '방법론': m,
                '표준 논문': catalog[m]['paper'][:80] + ('...' if len(catalog[m]['paper']) > 80 else ''),
                'red_flags': len(catalog[m].get('red_flags', [])),
                'source_files': len(catalog[m].get('source_files', [])),
            })
        st.dataframe(pd.DataFrame(cat_rows), hide_index=True, use_container_width=True)
    else:
        st.warning("catalog.json 미발견. `.claude/references/catalog.json` 확인 필요.")
        catalog = None
        methods = []

    st.markdown("---")

    # ── 검증 보고서 ──
    st.subheader("📋 최근 검증 보고서")
    if os.path.exists(reports_dir):
        md_files = sorted(glob.glob(os.path.join(reports_dir, '*.md')), reverse=True)
        if not md_files:
            st.info("검증 보고서 없음. 노트북에서 검증 실행 후 `.claude/verification_reports/`에 저장됩니다.")
        for md_path in md_files:
            fname = os.path.basename(md_path)
            with st.expander(f"📄 {fname}", expanded=(md_path == md_files[0])):
                with open(md_path, encoding='utf-8') as f:
                    st.markdown(f.read())
    else:
        st.warning("verification_reports 폴더 미발견.")

    # ── 사이드바: 인용 ──
    if catalog and methods:
        st.sidebar.markdown("---")
        st.sidebar.subheader("📖 학술 표준 인용")
        for m in methods:
            kr = catalog[m].get('citation_kr', '')
            if kr:
                st.sidebar.caption(f"**{m}**\n\n{kr}")

st.sidebar.markdown("---")
st.sidebar.caption("Phase 1 진단 + Phase 2 critical 4건 수정")
st.sidebar.caption("산출물: `_review/results/` 9개 CSV + `_review/figures/`")
