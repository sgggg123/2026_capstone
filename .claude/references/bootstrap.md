# Stationary Bootstrap (Politis & Romano 1994)

## 표준 논문
- Politis, D. N., & Romano, J. P. (1994). The Stationary Bootstrap. *Journal of the American Statistical Association*, 89(428), 1303-1313.
- Politis, D. N., & White, H. (2004). Automatic block-length selection for the dependent bootstrap. *Econometric Reviews*, 23(1), 53-70.

## 표준 절차 (Politis & Romano 1994 §2)

**문제**: iid bootstrap은 시계열 자기상관을 깨뜨려 표준오차를 과소평가.

**해결: Stationary Bootstrap**
1. 각 부트스트랩 표본은 무작위 길이 블록의 연결
2. 블록 길이는 평균 1/p의 기하분포 (p ∈ (0,1])
3. 결과 시계열은 strict stationary

**자동 블록 선택 (Politis & White 2004)**
- 자기상관함수 기반 최적 평균 블록 길이 추정
- Python `arch.bootstrap.optimal_block_length` 사용 가능

**Block Bootstrap CI**
- Percentile: `[Q_{0.025}, Q_{0.975}]`
- BCa (bias-corrected accelerated): 편향과 가속도 보정. 정확도 우월.

## 본 프로젝트 구현 위치
- `Edit_mj/이벤트_스터디_v2.ipynb`: CAR 유의성 검정용 부트스트랩
- `Edit_mj/GARCH_분석.ipynb`: 파라미터 표준오차용 부트스트랩
- `_review/scripts/02_event_study_sensitivity.py`: 민감도 분석

## 점검 체크리스트 (`/verify-bootstrap`이 자동 점검)

- [ ] `n_bootstrap >= 1000` (CI 안정성)
- [ ] 블록 길이가 자동 선택 또는 정당화된 고정값
- [ ] iid bootstrap이 아닌 block bootstrap 사용
- [ ] 시드 고정 (재현성)
- [ ] CI 방법(percentile / BCa) 명시

## 알려진 함정

1. **iid bootstrap 오용**: 시계열 데이터에 iid bootstrap을 쓰면 자기상관 무시 → 표준오차 과소 → 거짓 유의성. Block 또는 Stationary Bootstrap 필수.
2. **고정 블록 크기 정당화 누락**: "block_size = 10" 같은 매직 넘버는 데이터 의존적이어야. Politis-White 자동 선택 권장. 고정이면 사유 명시.
3. **부트스트랩 횟수 부족**: n=100 등은 CI 폭이 매우 불안정. n ≥ 1000 권장, 정확도 필요시 5000~10000.
4. **CI 방법 미보고**: percentile vs BCa 선택은 결과 해석에 영향. BCa가 일반적으로 더 정확.
5. **재현 불가**: 시드 미고정 시 동일 분석이 매번 다른 결과. 코드 시작에 `np.random.seed(42)` 등 필수.

## 인용 (한국어)
> Politis & Romano (1994, JASA 89:1303-1313) Stationary Bootstrap; Politis & White (2004) 자동 블록선택

## BibTeX
```
@article{politis1994stationary,title={The stationary bootstrap},author={Politis, Dimitris N and Romano, Joseph P},journal={JASA},volume={89},number={428},pages={1303--1313},year={1994}}
@article{politis2004automatic,title={Automatic block-length selection for the dependent bootstrap},author={Politis, Dimitris N and White, Halbert},journal={Econometric Reviews},volume={23},number={1},pages={53--70},year={2004}}
```
