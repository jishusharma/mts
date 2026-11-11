"""One base-rate registry for the live aid (card prob-base-rates-registry-1106, d-prob-registry-1106).

python base_rates.py build   -> writes base_rates.js (var BASE_RATES = {...}) and
                                research/prob_dist_layer_brief_2026-10-16/BASE_RATES.md

Reads each study's output AS IT IS (no recomputation). The four studies write <name>_rates.js into base_rates_input/ when
re-run; if that file is absent (deleted after the first build) the row's table is carried over from the existing
base_rates.js, so a re-run of one study followed by `build` refreshes only that row. The candle_flip table is read
from its cells.csv. Row keys: id, event, condition, outcome, horizon, n, units, window, regime_mix, fee_status,
source, built_utc, table. Windows and horizons are quoted from each study's meta / RESULT.md; nothing here is a new threshold.
"""
import csv
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
RES = HERE.parents[1] / "research"
INPUT_DIR = HERE / "base_rates_input"   # studies write <name>_rates.js here, never next to the registry
OUT_JS = HERE / "base_rates.js"
OUT_MD = RES / "prob_dist_layer_brief_2026-10-16" / "BASE_RATES.md"
FLIP_DIR = RES / "candle_flip_probability_2026-11"
REQUIRED = ("id", "event", "condition", "outcome", "horizon", "n", "units", "window", "regime_mix", "fee_status", "source", "built_utc", "table")
NO_MIX = "not recorded by the study"
FLIP_COLS = {"group": str, "cell": str, "colour": str, "n_fit": int, "n": int, "weeks": int, "realised": float, "null": float,
             "delta": float, "p": float, "holm48": float, "survives_48": lambda v: v == "True"}


def read_js_var(path):
    s = Path(path).read_text(encoding="utf-8")
    return json.loads(s[s.index("= ") + 2:s.rindex(";")])


def regime_line(result_md):
    for ln in Path(result_md).read_text(encoding="utf-8").splitlines():
        if ln.startswith("Regime mix"):
            return ln.strip()
    return NO_MIX


def flip_table():
    rows = []
    with open(FLIP_DIR / "cells.csv", newline="", encoding="utf-8") as fh:
        for r in csv.DictReader(fh):
            rows.append({k: f(r[k]) for k, f in FLIP_COLS.items()})
    return rows


def load_table(js_name, var, prev):
    p = INPUT_DIR / js_name
    if p.exists():
        return read_js_var(p)
    if prev is None:
        raise SystemExit("no source for %s: %s missing and no earlier base_rates.js row" % (var, js_name))
    return prev["table"]


READINGS = ("home", "grid", "adx15", "adx1h", "vfi15", "wt30")   # the six readings of the review (analyze.py parts), fixed order
LOW_N = 30


def _sg(x):
    return (x > 0) - (x < 0) if x is not None else 0


def _agreeing(e):
    """Readings that point the flag's way. Same definitions as research/live_aid_review_2026-11-11/analyze.py parts()."""
    s = 1 if e["side"] == "LONG" else -1
    v = {"home": {"LONG": 1, "SHORT": -1}.get(e["home"], 0), "grid": {"UP": 1, "DOWN": -1}.get(e["grid"], 0),
         "adx15": _sg(e["adx15"]) if e["adx15"] is not None and abs(e["adx15"]) >= 20 else 0,
         "adx1h": _sg(e["adx1h"]) if e["adx1h"] is not None and abs(e["adx1h"]) >= 20 else 0,
         "vfi15": _sg(e["vfi15"]), "wt30": _sg(e["wt30"])}
    return [k for k in READINGS if s * v[k] > 0]


