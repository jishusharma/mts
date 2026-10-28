"""LC1 consumers: the 8-family KEEP set is void on the fair control; the consumers must say so (annotate only, no rerun)."""
from pathlib import Path

REPO = Path(__file__).resolve().parents[5]
LC = REPO / "MyTradingSys/research/levels_confluence_2026-10-14"
LEGACY = "LEGACY 8-family set, void since T05-F5"


def _t(p):
    return Path(p).read_text(encoding="utf-8")


def test_stability_lc1_row_labelled_legacy():
    src = _t(Path(__file__).with_name("stability.py"))
    assert '"levels_hold LC1 KEEP (' + LEGACY in src
    assert LEGACY in src.split("def lc1_legacy_rows(")[1].split('"""')[1]


def test_ladder_consumers_labelled_legacy():
    assert "# " + LEGACY + "\nKEEP = {" in _t(LC / "event_table.py")
    assert LEGACY in _t(LC / "ladder_run.py").split('"""')[1]
    md = _t(LC / "ladder_dev.md")
    assert "SUPERSEDED-PREMISE" in md.split("## Verdict")[1].split("\n", 3)[2]


# ---- fair-control rows (12 families), loader seam, DEV only
import datetime as dt
import importlib.util
import random

import pytest

_spec = importlib.util.spec_from_file_location("t10_stability", Path(__file__).with_name("stability.py"))
stab = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(stab)
LC_FAMILIES = {"4h_fractal_high", "4h_fractal_low", "daily_open", "naked_poc", "prior_day_high", "prior_day_low",
               "prior_day_poc", "prior_day_vah", "prior_day_val", "prior_week_high", "prior_week_low", "round_1000"}


def _walk(days, t0=1647820800000):    # 2022-03-21 00:00 UTC
    rng = random.Random(3)
    px, out = 30000.0, []
    for k in range(1440 * days):
        o = px
        px += rng.uniform(-30, 30)
        out.append({"t": t0 + k * 60000, "o": o, "h": max(o, px) + rng.uniform(0, 10), "l": min(o, px) - rng.uniform(0, 10),
                    "c": px, "v": rng.uniform(1, 5), "tbv": 1.0})
    return out


def _reference(bars):
    """Independent re-computation: net per touch = HOLD(1/0) - the family's fair random_hold_rate, in pp."""
    stab.sys.path.insert(0, str(REPO / "MyTradingSys/research/levels_confluence_2026-10-14"))
    from levels import levels_by_day
    from levels_hold import analyze
    d0 = int(dt.datetime(2022, 4, 1, tzinfo=dt.timezone.utc).timestamp() * 1000)
    res = analyze([b for b in bars if b["t"] >= d0], levels_by_day(bars))
    return res


def test_lc1_rows_cover_all_families():
    bars = _walk(45)
    rows = stab.lc1_rows(bars=bars)
    res = _reference(bars)
    assert set(res["families"]) == LC_FAMILIES          # 12 families on the synthetic bars
    fam_rows = stab.lc1_family_rows(bars=bars)
    assert {r[0] for r in fam_rows} == LC_FAMILIES     # no keep filter: all 12 present
    assert len(rows) == len(res["touches"]) == len(fam_rows)
    rate = {k: v["random_hold_rate"] for k, v in res["families"].items()}
    want = [(e["day"] * stab.DAY_MS, e["side"], 100.0 * ((e["outcome"] == "HOLD") - rate[e["family"]]))
            for e in res["touches"]]
    assert rows == want


def test_lc1_legacy_rows_are_the_8_old_keep_families_only():
    bars = _walk(45)
    legacy = stab.lc1_legacy_rows(bars=bars)
    assert 0 < len(legacy) < len(stab.lc1_rows(bars=bars))
    assert {r[0] for r in stab.lc1_family_rows(bars=bars) if r[0] in stab.LC1_LEGACY_KEEP} == set(stab.LC1_LEGACY_KEEP)


def test_lc1_rows_refuse_bars_past_dev_end():
    bars = _walk(2, t0=stab.DEV_END_MS - 60000)           # last bar is at/after DEV_END_MS: VALIDATION data
    with pytest.raises(AssertionError):
        stab.lc1_rows(bars=bars)


def test_main_labels_fair_control_row():
    src = _t(Path(__file__).with_name("stability.py"))
    assert "levels_hold LC1 fair control (KEEP none)" in src
