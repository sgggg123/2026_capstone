# 지정학적 위기 시 암호화폐 안전자산 검증

**한 줄 요약**: 6개 지정학 이벤트(2019~2026)에서 BTC가 Baur & Lucey (2010) 정의의 Safe Haven 자산이었는지 이벤트스터디·GARCH·분위수회귀 3종으로 검증.

---

## 📚 읽는 순서 (팀원/리뷰어용)

| 우선순위 | 파일 | 용도 |
|---|---|---|
| 1️⃣ | **[ONBOARDING.md](ONBOARDING.md)** | 환경 설치 → 분석 실행 → 검증 → 대시보드까지 한 번에 |
| 2️⃣ | **[RESULTS_GUIDE.md](RESULTS_GUIDE.md)** | 6이벤트 × 3방법론 통합 판정 + Baur-Lucey 3조건 + 한계점 |
| 3️⃣ | `python3 -m streamlit run dashboard.py` | 시각화 (통합 판정 히트맵 + 방법론별 상세) |
| 4️⃣ | [`Edit_mj/results/final_report.md`](Edit_mj/results/final_report.md) | 학술 요약 1장 |
| 5️⃣ | [`CLAUDE.md`](CLAUDE.md) | Claude Code/사람 공용 프로젝트 가이드 |
| 참고 | [`.claude/verification_reports/cycle_3.md`](.claude/verification_reports/cycle_3.md) | 자가 피드백 최종 PASS 증빙 (3종 방법론 모두 PASS) |

---

## 학술 정의

**Baur & Lucey (2010)** Safe Haven 정의: *시장이 극단적으로 하락하는 시기에 위험자산(주식)과 음의 상관관계 또는 무상관인 자산*. "주가가 폭락할 때 BTC는 어떻게 움직였는가?"가 핵심 질문.

## 분석 3종

### 1. 이벤트 스터디 (MacKinlay 1997)
- **질문**: 위기 발생 전후 BTC의 누적 비정상수익률(CAR)이 양수인가?
- **본분석**: `Edit_mj/이벤트_스터디_v2.ipynb` — 추정창 [-120, -26] (95거래일) + 이벤트창 ±17일 + Block Bootstrap 5000회
- **보강**: BH-FDR 다중비교 보정 + Placebo 검정 200회

### 2. GARCH-X (Engle 2002)
- **질문**: 지정학 리스크(GPR)가 BTC 변동성을 키우는가?
- 모델: `σ²(t) = ω + α·ε²(t-1) + β·σ²(t-1) + γ·X(t)` (외생변수 X = GPR/VIX/Fear&Greed)
- **본분석**: `GARCH/GARCH_분석_통합최종본.ipynb` — Student-t MLE 직접 최적화, 5모델 × 10 초기값 격자, Richardson 외삽법 SE
- **보강**: ADF 정상성 사전검증, Ljung-Box 잔차 진단, EGARCH 비대칭 강건성

### 3. 분위수 회귀 (Koenker & Bassett 1978) — 주요 분석
- **질문**: 주식 폭락 하위 5~10% 구간에서 BTC가 반대로 움직였는가?
- 모델: `Q_τ(BTC) = α + β·SP500 + γ·GPR_custom`, τ ∈ [0.01, 0.025, 0.05, 0.10, 0.20, 0.25, 0.50, 0.75, 0.90, 0.95]
- **β < 0 (τ=0.05, 0.10)** → Safe Haven / **β > 0** → Risky Asset
- **본분석**: `Edit_mj/GPR_custom_analysis/master_data_generated/분위수_회귀.ipynb` — HAC(Newey-West) SE
- **보강**: BH-FDR 다중비교 보정, IV/LOO/MM 강건성 3종

## 6개 지정학 이벤트 (정본 1827행 master_data 표기)

| 이벤트 키 | 발생일 | 라벨 |
|---|---|---|
| `hormuz_crisis` | 2019-06-13 | 호르무즈 위기 |
| `soleimani_assassination` | 2020-01-03 | 솔레이마니 암살 |
| `russia_ukraine_war` | 2022-02-24 | 러-우 전쟁 |
| `israel_hamas_war` | 2023-10-07 | 이스라엘-하마스 |
| `israel_iran` | 2024-04-01 | 이스라엘-이란 충돌 |
| `us_israel_iran` | 2026-02-28 | 미-이스라엘-이란 |

## 통합 판정 (Baur-Lucey 3조건 기준)