def setup_board_table(events):
    """Hit rate per evidence mix (side + set of agreeing readings) over replayed idea flags (events.json of replay.js).
    right = price 1h later beyond the flag's price in the flag's direction (r1h > 0). Mixes with n < 30 are LOW_N.
    Mix definition is OURS (descriptive, in-sample, no fees)."""
    ev = [e for e in events if e.get("kind") == "idea" and e.get("r1h") is not None]
    if not ev:
        raise SystemExit("no scored idea flags")
    day = lambda ms: datetime.fromtimestamp(ms / 1000, timezone.utc).strftime("%Y-%m-%d")
    lo, hi = day(min(e["ts"] for e in ev)), day(max(e["ts"] for e in ev))
    win = "%s..%s" % (lo, hi)
    g = {}
    for e in ev:
        k = (e["side"], "+".join(_agreeing(e)) or "none")
        n, h = g.get(k, (0, 0))
        g[k] = (n + 1, h + (1 if e["r1h"] > 0 else 0))
    rows = [{"side": k[0], "mix": k[1], "n": n, "hits": h, "rate": h / n, "window": win, "low_n": n < LOW_N} for k, (n, h) in sorted(g.items())]
    return {"meta": {"range": [lo, hi], "events": len(ev), "min_n": LOW_N, "readings": list(READINGS),
                     "outcome": "close 60 min after the flag beyond the flag price in its direction",
                     "source": "research/live_aid_review_2026-11-11/replay.js events.json (idea flags)"}, "rows": rows}


def write_setup_board_rates(events_json):
    t = setup_board_table(json.loads(Path(events_json).read_text(encoding="utf-8")))
    INPUT_DIR.mkdir(exist_ok=True)
    (INPUT_DIR / "setup_board_rates.js").write_text("var SETUP_BOARD_RATES = " + json.dumps(t, sort_keys=True, separators=(",", ":")) + ";" + chr(10),
                                                   encoding="utf-8", newline=chr(10))
    return t


def window_of(meta):
    return "%s..%s" % tuple(meta["range"])


def rows(prev=None):
    prev = prev or {}
    out = {}
    t = load_table("us_open_rates.js", "US_OPEN_RATES", prev.get("us_open_levels"))
    m = t["meta"]
    out["us_open_levels"] = dict(
        event="US open (09:30 New York) vs a marked level", condition="distance bucket from price at the open to day-so-far / prior-day / 3-day / 7-day high or low",
        outcome="level touched inside the 120 min window; close 60 min after the first touch still beyond the level", horizon="%d min window, %d min hold" % (m["window_min"], m["hold_min"]),
        n=m["days"], units="weekday US opens (one per day)", window=window_of(m), regime_mix=NO_MIX,
        fee_status="fee-free, descriptive", source="research/us_open_levels_2026-10-30/results.json (study.py)", table=t)
    t = load_table("anticipation_rates.js", "ANTICIPATION_RATES", prev.get("anticipation_oi_delta"))
    m = t["meta"]
    out["anticipation_oi_delta"] = dict(
        event="60 min price change x 60 min OI change x taker delta (price and OI both beyond the flat band)", condition="price / OI / taker-delta state, 8 cells",
        outcome="price continues; the move is undone (close back past the window start); OI keeps its sign", horizon="%d min" % m["window_min"],
        n=m["events"], units="hourly events (overlap between neighbouring hours not removed by the study)", window=window_of(m),
        regime_mix=regime_line(RES / "anticipation_map_2026-11-05" / "RESULT.md"), fee_status="fee-free, descriptive",
        source="research/anticipation_map_2026-11-05/study.py", table=t)
    t = load_table("level_approach_rates.js", "LEVEL_APPROACH_RATES", prev.get("level_approach_prior_day"))
    m = t["meta"]
    out["level_approach_prior_day"] = dict(
        event="approach to the prior-day high or low", condition="U1 absorption vs matched non-absorption; U2 OI tell; U3 wick-rejection TF count",
        outcome="reversal 0.5 % first or break close first (U1, U2); level holds (U3)", horizon="60 bars after the approach",
        n=m["approaches"], units="prior-day H/L approaches (touches %d)" % m["touches"], window=window_of(m),
        regime_mix=regime_line(RES / "level_approach_prep_2026-11-05" / "RESULT.md"), fee_status="fee-free, descriptive",
        source="research/level_approach_prep_2026-11-05/study.py", table=t)
    t = load_table("bigcandle_rates.js", "BIGCANDLE_RATES", prev.get("bigcandle_story"))
    m = t["meta"]
    out["bigcandle_story"] = dict(
        event="big 1h candle (|z| >= %s sd)" % m["zBig"], condition="story (price / OI / delta) x top-trader class x 30-day band x weekly streak; BASE cells = every bar",
        outcome="continues in the candle's direction; undone", horizon="1h, 4h, 24h", n=m["events_1h"],
        units="big 1h events (5m events %d with a 12-bar lockout)" % m["events_5m"], window=window_of(m),
        regime_mix=regime_line(RES / "bigcandle_story_2026-11-05" / "RESULT.md"), fee_status="fee-free, descriptive",
        source="research/bigcandle_story_2026-11-05/study.py", table=t)
    if (INPUT_DIR / "setup_board_rates.js").exists() or prev.get("setup_board_mix"):   # row exists once the replay has been run
        t = load_table("setup_board_rates.js", "SETUP_BOARD_RATES", prev.get("setup_board_mix"))
        m = t["meta"]
        out["setup_board_mix"] = dict(
            event="Live Aid idea flag replayed every 5 min, grouped by side and the set of readings that agree", condition="mix of home / grid / adx15 / adx1h / vfi15 / wt30 agreeing; LOW_N below %d" % m["min_n"],
            outcome=m["outcome"], horizon="60 min", n=m["events"], units="idea flags (a flag counts when it first appears; neighbours not independent)", window=window_of(m),
            regime_mix=NO_MIX, fee_status="fee-free, in-sample, descriptive", source="research/live_aid_review_2026-11-11/replay.js", table=t)
    cells = flip_table()
    mix = (FLIP_DIR / "regime_mix.txt").read_text(encoding="utf-8").strip().splitlines()
    out["candle_flip_cells"] = dict(
        event="open candle (open / pc colour) per timeframe group and context cell", condition="12 context cells x 4 timeframe groups x open/pc",
        outcome="candle keeps its colour at the close", horizon="the candle's own timeframe", n=max(c["n"] for c in cells),
        units="scored bars (n is per cell, largest shown; weeks %d)" % max(c["weeks"] for c in cells),
        window="fit 2024-01-01..2024-12-31, score 2025-01-01..now (score window already burned)", regime_mix=" ; ".join(x.strip() for x in mix),
        fee_status="not fee-tested (probability gauge; gain <= 0.9 % of Brier)", source="research/candle_flip_probability_2026-11/cells.csv", table=cells)
    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    for k, r in out.items():
        r["id"] = k
        p = prev.get(k)
        r["built_utc"] = p["built_utc"] if p and p["table"] == r["table"] else now
    return {k: {f: out[k][f] for f in REQUIRED} for k in out}


