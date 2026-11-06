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


def test_rsi_1h_live_matches_source():
    """RSI 1h Live column must be the source's live_tradable_side (28), not same+live_only (27)."""
    import json
    import export_results
    par = json.load(open(export_results.AUDIT + "/scripts/T09/out/parity_result.json", encoding="utf-8"))
    src = par["per_key"]["rsi|rsi_events|1h"]["live_tradable_side"]
    assert src == 28
    ex = export_results.t09_result()["examples"][0]
    rows = {r[0]: r for r in ex["rows"]}
    assert rows["rsi_events 1h"][1] == 28
    for tf, want in (("5m", 461), ("15m", 147)):
        assert rows["rsi_events " + tf][1] == want
    assert rows["rsi_events 1h"][3:7] == [3, 0, 0, 24]
