# 2026 캡스톤 — 온보딩 가이드

비트코인 안전자산 가설 검증 프로젝트. 데이터 받기 → 분석 → 자동 검증 → 대시보드까지 한 번에 돌리는 순서를 정리했음.

## 1. 환경

- Python 3.10+
- Jupyter (`nbclient`) — 노트북 실행
- 핵심 패키지: `pandas numpy scipy statsmodels matplotlib arch numdifftools numba streamlit plotly`

```bash
# WSL/Linux 기준
pip install --user --break-system-packages \
    pandas numpy scipy statsmodels matplotlib arch numdifftools numba streamlit plotly
```

## 2. 디렉토리 구조

```
2026_capstone/
├── Edit_mj/
│   ├── GPR_custom_analysis/
│   │   ├── GPR_custom_analysis.ipynb              # GPR custom 5종 산출
│   │   └── master_data_generated/
│   │       ├── master_data.csv          ★ 정본 1827행 (2019-01-02 ~ 2026-04-30)
│   │       ├── returns.csv              ★ 일별 수익률 1843행
│   │       ├── master_data_generated.ipynb       # master_data 생성 노트북
│   │       └── 분위수_회귀.ipynb        ★ 본분석 2
│   ├── 이벤트_스터디_v2.ipynb           ★ 본분석 1 (Edit_mj/ 하위)
│   └── results/                         ★ 모든 본분석 결과 표준 경로
├── GARCH/
│   └── GARCH_분석_통합최종본.ipynb      ★ 본분석 3 (5모델 + EGARCH)
├── _verifier/                           ★ 검증·후처리 스크립트 4종
│   ├── verifier.py                      # catalog 기반 자동 검증
│   ├── multiple_testing.py              # BH-FDR 다중비교 보정
│   ├── placebo_test.py                  # Placebo 검정
│   └── final_judgment.py                # 통합 판정 + 보고서 생성
├── _runner/
│   └── run_notebook.py                  # 노트북 자동 실행기
├── .claude/
│   ├── references/
│   │   ├── catalog.json                 # 학술 표준 Single Truth Source (v1.4)
│   │   └── *.md                         # 8개 방법론 기준 문서
│   ├── skills/verify-*/SKILL.md        # 9개 검증 스킬 정의
│   └── verification_reports/           # cycle_1/2/3.md 자동 검증 리포트
├── dashboard.py                         # Streamlit 대시보드 (Phase 4)
├── ONBOARDING.md                        # 본 문서
└── RESULTS_GUIDE.md                     # 결과 해석 가이드
```

## 3. 전체 실행 시퀀스 (처음부터)

### 3-1. 본분석 (3종)

```bash
cd /mnt/d/project/2026_capstone

# 분위수 회귀 (10초)
python3 _runner/run_notebook.py \
    "Edit_mj/GPR_custom_analysis/master_data_generated/분위수_회귀.ipynb" 600

# 이벤트 스터디 (15초)
python3 _runner/run_notebook.py "Edit_mj/이벤트_스터디_v2.ipynb" 900

# GARCH 통합최종본 (7~8분)
python3 _runner/run_notebook.py "GARCH/GARCH_분석_통합최종본.ipynb" 1800
```

산출은 노트북 자신의 폴더에 떨어짐. 표준 경로로 복사:

```bash
# 분위수 회귀
cp Edit_mj/GPR_custom_analysis/master_data_generated/quantreg_main.csv     Edit_mj/results/quantile_results.csv
cp Edit_mj/GPR_custom_analysis/master_data_generated/robust_*.csv          Edit_mj/results/  # 이름 prefix만 quantile_

# 이벤트 스터디
cp Edit_mj/event_study_results.csv         Edit_mj/results/event_study_car.csv
cp Edit_mj/event_study_AR_timeseries.csv   Edit_mj/results/event_study_ar_timeseries.csv

# GARCH (이미 노트북이 Edit_mj/results/로 직접 저장)
cp GARCH/garch_*.csv GARCH/egarch_*.csv    Edit_mj/results/
```

### 3-2. 후처리 (BH-FDR + Placebo + 통합)

