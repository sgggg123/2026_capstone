# Hybrid GPR (Caldara-Iacoviello + FinBERT + PCA)

## 표준 논문
- Caldara, D., & Iacoviello, M. (2022). Measuring Geopolitical Risk. *American Economic Review*, 112(4), 1194-1225.
- OECD (2008). *Handbook on Constructing Composite Indicators*. (PCA 합성지수 표준)
- Araci, D. (2019). FinBERT: Financial Sentiment Analysis with Pre-trained Language Models. arXiv:1908.10063.

## 표준 절차

**Caldara-Iacoviello GPR (원본)**
- 11개 영어권 신문에서 지정학 위험 관련 사전(adverse, attack, war, threat 등)을 검색
- 일별/월별 빈도수를 평균 빈도로 정규화
- 100을 기준값으로 스케일링

**FinBERT 보강 (이 프로젝트의 커스텀 부분)**
- GDELT 기사 톤 + FinBERT 금융 도메인 감성 → EII (Event Intensity Index)
- 이벤트별 ±30거래일에서 가중치 학습
- Caldara-Iacoviello GPR와 결합 (PCA 또는 가중평균)

**PCA 합성 (OECD 2008 §3)**
- 1단계: 표준화 (z-score)
- 2단계: 주성분 추출, 분산설명비 ≥ 70% 권장
- 3단계: PC1 가중치를 합성지수 가중치로 사용

## 본 프로젝트 구현 위치
- `GPR_custom_analysis.ipynb`: GPR_custom 산출 노트북
- `Edit_mj/master_data.csv`: `GPR_custom`, `F3_raw`, `GPR`, `GPR_zscore`, `mean_tone` 컬럼
- 가중치 학습: 이벤트 ±30거래일

## 점검 체크리스트 (`/verify-gpr-hybrid`가 자동 점검)

- [ ] EII 가중치 학습 데이터 ≠ 적용(검증) 데이터 (순환논리 배제)
- [ ] PCA 분산설명비 ≥ 70%
- [ ] FinBERT 도메인 적합 (금융 텍스트로 사전학습)
- [ ] Caldara-Iacoviello 원 GPR과 상관관계 보고 (수렴 타당성)
- [ ] 이벤트 경계 ±5일 보간 또는 급변 처리 명시

## 알려진 함정

1. **순환논리 (가장 위험)**: BTC 변동성을 목적함수로 EII 가중치를 학습하고, 그 EII로 BTC 안전자산성을 검증하면 동어반복. 학습 데이터(이벤트 외 또는 다른 자산 기반)와 적용 데이터를 분리해야.
2. **PCA 분산설명비 부족**: PC1이 분산의 50% 미만이면 합성지수가 데이터를 잘 대표하지 못함. 70% 임계는 OECD (2008) 권장.
3. **FinBERT 도메인 mismatch**: FinBERT는 금융 보고서 기반 사전학습. 일반 뉴스 톤에 적용 시 보정 필요. 또는 RoBERTa-news 등 대안 검토.
4. **이벤트 경계 효과**: ±30거래일 창 안팎에서 GPR 값이 급변하면 회귀 잔차에 인공 패턴. 선형 보간 또는 smooth weighting 필수.
5. **Caldara-Iacoviello 원본 미인용**: 본 프로젝트의 hybrid는 Caldara-Iacoviello GPR을 베이스로 가산하므로, 원본 인용은 필수.

## 인용 (한국어)
> Caldara & Iacoviello (2022, AER 112:1194-1225) GPR 지수; OECD (2008) 합성지수 PCA 표준; Araci (2019) FinBERT 금융 도메인 감성분석

## BibTeX
```
@article{caldara2022measuring,title={Measuring geopolitical risk},author={Caldara, Dario and Iacoviello, Matteo},journal={American Economic Review},volume={112},number={4},pages={1194--1225},year={2022}}
@article{araci2019finbert,title={FinBERT: Financial sentiment analysis with pre-trained language models},author={Araci, Dogu},journal={arXiv:1908.10063},year={2019}}
```
