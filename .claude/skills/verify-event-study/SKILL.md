---
name: verify-event-study
description: 이벤트 스터디(MacKinlay 1997 표준) 절차 준수 여부를 검증한다. 추정창 길이, 이벤트창, 모델 선택, 부트스트랩, Bonferroni 보정, Placebo를 자동 점검한다.
---

# verify-event-study

당신의 임무: 본 프로젝트의 이벤트 스터디 구현이 MacKinlay (1997) 표준 절차를 준수하는지 검증하고 PASS/WARN/FAIL 보고서를 한국어로 출력한다.

## 절차

1. `.claude/references/catalog.json` 읽고 `event_study` 섹션의 `red_flags`, `recommended_params`, `source_files`, `result_files`, `param_regex` 추출.
2. `.claude/references/event_study.md`의 점검 체크리스트 확인.
3. 각 source_file에 대해 Bash + grep으로 다음 추출:
   - 추정창 길이 (`EST_PRE`, `est_window`, `estimation_window` 등)
   - 이벤트창 (`EVT_WINDOW`, `event_window` 등)
   - 모델 종류 (CMRM, MarketModel)
   - Bootstrap 사용 여부 (`bootstrap`, `boot`, `Politis`)
   - Bonferroni / FDR 보정 여부
   - Placebo 검증 셀 존재 여부
4. 각 result_file에 대해 head/wc로 행 수, 컬럼 검증.
5. 다음 항목별로 PASS / WARN / FAIL 판정:

   | 항목 | PASS | WARN | FAIL |
   |---|---|---|---|
   | 추정창 길이 | ≥120 | 100~119 | <100 |
   | 이벤트창 정의 | [-5,+5] 또는 [-10,+10] | 그 외 정당화된 변형 | 정의 부재 |
   | BTC 모델 | CMRM | Market Model + 사유 | 미지정 |
   | Bootstrap | 사용 + n≥1000 | 사용하나 n<1000 | 미사용 |
   | 보정 | Bonferroni 또는 BH-FDR | 보정만 적용 사유 부족 | 미적용 |
   | Placebo | 별도 셀/스크립트 존재 | 언급만 | 부재 |
   | 통일 키 | 7개 모두 사용 | 일부 누락 | 옛 키 잔존 |

6. 결과를 `.claude/verification_reports/YYYY-MM-DD_event_study.md`에 저장 (오늘 날짜는 환경의 `currentDate` 사용).
7. 사용자에게 한국어로 요약 출력. 인용은 `.claude/references/catalog.json`의 `event_study.citation_kr`.

## 출력 형식

```
[검증: 이벤트 스터디] (MacKinlay 1997 기준)

✅ PASS (n개)
- 추정창 길이: 120일
- BTC 모델: CMRM
- ...

⚠️ WARN (n개)
- 이벤트창 비대칭 [-5,+10]: 사유 명시 필요

❌ FAIL (n개)
- Placebo 검증 셀 부재

총평: PASS 5 / WARN 1 / FAIL 1
참조: MacKinlay (1997, JEL 35:13-39)
보고서: .claude/verification_reports/2026-05-10_event_study.md
```

## 사용한 도구
- Read (catalog.json, event_study.md)
- Bash + grep (코드 파라미터 추출)
- Bash + head/wc (결과 csv 검증)
- Write (보고서 저장)

외부 호출 없음.