def validate(reg):
    for k, r in reg.items():
        miss = [f for f in REQUIRED if f not in r]
        assert not miss, (k, miss)
        assert r["id"] == k and isinstance(r["n"], int) and r["n"] > 0, (k, "n")
        for f in ("window", "units", "event", "outcome", "horizon", "fee_status", "source", "regime_mix"):
            assert isinstance(r[f], str) and r[f].strip(), (k, f)
        assert r["table"], (k, "table")


def load_existing():
    return read_js_var(OUT_JS) if OUT_JS.exists() else None


def md(reg):
    L = ["# Base rates registry", "", "Built by `MyTradingSys/tools/live_aid/base_rates.py build` from the existing study outputs (no recomputation). "
         "The live aid reads `base_rates.js`; each panel shows the window beside its numbers. Descriptive context for a trade already chosen, never a signal.", "",
         "| id | event | outcome | horizon | n | independent units | window | regime mix | fee status | source |", "|---|---|---|---|---:|---|---|---|---|---|"]
    for r in reg.values():
        L.append("| `%s` | %s | %s | %s | %s | %s | %s | %s | %s | `%s` |" % tuple(
            str(r[f]).replace("|", "/") for f in ("id", "event", "outcome", "horizon", "n", "units", "window", "regime_mix", "fee_status", "source")))
    return "\n".join(L) + "\n"


def build():
    reg = rows(load_existing())
    validate(reg)
    OUT_JS.write_text("// built by tools/live_aid/base_rates.py from the study outputs; do not edit\nvar BASE_RATES = " + json.dumps(reg, sort_keys=True, separators=(",", ":")) + ";\n",
                      encoding="utf-8", newline="\n")
    OUT_MD.write_text(md(reg), encoding="utf-8", newline="\n")
    print("rows:", ", ".join(reg))
    return reg


if __name__ == "__main__":
    if sys.argv[1:] == ["build"]:
        build()
    elif len(sys.argv) == 3 and sys.argv[1] == "setup-board":
        write_setup_board_rates(sys.argv[2])
    else:
        raise SystemExit("usage: base_rates.py build | setup-board <events.json>")
