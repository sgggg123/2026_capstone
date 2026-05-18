# Quantile Regression (Koenker & Bassett 1978)

## 표준 논문
- Koenker, R., & Bassett, G. (1978). Regression Quantiles. *Econometrica*, 46(1), 33-50.
- Bouri, E., Gupta, R., Tiwari, A. K., & Roubaud, D. (2017). Does Bitcoin hedge global uncertainty? *Finance Research Letters*, 23, 87-95.

## 표준 절차 (Koenker & Bassett 1978 §1-3)

**모델**
```
Q_τ(R_BTC | X) = α(τ) + β(τ)·R_SP500 + γ(τ)·GPR + ...
```

**최적화**
```
min_β  Σ ρ_τ(y_i - x_i'β),    ρ_τ(u) = u·(τ - 1{u<0})
```
선형계획으로 풀이. R `quantreg`, Python `statsmodels.QuantReg`.

**핵심 분위**
- τ = 0.05 또는 0.10: 극단 하락 (위기) 시 BTC 행동
- τ = 0.50: 중앙값 (비교 기준)

**안전자산 조건 (Baur & Lucey 2010 적용)**
- β(τ=0.05) < 0, p < 0.05  →  강한 safe haven
- β(τ=0.05) ≈ 0, 비유의   →  약한 safe haven
- β(τ=0.05) > 0, 유의      →  위험자산

## 본 프로젝트 구현 위치
- `Edit_mj/분위수_회귀.ipynb`
- `test/분위수_회귀.ipynb`

## 점검 체크리스트 (`/verify-quantile-reg`가 자동 점검)

- [ ] τ ∈ {0.05, 0.10} 사용 (Bouri 2017 표준)
- [ ] 분위 크로싱 점검 (β(τ=0.05) ≤ β(τ=0.10) 등)
- [ ] 표준오차: 부트스트랩 또는 Powell sandwich (OLS sandwich 금지)
- [ ] 표본 수: n·τ ≥ 30
- [ ] 다중공선성 점검 (X 변수 간 VIF)

## 알려진 함정

1. **τ가 너무 극단**: τ < 0.01이면 표본 부족. τ = 0.05가 안정적 하한.
2. **분위 크로싱 (Quantile Crossing)**: 추정된 분위 함수가 교차하면 비논리적. Chernozhukov-Fernandez-Val 보정 또는 monotone constraint 사용.
3. **표준오차 잘못 계산**: 분위회귀 표준오차는 OLS sandwich로 계산하면 안 됨. iid 가정 부트스트랩 또는 Powell kernel 사용.
4. **위기 정의 vs 분위**: 분위회귀의 τ는 *조건부* 분위. 시장 일별 수익률이 하위 5%일 때 BTC 행동을 보고 싶다면 비조건부 위기 더미와 결합 필요.
5. **Bouri (2017)와 임계값 차이**: Bouri는 τ ∈ {0.05, 0.95} 양쪽 모두 검토 (extreme up + extreme down). 본 프로젝트는 down side만이라면 그 사유 명시.

## 인용 (한국어)
> Koenker & Bassett (1978, Econometrica 46:33-50) 분위회귀 표준; Bouri 외 (2017, FRL 23:87-95) Bitcoin 안전자산 검증 적용

## BibTeX
```
@article{koenker1978regression,title={Regression quantiles},author={Koenker, Roger and Bassett Jr, Gilbert},journal={Econometrica},volume={46},number={1},pages={33--50},year={1978}}
@article{bouri2017does,title={Does Bitcoin hedge global uncertainty?},author={Bouri, Elie and others},journal={Finance Research Letters},volume={23},pages={87--95},year={2017}}
```
