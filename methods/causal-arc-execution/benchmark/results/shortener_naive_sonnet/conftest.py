"""Root conftest — ensures the project root is on sys.path for test imports."""
import sys
from pathlib import Path

# Make sure `main` and `database` are importable from the project root
sys.path.insert(0, str(Path(__file__).parent))
