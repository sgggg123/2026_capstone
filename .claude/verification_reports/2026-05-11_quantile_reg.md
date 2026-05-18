# 검증 보고서: 분위회귀 (Quantile Regression)

- **일자**: 2026-05-11
- **기준**: Koenker & Bassett (1978, Econometrica 46:33-50); Bouri 외 (2017, FRL 23:87-95); `.claude/references/quantile_reg.md`
- **카탈로그**: `.claude/references/catalog.json#quantile_reg`
- **검증 대상**:
  - `Edit_mj/분위수_회귀.ipynb` (메인 분석)
  - `test/분위수_회귀.ipynb` (대조군)

## 항목별 판정

| # | 항목 | 검출값 | 판정 | 비고 |
|---|---|---|---|---|
| 1 | τ 임계값 | Edit_mj: `[0.05, 0.10, 0.25, 0.50, 0.75, 0.90, 0.95]` (7분위) | ✅ PASS | Bouri 2017 양측 검증 형식. 극단 5%/10% + 중앙값 모두 포함 |
| 2 | statsmodels.QuantReg 사용 | Edit_mj 24회, test 16회 등장 | ✅ PASS | 표준 라이브러리 |
| 3 | 통일 이벤트 키 | 6키 모두 사용 (양 노트북) | ✅ PASS | 분석 범위 완전 커버 |
| 4 | 표준오차 방법 | `bootstrap`/`sandwich`/`Powell`/`kernel` 키워드 0건 | ⚠️ WARN | OLS sandwich 잘못 사용 우려. 명시 필요 |
| 5 | 분위 크로싱 점검 | `crossing`/`monotone` 키워드 0건 | ⚠️ WARN | β(τ=0.05) ≤ β(τ=0.10) 단조성 점검 안 됨 |
| 6 | Bouri 2017 인용 | 0건 | ⚠️ WARN | 본 프로젝트 핵심 선행연구. 마크다운 인용 추가 필요 |
| 7 | Koenker & Bassett 1978 인용 | 0건 | ⚠️ WARN | 분위회귀 표준 논문. 인용 누락 |
| 8 | seed 고정 | 미설정 | ❌ FAIL | 부트스트랩 표준오차 사용 시 재현 불가 |
| 9 | test 노트북 τ 명시 | 추출 패턴에 안 잡힘 | ⚠️ WARN | Edit_mj와 동일 분위 사용 여부 수동 점검 |

## 종합

| 결과 | 개수 |
|---|---|
| ✅ PASS | 3 |
| ⚠️ WARN | 5 |
| ❌ FAIL | 1 |

## 즉시 조치 필요 (FAIL 1건)

1. **seed 미고정**
   - 분위회귀 자체는 deterministic이지만 부트스트랩 표준오차를 쓸 경우 재현 불가
   - 조치: 노트북 첫 셀에 `np.random.seed(42)` 추가
   - 부트스트랩 표준오차를 안 쓴다면 — 그것 자체가 또 다른 WARN (항목 4)

## 검토 권유 (WARN 5건)

1. **표준오차 방법 명시**
   - 현재 statsmodels.QuantReg 기본 호출 → IID asymptotic SE 사용 중일 가능성
   - 분위회귀 표준 권장: bootstrap (`fit(method='bootstrap')`) 또는 Powell kernel
   - **조치**: `model.fit(method='bootstrap', n_replications=1000)` 또는 Powell 명시

2. **분위 크로싱 점검**
   - 추정된 β(τ)가 τ에 대해 단조성을 위반하지 않는지 시각적으로 점검
   - **조치**: 코드 셀 추가 — `for t in [0.05, 0.10, ...]: print(t, model.fit(q=t).params['SP500'])` 후 단조성 확인
   - 위반 시 Chernozhukov-Fernandez-Val (2010) 보정 권장

3. **Bouri (2017) 인용 누락**
   - 본 프로젝트가 직접 차용한 절차의 핵심 선행연구
   - **조치**: 마크다운 셀에 "본 분석은 Bouri 외 (2017, FRL 23:87-95)의 BTC 안전자산 분위회귀 절차를 따른다" 한 줄 추가
   - `.claude/citations/ready_to_paste.md` 참조

4. **Koenker & Bassett (1978) 인용 누락**
   - 분위회귀 표준 논문. 방법론 셀에 인용 추가
   - 동일하게 `.claude/citations/ready_to_paste.md` 참조

5. **test 노트북 τ 분포 일치성**
   - Edit_mj는 7분위 명시, test는 추출 안 됨
   - **조치**: test 노트북에서 같은 τ 리스트를 사용하는지 코드 직접 확인

## 강점 (보존할 것)

- **τ 7분위 사용** (0.05, 0.10, 0.25, 0.50, 0.75, 0.90, 0.95) — Bouri 2017보다 상세한 분포 검사. 양측(상승·하락) safe-haven 모두 검증 가능
- **statsmodels.QuantReg 사용** — 검증된 표준 라이브러리
- **이벤트 키 6개 모두 커버** — 분석 범위 완전성

## 인용

> Koenker & Bassett (1978, Econometrica 46:33-50) 분위회귀 표준; Bouri 외 (2017, FRL 23:87-95) Bitcoin 안전자산 분위회귀 적용

```bibtex
@article{koenker1978regression,title={Regression quantiles},author={Koenker, Roger and Bassett Jr, Gilbert},journal={Econometrica},volume={46},number={1},pages={33--50},year={1978}}
@article{bouri2017does,title={Does Bitcoin hedge global uncertainty?},author={Bouri, Elie and others},journal={Finance Research Letters},volume={23},pages={87--95},year={2017}}
```

상세 점검 항목: `.claude/references/quantile_reg.md`
