"""catalog.json 기반 자동 검증 — 3종 본분석 (event_study / dcc_garch / quantile_reg).

사용:
    python3 _verifier/verifier.py                # 1사이클 검증, 보고서를 verification_reports/cycle_N.md로 저장
    python3 _verifier/verifier.py --cycle 1      # 사이클 번호 명시
    python3 _verifier/verifier.py --methodology event_study  # 특정 방법론만

검증 내용:
  1. source_files 존재 + 노트북 마지막 실행 성공 여부
  2. param_regex로 파라미터 추출 → recommended_params와 비교
  3. red_flags 패턴 매치 (코드에 필수 키워드 존재 여부)
  4. result_files 존재 + 비어있지 않음 (>1행)
  5. PASS / WARN / FAIL 자동 판정 + cycle_N.md 보고서
"""
import argparse
import json
import re
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CATALOG = ROOT / '.claude' / 'references' / 'catalog.json'
REPORTS_DIR = ROOT / '.claude' / 'verification_reports'

# 각 방법론별 red_flag 자동 패턴 매치 룰 (소스 코드에서 찾을 키워드)
RED_FLAG_PATTERNS = {
    'event_study': {
        'Bootstrap 미사용 (t-test 단독)': {
            'must_exist': [r'bootstrap', r'N_BOOT|n_boot'],
            'severity': 'FAIL',
        },
        'Placebo 검증 누락': {
            'must_exist': [r'placebo|pseudo[_\s]event'],
            'severity': 'WARN',
        },
        '다중비교 보정 누락 (Bonferroni 또는 BH-FDR)': {
            'must_exist': [r'bonferroni|benjamini|hochberg|fdr|BH[-_]'],
            'severity': 'WARN',
        },
        'est_window < 90 거래일': {
            'check': 'est_window_length_lt_90',
            'severity': 'WARN',
        },
    },
    'dcc_garch': {
        'α + β >= 1 (비정상)': {
            'check': 'alpha_beta_sum_ge_1',
            'severity': 'FAIL',
        },
        'ADF 사전검증 미수행': {
            'must_exist': [r'adfuller|adf_test|ADF'],
            'severity': 'WARN',
        },
        '잔차 진단(Ljung-Box) 미수행': {
            'must_exist': [r'ljung[_\s]?box|acorr_ljungbox'],
            'severity': 'WARN',
        },
        '단일 초기값 MLE (지역 최솟값 위험)': {
            'must_exist': [r'multi[_\s]?init|n_init|n_starts|grid_search|격자'],
            'severity': 'WARN',
        },
        'seed 미고정 (재현 불가)': {
            'must_exist': [r'np\.random\.seed|random_state\s*=\s*[0-9]|RANDOM_SEED'],
            'severity': 'WARN',
        },
    },
    'quantile_reg': {
        'τ < 0.01 또는 τ > 0.99 (극단 표본 부족)': {
            'check': 'tau_out_of_range',
            'severity': 'WARN',
        },
        '표준오차가 OLS sandwich (분위회귀에 부적합)': {
            'must_exist': [r'HAC|newey[_\s]?west|hac_se|bootstrap'],
            'severity': 'WARN',
        },
        '다중비교 보정 누락': {
            'must_exist': [r'bonferroni|benjamini|hochberg|fdr|BH[-_]'],
            'severity': 'WARN',
        },
    },
}


def read_notebook_source(nb_path: Path) -> str:
    """노트북의 모든 code 셀 source를 합쳐서 단일 문자열로."""
    if not nb_path.exists():
        return ''
    try:
        nb = json.load(open(nb_path, encoding='utf-8'))
        srcs = []
        for cell in nb.get('cells', []):
            if cell.get('cell_type') == 'code':
                srcs.append(''.join(cell.get('source', [])))
        return '\n\n'.join(srcs)
    except Exception as e:
        return f'<<read_error: {e}>>'


def notebook_executed_ok(nb_path: Path) -> tuple[bool, str]:
    """노트북의 cell outputs에 error가 있는지."""
    if not nb_path.exists():
        return False, f'no notebook: {nb_path}'
    try:
        nb = json.load(open(nb_path, encoding='utf-8'))
        for i, cell in enumerate(nb.get('cells', [])):
            if cell.get('cell_type') != 'code':
                continue
            for out in cell.get('outputs', []):
                if out.get('output_type') == 'error':
                    ename = out.get('ename', '?')
                    return False, f'cell {i} {ename}: {out.get("evalue","?")}'
        return True, 'all cells ok'
    except Exception as e:
        return False, f'read_error: {e}'


def extract_params(src: str, regex_dict: dict) -> dict:
    """param_regex를 코드에 적용해 모든 매치 추출."""
    out = {}
    for name, pat in regex_dict.items():
        try:
            matches = re.findall(pat, src, re.IGNORECASE)
            out[name] = matches if matches else None
        except re.error as e:
            out[name] = f'<regex_error: {e}>'
    return out


