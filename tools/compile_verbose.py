import py_compile
import sys
import traceback
from pathlib import Path

root = Path('app')
failed = False
for p in sorted(root.rglob('*.py')):
    try:
        py_compile.compile(str(p), doraise=True)
    except Exception:
        failed = True
        print('\n--- Compile failed:', p)
        traceback.print_exc()

if not failed:
    print('ALL_COMPILE_OK')
    sys.exit(0)
else:
    sys.exit(2)
