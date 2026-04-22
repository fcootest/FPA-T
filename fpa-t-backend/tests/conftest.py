import sys
from pathlib import Path

# Add backend root to sys.path so tests can import app modules
BACKEND_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BACKEND_ROOT))
