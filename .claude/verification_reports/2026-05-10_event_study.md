# 검증 보고서: 이벤트 스터디

- **일자**: 2026-05-10 (재실행)
- **기준**: MacKinlay (1997, JEL 35:13-39); `.claude/references/event_study.md`
- **카탈로그**: `.claude/references/catalog.json#event_study`
- **검증 대상**:
  - `Edit_mj/이벤트_스터디_v2.ipynb` (메인 분석)
  - `test/이벤트_스터디_v2.ipynb` (대조군)
  - `_review/scripts/02_event_study_sensitivity.py` (민감도)
  - 결과: `_review/results/event_study_sensitivity.csv` (121행), `event_study_summary_BTC_CAR.csv` (7행), `event_study_summary_BTC_label.csv` (7행)

## 항목별 판정

| # | 항목 | 검출값 | 판정 | 비고 |
|---|---|---|---|---|
| 1 | 추정창 길이 | EST_START=-120, EST_END=-26 → **95 거래일** (Edit_mj·test·_review 동일) | ❌ **FAIL** | rubric `<100=FAIL`. 26거래일 사전 차단(통상 11) 때문에 짧아짐 |
| 2 | 이벤트창 (EVENT_WINDOW) | 메인 ±17, 민감도 [3, 5, 10, 17] | ⚠️ WARN | 표준 ±5/±10 아님. 민감도 분석으로 부분 정당화 — 사유 마크다운 셀 명시 권장 |
| 3 | BTC 모델 | Edit_mj `CMRM_ASSETS=['Gold','DXY']` → BTC=**MM(NASDAQ)**; test `CMRM_ASSETS=['BTC']` → BTC=CMRM | ⚠️ WARN | 메인 분석에서 BTC가 catalog 권장(CMRM)과 다름. 노트북에 R²≈0 사유 명시 있음(L387). 검증 대조군과 모델 불일치 — 둘 중 하나로 통일 또는 양쪽 결과 병기 필요 |
| 4 | Bootstrap (메인) | `bootstrap_block_car(n_boot=5000, block_size=5, seed=42)` (Edit_mj, _review) | ✅ PASS | n≥1000 충족, block bootstrap, 시드 고정 |
| 4b | Bootstrap (대조군) | test/`bootstrap_car` = `rng.choice(replace=True)` → **iid** bootstrap | ⚠️ WARN | 시계열 자기상관 무시. 메인은 block으로 수정됨 (Edit_mj L814 명시). test 노트북도 동기화 필요 |
| 5 | block_size 정당화 | `block_size=5` 고정, Politis-White 자동선택 미사용 | ⚠️ WARN | 자기상관 길이 기반 근거 또는 자동선택으로 교체 권장 |
| 6 | 다중비교 보정 | `bonferroni`/`fdr`/`benjamini`/`hochberg`/`multipletests` 키워드 **0건** (3개 파일 전체) | ❌ **FAIL** | 7 이벤트 × 5 자산 = 35 검정에 보정 미적용. catalog `red_flags` 직접 위배 |
| 7 | Placebo 검증 | `placebo`/`fake_event`/`random_dates` 키워드 **0건** | ❌ **FAIL** | MacKinlay (1997) §4 표준 절차 누락 |
| 8 | 통일 이벤트 키 (소스) | Edit_mj·test·_review 모두 6키 (hormuz·soleimani·russia_ukraine_war·israel_hamas_war·israel_iran_war·us_israel_iran_war) 일관 사용 | ✅ PASS | 분석 범위 내 모든 이벤트 커버. COVID-19는 의도적 제외 (지정학 이벤트 아님) |
| 9 | 통일 이벤트 키 (결과) | `event_study_sensitivity.csv`(2026-05-02) 옛 키 잔존: hormuz_crisis, soleimani_assassination, russia_ukraine_invasion, israel_hamas, israel_iran, us_israel_iran | ❌ **FAIL** | 스크립트는 통일 키지만 CSV는 stale. 재실행 후 덮어쓰기 필요 |
| 10 | 결과 csv 무결성 | sensitivity 121행×9열, summary 각 7행×5열 | ✅ PASS | 파일 존재·행수 정합 |

## 종합

| 결과 | 개수 |
|---|---|
| ✅ PASS | 2 |
| ⚠️ WARN | 5 |
| ❌ FAIL | 4 |

## 즉시 조치 필요 (FAIL)

1. **다중비교 보정 미적용** (항목 6)
   - 35개 검정 → α* = 0.05/35 ≈ 0.00143 (Bonferroni) 또는 BH-FDR q=0.05 적용
   - `Edit_mj/이벤트_스터디_v2.ipynb` 결과 표에 `p_bonf`, `q_fdr` 컬럼 추가
   - `statsmodels.stats.multitest.multipletests` 사용

2. **Placebo 검증 누락** (항목 7)
   - 비이벤트 날짜 5~10개 무작위 선정 → 동일 추정/이벤트창 적용
   - CAR 분포가 0 근처 + p > α* 확인 → 절차 신뢰성 입증
   - 별도 셀 (`# METHOD: event_study_placebo`) 추가 권장

3. **추정창 95거래일** (항목 1)
   - 옵션 A: EST_END을 -11로 변경 → 110거래일 (WARN 진입)
   - 옵션 B: EST_START을 -135으로 확장 → 110거래일
   - 옵션 C: 26거래일 사전 차단의 사유(이벤트 직전 정보 누출 우려 등)를 catalog `recommended_params`에 추가하여 의도된 변형으로 등록

4. **결과 CSV stale** (항목 9)
   - `_review/scripts/02_event_study_sensitivity.py` 재실행 → `event_study_sensitivity.csv` 덮어쓰기
   - 통일 키로 재생성 후 git commit

## 검토 권유 (WARN)

1. **이벤트창 ±17** — 민감도 분석은 있으나 메인 결과 보고 시 ±17 채택 사유(예: master_data 이벤트별 평균 ±17 거래일 보장) 노트북 마크다운에 명시
2. **BTC 모델 불일치** — Edit_mj(MM(NASDAQ)) vs test(CMRM) 불일치 해소. 두 모델 결과 차이 표로 보고하거나 한쪽으로 통일
3. **block_size=5 고정** — Politis & White (2004) 자동선택 또는 ACF 기반 정당화 1줄 추가
4. **test 노트북 iid bootstrap** — Edit_mj와 동일한 block bootstrap으로 동기화

## 인용

> MacKinlay (1997, JEL 35:13-39)에 따른 표준 이벤트 스터디 절차

```bibtex
@article{mackinlay1997event,title={Event studies in economics and finance},author={MacKinlay, A Craig},journal={Journal of economic literature},volume={35},number={1},pages={13--39},year={1997}}
```

상세 점검 항목: `.claude/references/event_study.md`
