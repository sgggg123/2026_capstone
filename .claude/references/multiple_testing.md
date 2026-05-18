# Multiple Testing Correction

## 표준 논문
- Benjamini, Y., & Hochberg, Y. (1995). Controlling the False Discovery Rate: A Practical and Powerful Approach to Multiple Testing. *JRSSB*, 57(1), 289-300.
- Bonferroni, C. E. (1936). Teoria statistica delle classi e calcolo delle probabilità.

## 표준 절차

**문제**: m개 검정을 동시에 수행하면 family-wise error (FWER)가 누적. 7 이벤트 × 7 자산 = 49 검정에서 α=0.05 단순 적용 시 family-wise α ≈ 1 - (1-0.05)^49 ≈ 0.92 → 거짓 발견 거의 확실.

**Bonferroni (1936)**
- α* = α / m
- FWER ≤ α 보장 (보수적)
- m이 크면 검정력 매우 낮음

**Benjamini-Hochberg FDR (1995)**
1. p-value 오름차순 정렬: `p_(1) ≤ p_(2) ≤ ... ≤ p_(m)`
2. 가장 큰 k 찾기: `p_(k) ≤ (k/m) · q`
3. p_(1), ..., p_(k) 모두 기각
- E[FDR] ≤ q 보장 (덜 보수적, 검정력 우월)

**언제 무엇을 쓰나**
- 안전 우선 (의약품, 인과 주장): Bonferroni
- 발견 지향 (탐색적 분석, 다수 신호 검출): BH-FDR
- 검정 간 강한 양의 의존: BY (Benjamini-Yekutieli) 보정

## 본 프로젝트 적용

49 검정 (7 이벤트 × 7 자산):
- Bonferroni: α* = 0.05 / 49 ≈ 0.00102
- BH-FDR (q=0.05): 가변 (관측 p-value 분포에 의존)

## 본 프로젝트 구현 위치
- `Edit_mj/이벤트_스터디_v2.ipynb`: CAR p-value 보정
- `_review/scripts/02_event_study_sensitivity.py`
- 결과: `_review/results/event_study_summary_BTC_CAR.csv`, `event_study_summary_BTC_label.csv`

## 점검 체크리스트 (`/verify-multiple-testing`이 자동 점검)

- [ ] 검정 가족(family) 수 m이 명시됨
- [ ] Bonferroni 또는 BH-FDR 적용
- [ ] 보정 방법 선택 사유 명시
- [ ] 보정 후 결론을 "유의 결과 부재 = 효과 없음"으로 오역하지 않음

## 알려진 함정

1. **보정 미적용**: 49개 중 1개만 p < 0.05라고 "유의 발견" 주장 시 거짓.
2. **Bonferroni 결과를 강하게 해석**: Bonferroni는 매우 보수적. α* 미달이라고 "BTC는 안전자산이 아니다"라고 단정하면 검정력 부족 가능 (Type II error).
3. **사후 family 변경**: 분석 후 검정 가족을 좁혀(예: 7→3 자산) p-value 보정 강도 낮추는 행위 (p-hacking). 가족은 사전 등록 필수.
4. **BH-FDR + 음의 의존성**: BH는 양의 의존성에 안전, 음의 의존성에서는 BY 보정 권장.
5. **분위회귀에서의 다중검정**: τ = {0.05, 0.10, 0.50} 3개 분위 × 7 이벤트도 별도 family. 누락 흔함.

## 인용 (한국어)
> Benjamini & Hochberg (1995, JRSSB 57:289-300) FDR 보정; Bonferroni (1936) FWER 보정

## BibTeX
```
@article{benjamini1995controlling,title={Controlling the false discovery rate},author={Benjamini, Yoav and Hochberg, Yosef},journal={JRSSB},volume={57},number={1},pages={289--300},year={1995}}
```
