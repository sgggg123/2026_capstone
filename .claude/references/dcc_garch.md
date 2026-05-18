# DCC-GARCH (Engle 2002 / Aielli 2013)

## 표준 논문
- Engle, R. F. (2002). Dynamic Conditional Correlation: A Simple Class of Multivariate GARCH Models. *Journal of Business & Economic Statistics*, 20(3), 339-350.
- Aielli, G. P. (2013). Dynamic Conditional Correlation: On Properties and Estimation. *JBES*, 31(3), 282-299. (cDCC 일관추정 보정)

## 표준 절차 (Engle 2002 §2-3)

**1단계: 개별 GARCH(1,1) 추정**

각 자산 i에 대해
```
r_it = μ_i + ε_it,    ε_it = √h_it · z_it
h_it = ω_i + α_i·ε²_{i,t-1} + β_i·h_{i,t-1}
```
정상성: α_i + β_i < 1.

**2단계: 표준화 잔차 추출**
`z_it = ε_it / √h_it`

**3단계: 동적 공분산**
```
Q_t = (1 - a - b)·Q̄ + a·z_{t-1}·z'_{t-1} + b·Q_{t-1}
R_t = diag(Q_t)^(-1/2) · Q_t · diag(Q_t)^(-1/2)
```
정상성: a + b < 1, a, b ≥ 0.

**4단계: QML 우도 최대화**
`L(θ) = -½ Σ [n·log(2π) + log|D_t| + log|R_t| + z'_t·R_t^(-1)·z_t]`

**Aielli (2013) cDCC 보정**: Engle 원식의 `Q̄` 추정 편향을 보정. `z_t` 대신 `z*_t = √(diag(Q_t)) · z_t` 사용.

## 사전 검증
- **ADF (Augmented Dickey-Fuller)**: 수익률이 정상인지 확인. 비정상이면 차분.
- **ARCH-LM 검정**: ARCH 효과 존재 확인 (없으면 GARCH 부적합).

## 사후 검증 (잔차 진단)
- **Ljung-Box (z_it)**: 자기상관 없음
- **Ljung-Box (z²_it)**: ARCH 효과 잔존 없음

## 본 프로젝트 구현 위치
- `Edit_mj/GARCH_분석.ipynb`
- `test/GARCH_분석.ipynb`
- `_review/scripts/01_garch_fixed.py`
- 결과: `_review/results/garch_arch_lib.csv`, `garch_compare.csv`, `garch_custom_compare.csv`, `garch_custom_fixed.csv`

## 점검 체크리스트 (`/verify-dcc-garch`가 자동 점검)

- [ ] GARCH(1,1) α + β < 1
- [ ] DCC a + b < 1
- [ ] ADF 사전 검증 보고
- [ ] 잔차 Ljung-Box 보고
- [ ] MLE 다중 초기값 (≥5개) 시도
- [ ] Aielli (2013) cDCC 보정 또는 미적용 사유 명시

## 알려진 함정

1. **단일 초기값**: MLE는 비볼록. 단일 초기값으로는 지역 최솟값에 갇힐 수 있음. L-BFGS-B + Nelder-Mead fallback 권장.
2. **arch 라이브러리 vs custom**: Python `arch` 패키지는 정확하지만 multivariate DCC는 직접 구현 필요. `_review/results/garch_arch_lib_compare.csv`에서 비교 결과 확인.
3. **고빈도 변동성에서 비정상**: BTC는 변동성 클러스터가 강해 GARCH(1,1) 부족할 수 있음. EGARCH/GJR-GARCH 비교 권장.
4. **위기 시 상관계수 해석**: 안전자산 조건은 "위기 시 상관계수가 음수"이지 "감소"가 아님 (Baur & Lucey 2010 정의).

## 인용 (한국어)
> Engle (2002, JBES 20:339-350) DCC-GARCH 표준; Aielli (2013, JBES 31:282-299) cDCC 일관추정 보정

## BibTeX
```
@article{engle2002dynamic,title={Dynamic conditional correlation},author={Engle, Robert},journal={Journal of Business \& Economic Statistics},volume={20},number={3},pages={339--350},year={2002}}
@article{aielli2013dynamic,title={Dynamic conditional correlation: On properties and estimation},author={Aielli, Gian Piero},journal={Journal of Business \& Economic Statistics},volume={31},number={3},pages={282--299},year={2013}}
```
