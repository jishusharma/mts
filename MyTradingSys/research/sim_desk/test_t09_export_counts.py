"""T09 exact-match count must be 3,156 (2,880+30+99+130+17), not 3,200+."""
from pathlib import Path

HERE = Path(__file__).resolve().parent
MD = HERE.parent / "dsa_backtest_audit_2026-10-16" / "T09_live_parity.md"
PY = HERE / "export_results.py"


def test_no_overstated_count():
    for p in (MD, PY):
        t = p.read_text(encoding="utf-8")
        assert "3,200+" not in t, p.name
        assert "0 differences in 3,156 signals" in t, p.name


def test_family_sum():
    assert 2880 + 30 + 99 + 130 + 17 == 3156
