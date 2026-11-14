"""BTC market regime (research_kit.regime_tag) as-of any time, and the regime-mix line for a window. A property of BTC closes only."""
import importlib.util
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
sys.path.insert(0, str(REPO))
from MyTradingSys.backtest import research_kit as rk  # noqa: E402

_sp = importlib.util.spec_from_file_location("rsi_gated_sibling", REPO / "MyTradingSys/research/rsi_divergence_mtf_gated_2026-11-04/study.py")
sib = importlib.util.module_from_spec(_sp)
_sp.loader.exec_module(sib)
CACHE = REPO / "runtime_data" / "rsi-confirm-10sym-1115"
DAY = 86400000


def _load(iv):
    return [{"t": r[0], "o": r[1], "h": r[2], "l": r[3], "c": r[4]} for r in json.loads((CACHE / ("BTC_%s.json" % iv)).read_text())]


def regime_fn():
    d = _load("1d")
    daily = ([x["t"] + DAY for x in d], [x["c"] for x in d])
    return sib.make_regime_at(daily, sib.rsi_series(_load("1w")), sib.rsi_series(_load("1M")))


def ms(s):
    return sib.ms(__import__("pandas").Timestamp(s))


def mix(regime_at, lo, hi):
    return rk.regime_mix_line([regime_at(t) for t in sib.week_starts(ms(lo), ms(hi))])


if __name__ == "__main__":
    r = regime_fn()
    lines = ["DEV 2020-03-01..2023-12-31: " + mix(r, "2020-03-01", "2024-01-01"),
             "VALIDATION 2024-01-01..2026-11-14: " + mix(r, "2024-01-01", "2026-11-15"),
             "VAL first half 2024-01-01..2025-06-30: " + mix(r, "2024-01-01", "2025-07-01"),
             "VAL second half 2025-07-01..2026-11-14: " + mix(r, "2025-07-01", "2026-11-15")]
    (HERE / "regime_mix.txt").write_text("\n".join(lines) + "\n")
    print("\n".join(lines))
