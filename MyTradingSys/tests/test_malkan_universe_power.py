import importlib.util
from pathlib import Path
import pytest

SCRIPT_PATH = Path(__file__).resolve().parents[1] / "research" / "malkan_universe_2026-10" / "universe_power.py"


def load_universe_power():
    if not SCRIPT_PATH.exists():
        raise FileNotFoundError(f"Script does not exist: {SCRIPT_PATH}")
    spec = importlib.util.spec_from_file_location("universe_power", str(SCRIPT_PATH))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_reproduces_event_counts_1655_figure():
    """Unit test that the N/MDE calculation reproduces the 1,655-event figure of EVENT_COUNTS.md for +0.10 R."""
    mod = load_universe_power()
    
    # 1. Direct function call to compute trades needed for 80% power at +0.10 R
    # Using KR-S1 1d BTC anchor parameters from EVENT_COUNTS.md (median stop 4.1%, cost_r = 0.001 / 0.041)
    trades_needed = mod.events_for_target_net_r(target_net_r=0.10, rr=2.0, cost_r=0.001 / 0.041)
    assert round(trades_needed) == 1655

    # 2. Verify that the generated table / rows reproduce 1655 as the anchor events for +0.10R
    rows = mod.compute_malkan_power_table()
    # Find the KR-S1 anchor or verify all Malkan +0.10R rows are in the ~1650-1657 range
    krs1_anchor = next((r for r in rows if r["name"] == "KR-S1 1d (anchor)"), None)
    assert krs1_anchor is not None
    assert round(krs1_anchor["events_for_80pct_power"]) == 1655


def test_asset_years_and_underpowered_inconclusive():
    """Verify asset-years arithmetic and that N < 100 is flagged INCONCLUSIVE in advance."""
    mod = load_universe_power()
    
    # Check MAL-5 (3.638 events/calendar yr)
    # 1655 / 3.638 = ~455 asset-years (quoted in HOME_FIT_AUDIT_MALKAN.md:75)
    ay = mod.compute_asset_years_needed("MAL-5 1d", target_net_r=0.10)
    assert 1655.0 / ay["rate_per_cal_year"] == pytest.approx(455.0, abs=0.5)
    assert round(ay["asset_years_calendar"]) in (454, 455)

    # Check N < 100 verdict
    res_under_100 = mod.evaluate_universe_cell(n_events=50, rr=2.0, cost_r=0.016)
    assert res_under_100["verdict"] == "INCONCLUSIVE"
    assert res_under_100["inconclusive_in_advance"] is True

    # Check N >= 100 verdict
    res_over_100 = mod.evaluate_universe_cell(n_events=500, rr=2.0, cost_r=0.016)
    assert res_over_100["inconclusive_in_advance"] is False
