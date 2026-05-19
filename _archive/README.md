# _archive/ — 옛 작업본 모음 (본분석 비참조)

2026-05-19 정리 시점에 ONBOARDING.md §2 정본 구조에 들어가지 않는 파일을 모았다. **참고용으로만 보관**한다. 현재 분석 파이프라인(`dashboard.py`, `_verifier/*.py`, catalog.json `source_files`)은 이 폴더를 일체 참조하지 않는다.

## 폴더 구조

| 폴더 | 내용 |
|---|---|
| `notebooks_root/` | 루트에 흩어져 있던 옛 분석/시연 노트북 10개 (216행 master_data 시절) |
| `docs_root/` | 옛 발표대본·작업정리·시연 대본 등 한시적 문서 7개 + `검증패키지_2026_capstone.zip` |
| `legacy_dirs/test/` | 옛 본분석 대조군 노트북 3개 — 현재 본분석은 `Edit_mj/이벤트_스터디_v2.ipynb`·`GARCH/GARCH_분석_통합최종본.ipynb`·`Edit_mj/GPR_custom_analysis/master_data_generated/분위수_회귀.ipynb` |
| `legacy_dirs/_review/` | 옛 발표·공유용 자료 (브리핑 대본, `공유용_분석노트북.ipynb`, scripts, results, figures) |
| `legacy_dirs/new/` | 원시 크롤링 csv 4개 (마스터 데이터 통합 전 단계) |
| `app_old/app.py` | 옛 524줄 Streamlit 대시보드 — `dashboard.py`가 후속본 |
| `edit_mj_legacy/` | Edit_mj/ 루트에 남아있던 216행 master_data·옛 노트북·.bak |

## 정본 위치 (현재 분석은 여기로만)

| 자료 | 경로 |
|---|---|
| master_data | `Edit_mj/GPR_custom_analysis/master_data_generated/master_data.csv` (1827행) |
| returns | `Edit_mj/GPR_custom_analysis/master_data_generated/returns.csv` (1843행) |
| 이벤트 스터디 | `Edit_mj/이벤트_스터디_v2.ipynb` |
| 분위수 회귀 | `Edit_mj/GPR_custom_analysis/master_data_generated/분위수_회귀.ipynb` |
| GARCH | `GARCH/GARCH_분석_통합최종본.ipynb` |
| 결과 csv | `Edit_mj/results/` |
| 대시보드 | `dashboard.py` |

## 복원

git 추적본은 `git mv` 했으므로 `git log --follow -- _archive/<path>` 로 히스토리가 살아있다. 옛 위치로 되돌리려면 `git mv _archive/<...> <원래경로>` 만 하면 된다.