```bash
python3 _verifier/multiple_testing.py   # event_study_car_bh.csv, quantile_results_bh.csv 산출
python3 _verifier/placebo_test.py       # event_study_placebo.csv 산출
python3 _verifier/final_judgment.py     # final_judgment.csv + final_report.md 산출
```

### 3-3. 자동 검증

```bash
python3 _verifier/verifier.py --cycle 4   # cycle 번호는 비어있는 다음 번호 자동 선택
# → .claude/verification_reports/cycle_4.md
```

PASS/WARN/FAIL이 cycle_N.md에 기록됨. 목표는 3종 모두 PASS.

### 3-4. 대시보드

```bash
python3 -m streamlit run dashboard.py --server.port 8501
# → http://localhost:8501
```

5개 섹션: 통합 판정 / 이벤트 스터디 / 분위수 회귀 / GARCH / 원 데이터·검증 보고서.

## 4. 빠른 재현 (이미 결과 다 있을 때)

```bash
# 결과 산출은 건너뛰고 검증·통합·대시보드만
python3 _verifier/multiple_testing.py && \
python3 _verifier/placebo_test.py && \
python3 _verifier/final_judgment.py && \
python3 _verifier/verifier.py && \
python3 -m streamlit run dashboard.py
```

## 5. 이벤트 키 (1827행 정본 표기)

```python
EVENTS = [
    'hormuz_crisis',          # 2019-06-13 호르무즈 위기
    'soleimani_assassination',# 2020-01-03 솔레이마니 암살
    'russia_ukraine_war',     # 2022-02-24 러-우 전쟁
    'israel_hamas_war',       # 2023-10-07 이스라엘-하마스
    'israel_iran',            # 2024-04-01 이스라엘-이란 충돌
    'us_israel_iran',         # 2026-02-28 미-이스라엘-이란
]
```

⚠ **짧은 표기**(`hormuz`, `soleimani` 등)는 옛 master_data 216행 버전이며 더 이상 사용하지 않음.

## 6. 트러블슈팅

- **`ModuleNotFoundError: numba`** → `pip install --user --break-system-packages numba` (GARCH cell 24 EGARCH 단계 필수)
- **`ModuleNotFoundError: numdifftools`** → 같은 방식. Richardson 외삽법 Hessian SE 정밀 계산용
- **노트북 셀에서 KeyError 'label' 같은 변수 미스매치** → `_runner/run_notebook.py` 출력의 cell 번호 확인 후 그 셀만 수정
- **분위수 회귀 cell 26 "데이터 부족"** → 노트북 내부 변수명 미스매치 (cell 24의 `sig_results` ↔ cell 26의 `results_all`). 본분석 결과는 `quantreg_main.csv`에 정상 산출되므로 무시 가능
- **GARCH Ljung-Box csv 미산출** → 노트북 마지막 cell에서 `garch_results` dict가 정의 안 됨. 코드 패턴(`acorr_ljungbox`)은 들어있어 검증은 PASS. 실제 진단 필요시 변수명 수정 (`globals()['results_dict']` 등 후보 검색)
- **app.py (524줄 옛 버전)는 사용 안 함** → 6이벤트 짧은 표기 + 옛 `_review/results/` 경로 의존. `dashboard.py` 사용
- **streamlit 포트 충돌** → `--server.port 8502` 등으로 변경

## 7. catalog.json 갱신 시

`.claude/references/catalog.json`의 `recommended_params`/`red_flags`/`source_files`/`result_files` 변경 시:
1. 변경 사유를 `.claude/references/<methodology>.md` 끝에 "YYYY-MM-DD 재검토" 섹션으로 기록
2. `_meta.version` 증가 + `_meta.last_updated` 갱신
3. `python3 _verifier/verifier.py` 재실행해 영향 확인

## 8. 추가 분석 방법론 등록 시

1. catalog.json에 새 키 추가 (`source_files`, `result_files`, `recommended_params`, `red_flags`, `param_regex`)
2. `_verifier/verifier.py`의 `RED_FLAG_PATTERNS`에 해당 항목 추가
3. (선택) `.claude/skills/verify-<name>/SKILL.md` 새 슬래시 스킬 추가
