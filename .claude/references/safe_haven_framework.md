# Safe-Haven Framework (Baur & Lucey 2010)

## 표준 논문
- Baur, D. G., & Lucey, B. M. (2010). Is Gold a Hedge or a Safe Haven? An Analysis of Stocks, Bonds and Gold. *Financial Review*, 45(2), 217-229.
- Baur, D. G., & McDermott, T. K. (2010). Is gold a safe haven? International evidence. *Journal of Banking & Finance*, 34(8), 1886-1898.

## 표준 정의 (Baur & Lucey 2010, p.219-221)

자산 A와 위험자산(예: 주식 시장) S의 관계로 분류:

| 분류 | 평균적 관계 | 위기 시 관계 |
|---|---|---|
| **Hedge** | 무상관 또는 음의 상관 | (위기 조건 없음) |
| **Diversifier** | 양의 (그러나 완전하지 않은) 상관 | (위기 조건 없음) |
| **Weak Safe Haven** | (조건 없음) | 무상관 (β = 0) |
| **Strong Safe Haven** | (조건 없음) | 음의 상관 (β < 0) |

**핵심**: Safe-haven은 *위기 조건부* 정의. 평균 상관과 별개.

**위기(crisis) 정의**
- 일반: 시장 수익률 분포 하위 q% 분위 (q = 1, 2.5, 5, 10)
- 본 프로젝트: q = 5%, 10% (분위회귀 τ)

**검증 모형 (Baur & Lucey 2010 §3)**
```
R_BTC,t = a + (b₀ + b₁·D_q5 + b₂·D_q1)·R_market,t + ε_t
```
- D_q5 = 1 if R_market,t ≤ q=5% 분위
- b₀ + b₁ + b₂ < 0 → strong safe haven (q=1 위기)
- b₀ + b₁ + b₂ ≈ 0, 비유의 → weak safe haven

## 본 프로젝트의 3조건 통합 적용

`_review/분석방식_전체.md`에 명시된 통합 판정:

| 조건 | 검정 방법 | 안전자산 임계 |
|---|---|---|
| ① CAR ≥ 0 (이벤트 직후 수익률 비감소) | Event Study CAR + Bonferroni | CAR ≥ 0 & 유의 |
| ② 위기 시 상관계수 감소 또는 음수 | DCC-GARCH 동적 상관 | 위기창 상관 < 0 (strong) 또는 ≈ 0 (weak) |
| ③ 극단 분위 β < 0 | Quantile Regression τ=0.05, 0.10 | β < 0, p < 0.05 |

3조건 모두 충족 → strong safe haven
①, ② 충족 (β ≈ 0) → weak safe haven
일부만 충족 → diversifier 또는 hedge
모두 불충족 → 위험자산

## 본 프로젝트 구현 위치
- `_review/분석방식_전체.md`: 판정 로직 문서
- `_review/results/btc_logic_ablation.csv`: 조건별 ablation
- `_review/results/btc_returns_compare.csv`: 자산 간 비교
- `_review/scripts/03_btc_logic_ablation.py`: 판정 스크립트

## 점검 체크리스트 (`/verify-safe-haven`이 자동 점검)

- [ ] "weak/strong safe haven" 용어가 정의에 부합
- [ ] 3조건이 모든 이벤트에 일관 적용
- [ ] 위기 정의(분위 q)가 사전 명시
- [ ] 단일 이벤트만으로 일반 결론 도출하지 않음
- [ ] 조건 미충족을 "효과 없음"이 아니라 "안전자산 증거 부족"으로 표현
- [ ] Baur & Lucey (2010) 인용 포함

## 알려진 함정

1. **용어 오용**: "BTC는 strong safe haven"이라고 쓰면서 β > 0이면 정의 위반. 검증 스킬이 자동 검출.
2. **위기 정의 사후 변경**: 결과를 보고 q를 5%→10%로 바꿔 유의성 만들기 = p-hacking.
3. **단일 이벤트 일반화**: 한 사례만으로 "BTC는 위기에 약/강하다" 단정 금지. 6개 이벤트(soleimani, hormuz, russia_ukraine_war, israel_hamas_war, israel_iran_war, us_israel_iran_war) 일관 패턴 필요.
4. **Hedge vs Safe-Haven 혼동**: Hedge는 평균적 무관성, Safe-Haven은 위기 조건부. 다른 개념.
5. **결론 비대칭**: ①②③ 모두 위배인데 일부만 보고하고 "약한 safe haven"이라고 약화 표현 = 학술 부정직.

## 인용 (한국어)
> Baur & Lucey (2010, Financial Review 45:217-229) safe-haven 표준 정의 (hedge/diversifier/weak/strong); Baur & McDermott (2010, JBF 34:1886-1898) 국제 검증

## BibTeX
```
@article{baur2010gold,title={Is gold a hedge or a safe haven?},author={Baur, Dirk G and Lucey, Brian M},journal={Financial Review},volume={45},number={2},pages={217--229},year={2010}}
@article{baur2010mcdermott,title={Is gold a safe haven? International evidence},author={Baur, Dirk G and McDermott, Thomas K},journal={JBF},volume={34},number={8},pages={1886--1898},year={2010}}
```
