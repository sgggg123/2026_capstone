# 즉시 붙여쓰기용 인용 스니펫

분석 보고서/노트북 마크다운 셀/발표대본에 그대로 복사해 사용. 한국어 + BibTeX 페어.

---

## 이벤트 스터디

> 본 분석은 **MacKinlay (1997, JEL 35:13-39)** 의 표준 이벤트 스터디 절차를 따른다. 추정창 [-T₁, -11], 이벤트창 [-5, +5]를 사용하며 BTC는 Constant Mean Return Model, 그 외 자산은 Market Model (시장 = SP500)로 정상수익률을 추정한다.

```bibtex
@article{mackinlay1997event,title={Event studies in economics and finance},author={MacKinlay, A Craig},journal={Journal of economic literature},volume={35},number={1},pages={13--39},year={1997}}
```

---

## DCC-GARCH

> 동적 조건부 상관계수는 **Engle (2002, JBES 20:339-350)** 의 2단계 QML 방법으로 추정한다. 1단계에서 각 자산의 GARCH(1,1)을 적합하고, 2단계에서 표준화 잔차로 시변 공분산을 추정한다. 일관추정을 위해 **Aielli (2013, JBES 31:282-299)** 의 cDCC 보정을 적용한다.

```bibtex
@article{engle2002dynamic,title={Dynamic conditional correlation},author={Engle, Robert},journal={JBES},volume={20},number={3},pages={339--350},year={2002}}
```

---

## 분위 회귀

> 극단 시장 환경에서의 자산 간 관계는 **Koenker & Bassett (1978, Econometrica 46:33-50)** 의 분위회귀로 분석한다. 위기 분위 τ = {0.05, 0.10}와 중앙 분위 τ = 0.50을 비교하며, 표준오차는 부트스트랩으로 산출한다 (**Bouri 외 2017, FRL 23:87-95** 의 Bitcoin 적용 절차).

```bibtex
@article{koenker1978regression,title={Regression quantiles},author={Koenker, Roger and Bassett Jr, Gilbert},journal={Econometrica},volume={46},number={1},pages={33--50},year={1978}}
```

---

## 하이브리드 GPR

> 본 연구의 Hybrid GPR 지수는 **Caldara & Iacoviello (2022, AER 112:1194-1225)** 의 표준 지정학 위험 지수를 기반으로, GDELT 톤과 **FinBERT (Araci, 2019)** 감성을 결합해 구축한 EII와 PCA로 합성한다 (**OECD 2008** 합성지수 표준).

```bibtex
@article{caldara2022measuring,title={Measuring geopolitical risk},author={Caldara, Dario and Iacoviello, Matteo},journal={American Economic Review},volume={112},number={4},pages={1194--1225},year={2022}}
```

---

## 부트스트랩

> 시계열 자기상관을 보존하는 신뢰구간은 **Politis & Romano (1994, JASA 89:1303-1313)** 의 Stationary Bootstrap (5,000회 반복)으로 산출한다.

```bibtex
@article{politis1994stationary,title={The stationary bootstrap},author={Politis, Dimitris N and Romano, Joseph P},journal={JASA},volume={89},number={428},pages={1303--1313},year={1994}}
```

---

## 다중비교 보정

> 7 이벤트 × 7 자산 = 49 검정의 family-wise error 통제를 위해 **Bonferroni (1936)** 보정을 적용한다 (α* = 0.05 / 49 ≈ 0.00102). 검정력 비교를 위해 **Benjamini & Hochberg (1995, JRSSB 57:289-300)** FDR 보정 결과도 함께 보고한다.

```bibtex
@article{benjamini1995controlling,title={Controlling the false discovery rate},author={Benjamini, Yoav and Hochberg, Yosef},journal={JRSSB},volume={57},number={1},pages={289--300},year={1995}}
```

---

## 안전자산 프레임워크

> 안전자산 분류는 **Baur & Lucey (2010, Financial Review 45:217-229)** 의 정의를 따른다. Hedge는 평균적 무상관/음의 상관, Diversifier는 양의 부분 상관, Weak Safe Haven은 위기 시 무상관, Strong Safe Haven은 위기 시 음의 상관으로 정의된다. 본 연구는 이 프레임워크를 **Baur & McDermott (2010, JBF 34:1886-1898)** 의 다국가 검증 절차로 확장 적용한다.

```bibtex
@article{baur2010gold,title={Is gold a hedge or a safe haven?},author={Baur, Dirk G and Lucey, Brian M},journal={Financial Review},volume={45},number={2},pages={217--229},year={2010}}
```

---

## 사용 팁
- 결론 문장 직후에 위 인용 블록을 붙인다.
- BibTeX는 `references.bib` 파일에 모아두면 LaTeX 보고서에 바로 사용 가능.
- `/cite-method <name>`을 호출하면 위 한국어 + BibTeX 페어를 즉시 출력한다.
