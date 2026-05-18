# Event Study (MacKinlay 1997 표준)

## 표준 논문
MacKinlay, A. C. (1997). Event Studies in Economics and Finance. *Journal of Economic Literature*, 35(1), 13-39.

## 표준 절차 (MacKinlay 1997, §3-4)

1. **이벤트 정의**: 이벤트 날짜 t=0 명시
2. **추정창 (estimation window)**: [-T₁, -T₀], 보통 [-250, -11] 또는 [-120, -11]. 이벤트 직전 영향 차단을 위해 -11일까지.
3. **이벤트창 (event window)**: 보통 [-5, +5] 또는 [-1, +1]. 사전·사후 누출 검토.
4. **정상수익률 모델 추정**: Market Model이 표준 — `R_it = α_i + β_i·R_mt + ε_it` (시장은 보통 SP500). BTC 같이 시장모델 부적합 자산은 CMRM(Constant Mean Return Model) 사용 가능.
5. **Abnormal Return 계산**: `AR_it = R_it - (α̂_i + β̂_i·R_mt)`
6. **CAR (Cumulative Abnormal Return)**: 이벤트창 내 AR 합계
7. **유의성 검정**:
   - 전통 t-test: `t = CAR / (σ_AR · √n)`, σ_AR은 추정창에서 계산
   - 권장: Block Bootstrap 95% CI ([bootstrap.md](bootstrap.md) 참조)
8. **다중비교 보정**: 여러 이벤트 × 자산 조합 시 Bonferroni 또는 BH-FDR ([multiple_testing.md](multiple_testing.md))
9. **Placebo 검증**: 비이벤트 날짜에서 동일 절차 → CAR ≈ 0 기대

## 본 프로젝트 구현 위치

- `Edit_mj/이벤트_스터디_v2.ipynb`: 7개 이벤트 × 7개 자산
- `test/이벤트_스터디_v2.ipynb`: 동일 절차 테스트본
- `_review/scripts/02_event_study_sensitivity.py`: 추정창·이벤트창 길이 민감도 분석
- 결과: `_review/results/event_study_sensitivity.csv`, `event_study_summary_BTC_CAR.csv`, `event_study_summary_BTC_label.csv`

## 점검 체크리스트 (`/verify-event-study`가 자동 점검)

- [ ] 추정창 길이 ≥ 120 거래일
- [ ] 이벤트 날짜가 추정창 내부에 없음 (이벤트 간 추정창 겹치지 않게 격리)
- [ ] 이벤트창 [-5, +5] 또는 정당화된 변형
- [ ] BTC는 CMRM, 다른 자산은 Market Model 사용
- [ ] t-test와 Block Bootstrap 이중 검증
- [ ] Bonferroni 또는 BH-FDR 보정 적용
- [ ] Placebo 검증 포함

## 알려진 함정

1. **이벤트 클러스터링**: 이벤트가 시기적으로 가까우면 추정창이 다른 이벤트를 포함해 추정 편향 발생. 해결: 추정창에서 다른 이벤트 ±10일 제외 또는 추정창 시작점을 더 앞으로 이동.
2. **BTC 시장모델 부적합**: BTC와 SP500의 β가 시기별로 매우 불안정. 보통 CMRM 권장.
3. **Bonferroni 과도 보정**: 7×7=49 검정에 α*=0.001 적용 시 검정력 매우 낮음. 결론은 "BTC≠safe-haven"이 아니라 "유의미한 증거 부족"으로 해석해야.
4. **사후 분석 문제**: 이벤트창을 결과 보고 늘리거나 줄이는 행위 금지. 사전 등록 필수.

## 인용 (한국어)
> MacKinlay (1997, JEL 35:13-39)에 따른 표준 이벤트 스터디 절차

## BibTeX
```
@article{mackinlay1997event,
  title={Event studies in economics and finance},
  author={MacKinlay, A Craig},
  journal={Journal of economic literature},
  volume={35},number={1},pages={13--39},year={1997}
}
```
