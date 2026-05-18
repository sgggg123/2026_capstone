---
name: verify-bootstrap
description: Stationary Bootstrap(Politis & Romano 1994) 사용 검증. 블록 길이, 반복 횟수, 시드 고정 점검.
---

# verify-bootstrap

본 프로젝트의 부트스트랩 절차가 Politis & Romano (1994) 표준을 준수하는지 검증한다. 시계열 자기상관을 보존하는 block/stationary bootstrap 사용이 핵심.

## 절차

1. catalog.json의 `bootstrap` 섹션 로드.
2. source_files (이벤트 스터디 노트북, GARCH 노트북, `_review/scripts/02_event_study_sensitivity.py`)에서 부트스트랩 코드 추출:
   - 반복 횟수: `grep -oE "(n_boot|N_BOOT|n_bootstrap|nboot)\s*=\s*([0-9]+)"`
   - 블록 길이: `grep -oE "(block|BLOCK|block_size|block_length)\s*=\s*([0-9]+)"`
   - 시드: `grep -E "seed|np\.random\.seed|RandomState"`
   - 부트스트랩 종류: `grep -E "iid|stationary|block|StationaryBootstrap|MovingBlock"`
   - CI 방법: `grep -E "percentile|BCa|bias.corrected"`

3. 항목별 판정:

   | 항목 | PASS | WARN | FAIL |
   |---|---|---|---|
   | 부트스트랩 종류 | StationaryBootstrap 또는 MovingBlock | 명시 부족 | iid bootstrap |
   | 반복 횟수 | ≥1000 (이상적 5000) | 500~999 | <500 |
   | 블록 길이 | 자동 선택 (Politis-White) | 고정 + 사유 | 고정 + 무사유 |
   | 시드 고정 | 명시 | 부분 | 미고정 |
   | CI 방법 | percentile 또는 BCa | 미명시 | 잘못된 분포 가정 |

4. 보고서 + 한국어 요약. 인용: `Politis & Romano (1994, JASA 89:1303-1313); Politis & White (2004) 자동 블록선택`.

## 도구
Read, Bash + grep, Write.
