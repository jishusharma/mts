"""Test C34 spot cost re-scoring of long leads C30 and C28.

Tests fail on old code first (c34_spot_costs.py absent).
Recomputes perp numbers from BACKTEST_CANDIDATES.md:37 and :39 and matches them before spot rows are trusted.
Skips if BTC 5m/15m temp cache files are absent (GATE supervisor B 11-06).
"""
import os
import sys
import tempfile
from pathlib import Path
import pytest

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
CACHE_15M = Path(tempfile.gettempdir()) / "btc15m_bbdiv.json"
CACHE_5M = Path(tempfile.gettempdir()) / "btc5m_2022_2024h1.json"


def test_recomputes_existing_perp_numbers():
    if not CACHE_15M.exists() or not CACHE_5M.exists():
        pytest.skip("BTC 5m/15m temp cache absent")

    sys.path.insert(0, str(HERE))
    sys.path.insert(0, str(REPO))
    import c34_spot_costs as c34

    results = c34.run_rescore()

    # C30 30m buy dot <= -53 + bull div, any trend, exit X1:
    # SOURCED BACKTEST_CANDIDATES.md:39: "n=88 win 80% +0.35% both halves +"
    c30_row = results["C30_30m"]
    assert c30_row["n"] == 88
    assert round(c30_row["perp_fee_net_R"], 2) == 0.35
    assert abs(c30_row["perp_fee_net_R"] - 0.346) < 0.005

    # C28 2h uptrend buy dot <= 0 exit X3:
    # SOURCED BACKTEST_CANDIDATES.md:37: "n=69 +0.45% net, both halves +"
    c28_row = results["C28_2h"]
    assert c28_row["n"] == 69
    assert round(c28_row["perp_fee_net_R"], 2) == 0.45
    assert abs(c28_row["perp_fee_net_R"] - 0.454) < 0.005

    # Spot cost re-score (2 bps maker round trip = 0.02% vs 10 bps perp taker = 0.10%):
    # Gross R must equal perp_net + 0.10%
    assert abs(c30_row["gross_R"] - (c30_row["perp_fee_net_R"] + 0.10)) < 1e-4
    assert abs(c30_row["spot_fee_net_R"] - (c30_row["gross_R"] - 0.02)) < 1e-4

    assert abs(c28_row["gross_R"] - (c28_row["perp_fee_net_R"] + 0.10)) < 1e-4
    assert abs(c28_row["spot_fee_net_R"] - (c28_row["gross_R"] - 0.02)) < 1e-4


def test_spot_costs_markdown_file_generated():
    if not CACHE_15M.exists() or not CACHE_5M.exists():
        pytest.skip("BTC 5m/15m temp cache absent")

    sys.path.insert(0, str(HERE))
    sys.path.insert(0, str(REPO))
    import c34_spot_costs as c34

    md_path = HERE / "C34_SPOT_COSTS.md"
    assert md_path.exists(), "C34_SPOT_COSTS.md does not exist"
    text = md_path.read_text(encoding="utf-8")

    assert "Context:" in text
    assert "Regime mix:" in text
    assert "FORMULAS" in text and "13" in text
    assert "FAIL" in text and "-0.066" in text
    assert "INCONCLUSIVE" in text and "+0.220" in text
    assert ("Verdict: NO-LEAD" in text) or ("Verdict: LEAD" in text)
