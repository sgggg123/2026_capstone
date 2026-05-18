"""노트북을 실행해서 inplace로 저장. nbclient 사용.

사용:  python3 _runner/run_notebook.py <notebook_path> [timeout_sec]
실행 cwd는 노트북이 있는 폴더로 자동 설정 (상대경로 'master_data.csv' 등을 위해).
"""
import sys, os, time, traceback
from pathlib import Path

if len(sys.argv) < 2:
    print('usage: python3 run_notebook.py <notebook_path> [timeout_sec]')
    sys.exit(2)

nb_path = Path(sys.argv[1]).resolve()
timeout = int(sys.argv[2]) if len(sys.argv) > 2 else 1800

if not nb_path.exists():
    print(f'❌ notebook not found: {nb_path}')
    sys.exit(2)

work_dir = nb_path.parent
print(f'▶ executing: {nb_path}')
print(f'  cwd      : {work_dir}')
print(f'  timeout  : {timeout}s')

import nbformat
from nbclient import NotebookClient
from nbclient.exceptions import CellExecutionError

nb = nbformat.read(str(nb_path), as_version=4)
client = NotebookClient(
    nb,
    timeout=timeout,
    kernel_name='python3',
    resources={'metadata': {'path': str(work_dir)}},
    allow_errors=False,
)

t0 = time.time()
exit_code = 0
try:
    client.execute()
    print(f'✅ executed OK in {time.time()-t0:.1f}s')
except CellExecutionError as e:
    print(f'❌ CellExecutionError after {time.time()-t0:.1f}s')
    print(f'   in cell: {getattr(e, "cell_index", "?")}')
    print(f'   ename:   {getattr(e, "ename", "?")}')
    print(f'   evalue:  {getattr(e, "evalue", "?")}')
    exit_code = 1
except Exception as e:
    print(f'❌ unexpected error after {time.time()-t0:.1f}s: {type(e).__name__}: {e}')
    traceback.print_exc()
    exit_code = 2
finally:
    nbformat.write(nb, str(nb_path))
    print(f'✓ saved (with whatever outputs were collected): {nb_path}')

sys.exit(exit_code)
