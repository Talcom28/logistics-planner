import traceback
import importlib
import sys
from pathlib import Path

# Ensure project root is on sys.path when running from tools/
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

importlib.invalidate_caches()
try:
    import app.main
    print('IMPORT_OK')
except Exception:
    traceback.print_exc()
    raise