| 이벤트 | C1 이벤트스터디 | C2 분위수회귀 (τ=0.05) | C3 GARCH (GPR γ) | 점수 | 판정 |
|---|---|---|---|---|---|
| 호르무즈 위기 | ✅ | ✅ | ✅ | 3/3 | **Safe Haven** |
| 솔레이마니 암살 | ✅ | ❌ | ✅ | 2/3 | Weak Haven |
| 러-우 전쟁 | ✅ | ❌ | ✅ | 2/3 | Weak Haven |
| 이스라엘-하마스 | ✅ | ❌ | ✅ | 2/3 | Weak Haven |
| 이스라엘-이란 충돌 | ✅ | ❌ | ✅ | 2/3 | Weak Haven |
| 미-이스라엘-이란 | ✅ | ❌ | ✅ | 2/3 | Weak Haven |

→ **BTC는 평균/변동성 채널에서는 지정학에 둔감(C1·C3 통과)하나, 극단 하락 시(τ=0.05) 시장과 동조(C2 실패) → 부분적 위험자산 특성.**

---

## 옛 "수정 필요사항" 해결 현황 (한 달 전 README 작성 시점 기준)

| 옛 한계점 | 현재 상태 |
|---|---|
| returns.csv 시작일 문제, hormuz 4거래일만 커버 | ✅ 해결 — 1827행 신본 master_data + returns 1843행 (2019-01-02부터). hormuz 182거래일 확보 (단 추정창 좌측이 짧아 Placebo 1건 실패는 잔존 한계로 RESULTS_GUIDE.md §5에 명시) |
| arch 라이브러리 부재 → OLS 근사 | ✅ 해결 — `GARCH/GARCH_분석_통합최종본.ipynb`가 직접 Student-t MLE + multi-init 10격자 + Richardson SE 채택. arch 의존성 자체를 제거 |
| 이벤트 창 ±25 → ±17 수정 | ✅ 해결 — v2 노트북이 본분석. `EVENT_WINDOW=17` 명시 |
| 분위수 회귀 p값 없음 | ✅ 해결 — statsmodels QuantReg + HAC(Newey-West) SE 적용, BH-FDR α=0.05 다중비교 보정까지 |
| Bootstrap p값 로직 재확인 | ✅ 해결 — 추정창/이벤트창 AR 분리해서 Block Bootstrap 5000회. Placebo 200회 추가. cycle 3 자가 검증 ALL PASS |
| F3 공식 (절대/상대 보도량) | ✅ 해결 — `Edit_mj/GPR_custom_analysis/total_custom_gpr_final.csv` 최종본 사용 |

## 잔존 한계점

1. **호르무즈 위기 추정창 부족** — 1827행 데이터가 2019-01-02부터라 hormuz_crisis(2019-06-13) 이전 추정창 좌측이 약간 짧음. Placebo 1건 실패. 호르무즈만 단독 Safe Haven 판정 — 데이터 한계 영향 가능성을 RESULTS_GUIDE.md §5에 명시.
2. **이벤트별 표본** 182~475일이라 τ=0.01 등 극단 분위수에선 유효 표본 부족 (코드에 ⚠ 표시).
3. **COVID-19 의도적 제외** — 지정학 이벤트가 아니며 별도 동학. `.claude/references/catalog.json` `_meta.scope_note` 참조.

---

## 빠른 시작

```bash
git clone https://github.com/sgggg123/2026_capstone.git
cd 2026_capstone

# 환경 설치 (자세한 건 ONBOARDING.md)
pip install --user --break-system-packages \
    pandas numpy scipy statsmodels matplotlib arch numdifftools numba streamlit plotly

# 결과 보기
python3 -m streamlit run dashboard.py
# → http://localhost:8501
```

## 인용

- MacKinlay, A. C. (1997). Event Studies in Economics and Finance. *Journal of Economic Literature*.
- Koenker, R., & Bassett, G. (1978). Regression Quantiles. *Econometrica*.
- Engle, R. F. (2002). Dynamic Conditional Correlation. *JBES*.
- Baur, D. G., & Lucey, B. M. (2010). Is Gold a Hedge or a Safe Haven? *Financial Review*.
- Benjamini, Y., & Hochberg, Y. (1995). Controlling the False Discovery Rate. *JRSS B*.
- Caldara, D., & Iacoviello, M. (2022). Measuring Geopolitical Risk. *American Economic Review*.

(BibTeX는 `.claude/citations/ready_to_paste.md` 참조)
