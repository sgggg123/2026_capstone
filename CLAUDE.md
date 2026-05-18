# 2026_capstone — 비트코인 안전자산 가설 검증

## 프로젝트 핵심
GDELT 톤 + FinBERT 감성 + Caldara-Iacoviello GPR을 결합한 **Hybrid GPR 지수**로 6개 지정학·안보 이벤트에서 비트코인이 안전자산 역할을 했는지 검증한다. 분석 도구: Event Study, DCC-GARCH, Quantile Regression, Stationary Bootstrap, Multiple Testing 보정, Baur-Lucey safe-haven 프레임워크.

## 통일된 이벤트 키 (필수)
모든 코드/데이터에서 다음 키만 사용한다 (총 6개, **1827행 정본 master_data 표기**):
`hormuz_crisis`, `soleimani_assassination`, `russia_ukraine_war`, `israel_hamas_war`, `israel_iran`, `us_israel_iran`

⚠ **2026-05-18 변경**: 옛 짧은 표기(`hormuz`, `soleimani`, `israel_iran_war`, `us_israel_iran_war`)는 216행 master_data 시절의 잔재. 1827행 정본 채택 이후 폐기. 옛 표기를 발견하면 긴 표기로 통일하라.

**범위 주의**: COVID-19는 본 분석 범위에서 의도적 제외. 지정학 이벤트가 아니며 동학이 다름. 검증·보고서·시각화 어디에도 covid를 추가하지 말 것.

## 학술 인용 의무
1. 통계 결론을 진술할 때마다 `.claude/references/catalog.json`에서 해당 방법론의 `citation_kr`을 첨부한다. 빠르게 가져오려면 `/cite-method <메서드명>`.
2. 분위 임계값 τ, 추정창 길이, 이벤트창, 블록크기, BH-FDR α* 등 핵심 파라미터를 변경할 때는 변경 전후 값을 커밋 메시지·PR 본문에 명시한다. catalog.json의 `recommended_params`와 비교 근거를 함께.
3. 새 통계 방법론을 도입할 때는 `.claude/references/<method>.md`를 코드 작성보다 **먼저** 추가한다.
4. "BTC는 (강한/약한) safe haven이다/아니다" 같은 결론을 쓰기 전에 `python3 _verifier/final_judgment.py`를 실행해 Baur & Lucey (2010) 3조건 통합 판정을 확인한다.

## 검증 시스템 사용법
- **자동 검증**: `python3 _verifier/verifier.py [--cycle N] [--methodology <name>]` → `.claude/verification_reports/cycle_N.md` 생성
- **후처리**: `python3 _verifier/multiple_testing.py` (BH-FDR), `python3 _verifier/placebo_test.py`, `python3 _verifier/final_judgment.py`
- **슬래시 스킬**: `.claude/skills/verify-*/SKILL.md` 정의 (수동 실행 가이드)
- **검증 보고서**: `.claude/verification_reports/cycle_{1,2,3}.md`에 자가 피드백 사이클별 누적

## 노트북 작성 규칙
- 새 셀에서 통계 절차를 시작할 때 첫 줄에 `# METHOD: <name>` 주석. (예: `# METHOD: event_study`). 이는 검증 스킬이 셀 단위로 매핑할 때 사용.
- 파라미터는 셀 상단에 모듈 변수처럼 모아서 정의 (`EST_START = -120`, `TAUS = [0.05, 0.10]`). 함수 내부 매직 넘버 금지.
- 노트북 결과 CSV는 `Edit_mj/results/`에 표준 이름으로 출력 (catalog.json `result_files` 키 참조).

## 데이터 위치 (절대 경로 기준)
- **정본 마스터**: `Edit_mj/GPR_custom_analysis/master_data_generated/master_data.csv` (1827행, 2019-01-02 ~ 2026-04-30)
- **정본 수익률**: `Edit_mj/GPR_custom_analysis/master_data_generated/returns.csv` (1843행)
- **본분석 노트북** (Phase 1 확정):
  - 이벤트 스터디: `Edit_mj/이벤트_스터디_v2.ipynb`
  - 분위수 회귀: `Edit_mj/GPR_custom_analysis/master_data_generated/분위수_회귀.ipynb`
  - GARCH: `GARCH/GARCH_분석_통합최종본.ipynb` (5모델 + EGARCH 강건성)
- **표준 결과**: `Edit_mj/results/` (catalog.json `result_files` 기준)
- **검증·후처리**: `_verifier/{verifier, multiple_testing, placebo_test, final_judgment}.py`
- **노트북 실행기**: `_runner/run_notebook.py`
- **대시보드**: `dashboard.py` (Streamlit, 5 섹션)
- **팀 문서**: `ONBOARDING.md`, `RESULTS_GUIDE.md`

⚠ 옛 위치 (`Edit_mj/master_data.csv` 216행, `Edit_mj/분위수_회귀.ipynb`, `Edit_mj/GARCH_분석.ipynb`, `_review/`, `test/`)는 더 이상 본분석에 사용 안 함. 참조 시 신경로로 마이그레이션할 것.

## 응답 언어
한국어로 답한다. 학술 용어는 원어 병기 (예: 정상성(stationarity)).
