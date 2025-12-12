import py_compile
import sys
import traceback

target = 'app/services/data_importer.py'
try:
    py_compile.compile(target, doraise=True)
    print('PY_COMPILE_OK')
except Exception:
    traceback.print_exc()
    sys.exit(1)