def check_red_flag(flag_name: str, rule: dict, src: str, params: dict) -> tuple[str, str]:
    """red_flag 자동 판정.
    Returns: (status, detail) where status in {PASS, WARN, FAIL}
    """
    severity = rule.get('severity', 'WARN')

    if 'must_exist' in rule:
        for pat in rule['must_exist']:
            if re.search(pat, src, re.IGNORECASE):
                return 'PASS', f'pattern matched: {pat}'
        return severity, f'missing patterns: {rule["must_exist"]}'

    check = rule.get('check')
    if check == 'est_window_length_lt_90':
        ests = params.get('est_window') or []
        ende = params.get('est_end') or []
        # EST_START, EST_END 모두 음수 → 추정창 길이 = |EST_START| - |EST_END| + 1
        try:
            est_start_val = max(int(m[1]) for m in ests) if ests else None  # 절대값으로 들어옴
            est_end_val   = max(int(m[1]) for m in ende) if ende else None
            if est_start_val and est_end_val:
                length = est_start_val - est_end_val + 1
                if length < 90:
                    return 'WARN', f'추정창 길이 {length}일 (< 90)'
                return 'PASS', f'추정창 길이 {length}일 (≥ 90)'
            return 'WARN', 'EST_START/EST_END 추출 실패'
        except Exception as e:
            return 'WARN', f'check error: {e}'

    if check == 'alpha_beta_sum_ge_1':
        # garch_model_comparison.csv에서 α+β 컬럼 직접 읽기
        comp = ROOT / 'Edit_mj' / 'results' / 'garch_model_comparison.csv'
        if not comp.exists():
            return 'WARN', 'garch_model_comparison.csv 없음'
        try:
            import pandas as pd
            df = pd.read_csv(comp)
            ab_col = next((c for c in df.columns if 'α+β' in c or 'alpha+beta' in c or 'a+b' in c), None)
            if ab_col is None:
                return 'WARN', f'α+β 컬럼 없음 (cols={list(df.columns)})'
            vals = pd.to_numeric(df[ab_col], errors='coerce').dropna()
            if (vals >= 1).any():
                return 'FAIL', f'비정상 모델 존재 (α+β max={vals.max():.4f})'
            return 'PASS', f'모든 모델 α+β < 1 (max={vals.max():.4f})'
        except Exception as e:
            return 'WARN', f'check error: {e}'

    if check == 'tau_out_of_range':
        tau_matches = params.get('tau') or []
        if not tau_matches:
            return 'WARN', 'TAUS 추출 실패'
        # 매치는 (name, '0.01, 0.025, ...') 튜플 또는 grouped
        tau_vals = []
        for m in tau_matches:
            text = m[1] if isinstance(m, tuple) else str(m)
            for tok in re.split(r'[,\s]+', text):
                try:
                    tau_vals.append(float(tok))
                except Exception:
                    pass
        out_range = [t for t in tau_vals if t < 0.01 or t > 0.99]
        if out_range:
            return 'WARN', f'τ 극단 표본 부족 위험: {out_range}'
        return 'PASS', f'모든 τ ∈ [0.01, 0.99]'

    return 'WARN', f'unknown check: {check}'


def check_result_files(result_files: list[str]) -> list[dict]:
    """result_files 존재 + 비어있지 않음."""
    out = []
    for rf in result_files:
        path = ROOT / rf
        if not path.exists():
            out.append({'path': rf, 'status': 'FAIL', 'detail': 'not found'})
            continue
        try:
            size = path.stat().st_size
            if size < 50:
                out.append({'path': rf, 'status': 'WARN', 'detail': f'too small ({size}B)'})
                continue
            # CSV이고 행이 1줄 이하면 빈 파일
            if rf.endswith('.csv'):
                with open(path, encoding='utf-8') as f:
                    n = sum(1 for _ in f)
                if n <= 1:
                    out.append({'path': rf, 'status': 'FAIL', 'detail': f'헤더만 ({n}줄)'})
                    continue
                out.append({'path': rf, 'status': 'PASS', 'detail': f'{n}줄 ({size}B)'})
            else:
                out.append({'path': rf, 'status': 'PASS', 'detail': f'{size}B'})
        except Exception as e:
            out.append({'path': rf, 'status': 'WARN', 'detail': f'read error: {e}'})
    return out


