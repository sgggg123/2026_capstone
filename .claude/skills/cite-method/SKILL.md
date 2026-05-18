---
name: cite-method
description: 메서드 이름을 받아 catalog.json에서 표준 인용(한국어 + BibTeX)을 즉시 출력한다. 결론 진술 시 빠른 인용 첨부용.
---

# cite-method

사용자가 통계 결론을 쓰는 도중 인용을 빠르게 가져올 때 호출.

## 사용법
```
/cite-method <method_name>
```

`method_name` 가능한 값:
- `event_study`
- `dcc_garch`
- `quantile_reg`
- `gpr_hybrid`
- `bootstrap`
- `multiple_testing`
- `safe_haven`

## 절차

1. `.claude/references/catalog.json` 읽기
2. `method_name` 키로 lookup
3. 해당 항목의 `citation_kr`과 `citation_bibtex` 추출
4. 다음 형식으로 출력:

```
인용 (한국어):
> {citation_kr}

BibTeX:
{citation_bibtex}

상세 점검 사항: .claude/references/{method_name}.md 참조
```

5. 키가 존재하지 않으면 가능한 키 목록 출력.

## 예
```
/cite-method event_study
```
→
```
인용 (한국어):
> MacKinlay (1997, JEL 35:13-39)에 따른 표준 이벤트 스터디 절차

BibTeX:
@article{mackinlay1997event,...}

상세 점검 사항: .claude/references/event_study.md 참조
```

## 도구
Read만 사용. Bash 불요.
