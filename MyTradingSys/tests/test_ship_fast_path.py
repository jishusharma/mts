"""Test alias pointing to FastShipTest in scripts/dev/test_sync.py."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts" / "dev"))
from test_sync import FastShipTest  # noqa: F401, E402