def verify_methodology(name: str, cat: dict) -> dict:
    """단일 방법론 검증."""
    spec = cat[name]
    report = {
        'methodology': name,
        'paper': spec.get('paper', ''),
        'source_check': [],
        'params_extracted': {},
        'red_flag_results': [],
        'result_check': [],
        'overall': 'PASS',
    }
    counters = {'PASS': 0, 'WARN': 0, 'FAIL': 0}

    # 1. source files
    combined_src = ''
    for sf in spec.get('source_files', []):
        path = ROOT / sf
        ok, msg = notebook_executed_ok(path) if str(path).endswith('.ipynb') else (path.exists(), 'file')
        status = 'PASS' if ok else 'FAIL'
        counters[status] += 1
        report['source_check'].append({'path': sf, 'status': status, 'detail': msg})
        if path.exists() and str(path).endswith('.ipynb'):
            combined_src += '\n\n' + read_notebook_source(path)
        elif path.exists():
            try:
                combined_src += '\n\n' + open(path, encoding='utf-8').read()
            except Exception:
                pass

    # 2. params
    params = extract_params(combined_src, spec.get('param_regex', {}))
    report['params_extracted'] = params

    # 3. red flags
    rules = RED_FLAG_PATTERNS.get(name, {})
    for flag, rule in rules.items():
        status, detail = check_red_flag(flag, rule, combined_src, params)
        counters[status] = counters.get(status, 0) + 1
        report['red_flag_results'].append({'flag': flag, 'status': status, 'detail': detail})

    # 4. result files
    rfs = check_result_files(spec.get('result_files', []))
    for r in rfs:
        counters[r['status']] = counters.get(r['status'], 0) + 1
    report['result_check'] = rfs

    # overall
    if counters.get('FAIL', 0) > 0:
        report['overall'] = 'FAIL'
    elif counters.get('WARN', 0) > 0:
        report['overall'] = 'WARN'
    else:
        report['overall'] = 'PASS'
    report['counters'] = counters
    return report


def write_markdown_report(reports: list[dict], cycle: int, out_path: Path) -> None:
    """verification_reports/cycle_N.md 작성."""
    lines = []
    lines.append(f'# Verification Report — cycle {cycle}')
    lines.append('')
    lines.append(f'- 일자: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}')
    lines.append(f'- catalog: `.claude/references/catalog.json` (v1.2)')
    lines.append(f'- 검증 방법론: {len(reports)}개')
    lines.append('')
    lines.append('## 요약')
    lines.append('')
    lines.append('| 방법론 | 종합 | PASS | WARN | FAIL |')
    lines.append('|---|---|---:|---:|---:|')
    for r in reports:
        c = r['counters']
        emoji = {'PASS': '✅', 'WARN': '⚠️', 'FAIL': '❌'}[r['overall']]
        lines.append(f'| {r["methodology"]} | {emoji} {r["overall"]} | {c.get("PASS",0)} | {c.get("WARN",0)} | {c.get("FAIL",0)} |')
    lines.append('')

    for r in reports:
        lines.append(f'## {r["methodology"]} — {r["overall"]}')
        lines.append('')
        lines.append(f'- **paper**: {r["paper"]}')
        lines.append('')
        lines.append('### 소스 파일')
        for s in r['source_check']:
            icon = {'PASS': '✅', 'WARN': '⚠️', 'FAIL': '❌'}.get(s['status'], '?')
            lines.append(f'- {icon} `{s["path"]}` — {s["detail"]}')
        lines.append('')

        lines.append('### 추출된 파라미터')
        for k, v in r['params_extracted'].items():
            short = str(v)
            if len(short) > 200:
                short = short[:200] + '...'
            lines.append(f'- `{k}`: {short}')
        lines.append('')

        lines.append('### Red Flag 자동 판정')
        for f in r['red_flag_results']:
            icon = {'PASS': '✅', 'WARN': '⚠️', 'FAIL': '❌'}.get(f['status'], '?')
            lines.append(f'- {icon} **{f["status"]}** — {f["flag"]}')
            lines.append(f'  - {f["detail"]}')
        lines.append('')

        lines.append('### 결과 파일')
        for rf in r['result_check']:
            icon = {'PASS': '✅', 'WARN': '⚠️', 'FAIL': '❌'}.get(rf['status'], '?')
            lines.append(f'- {icon} `{rf["path"]}` — {rf["detail"]}')
        lines.append('')

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text('\n'.join(lines), encoding='utf-8')
    print(f'✅ report written: {out_path}')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--cycle', type=int, default=None, help='cycle number')
    parser.add_argument('--methodology', default=None, help='single methodology')
    args = parser.parse_args()

    cat = json.load(open(CATALOG, encoding='utf-8'))
    targets = ['event_study', 'dcc_garch', 'quantile_reg']
    if args.methodology:
        targets = [args.methodology]

    # cycle 번호 자동 결정
    cycle = args.cycle
    if cycle is None:
        existing = sorted(REPORTS_DIR.glob('cycle_*.md'))
        cycle = len(existing) + 1

    reports = []
    for t in targets:
        if t not in cat:
            print(f'⚠️ {t} 카탈로그에 없음, 스킵')
            continue
        print(f'▶ verifying {t} ...')
        r = verify_methodology(t, cat)
        reports.append(r)
        print(f'  → {r["overall"]} (PASS={r["counters"].get("PASS",0)} '
              f'WARN={r["counters"].get("WARN",0)} FAIL={r["counters"].get("FAIL",0)})')

    out_path = REPORTS_DIR / f'cycle_{cycle}.md'
    write_markdown_report(reports, cycle, out_path)
    return 0


if __name__ == '__main__':
    sys.exit(main())
