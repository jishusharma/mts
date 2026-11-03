"""Live confluence feed: RSI 40/60 events + Malkan divergence flags (+ Krown hidden flags) as ALERT-ONLY inputs.

Cards krown-hidden-divergence-confluence-feed and rsi-cross-unmapped-and-pivot-stack (operator order
d-move-lagging-layers-1104). Before this the live levels-confluence runner had no RSI / Malkan input and RSI cross
events were only rejected as unmapped by the auto-trader. Now they are flags any confluence reader can consume.

Safety (fail closed): every event is collection_only, carries NO "side" and no size; no layer_rules entry exists for
layer "confluence_feed", so auto_trader.layer_side() returns None and nothing reaches the order path. The raw
rsi:cross stays unmapped on purpose (no source gives a cross a side; see RSI_CROSS_UNMAPPED.md).

Parameter labels:
- RSI period 14: SOURCED (Malkan / Wilder default, same as rsi_core callers). Levels 40 and 60: SOURCED (Malkan 40-60).
  Tolerance 0.5: OURS (RSI_TOL of live_layers.rsi_level_layer).
- Malkan regular bullish/bearish: bars 3..10, min_rsi_diff 0: SOURCED (params/malkan_divergence_default.json).
- Malkan PRD / NRD: RSI regime 60 / 40 SOURCED; bars window 5..14 OURS + UNVERIFIED (glossary conflict C1).
- Krown hidden bullish/bearish (K-HBULL / K-HBEAR): third-party definition, window 3..10 OURS; source KROWN-CONFLUENCE.
  Never credited to Malkan: MALKAN_KINDS holds regular + reverse kinds only.
Codes match research/malkan_div_flags_2026-10-28/BTCUSDT_divergences.csv (R-BULL, R-BEAR, PRD, NRD, K-HBULL, K-HBEAR).

Causality: an event is stamped on the bar that confirms it (rsi_events: the resolving bar; divergences: b+1) and uses
only bars up to it. A consumer may use it only once that bar has CLOSED (annotate_levels_events enforces t + feed_tf).
The function is stateless: a restart gives identical output; events of bars[:k] are the prefix of events of bars.
"""
import csv
import datetime as dt
import json
import math
from pathlib import Path

from MyTradingSys.backtest.layers.rsi.krown_hidden_divergence import KROWN_KINDS, krown_hidden_divergence
from MyTradingSys.backtest.layers.rsi.rsi_core import rsi_core
from MyTradingSys.backtest.layers.rsi.rsi_divergence import rsi_divergence
from MyTradingSys.backtest.layers.rsi.rsi_events import rsi_events

RSI_PERIOD = 14
RSI_LEVELS = (40.0, 60.0)
RSI_TOL = 0.5
MIN_BARS_NEEDED = RSI_PERIOD + 2
MALKAN_KINDS = ("bullish", "bearish", "prd", "nrd")
MALKAN_CODE = {"bullish": "R-BULL", "bearish": "R-BEAR", "prd": "PRD", "nrd": "NRD"}
KROWN_CODE = {"hidden_bullish": "K-HBULL", "hidden_bearish": "K-HBEAR"}
TF_MS = {"1h": 3_600_000, "4h": 14_400_000, "1d": 86_400_000, "1w": 604_800_000}
_PARAMS = Path(__file__).resolve().parents[1] / "rsi" / "params" / "malkan_divergence_default.json"


def _params():
    p = json.loads(_PARAMS.read_text(encoding="utf-8"))
    rev = p["reverse"]
    kb = p["krown_hidden_bars"]
    return {"regular": (p["min_bars"], p["max_bars"], p.get("min_rsi_diff", 0.0)),
            "reverse": (rev["min_bars"], rev["max_bars"], p.get("min_rsi_diff", 0.0)),
            "krown": (kb["min_bars"], kb["max_bars"], 0.0)}


def _clean(bars):
    out = []
    for b in bars or ():
        try:
            if all(math.isfinite(float(b[k])) for k in ("t", "o", "h", "l", "c")):
                out.append(b)
        except (KeyError, TypeError, ValueError):
            continue
    return out


def confluence_feed_layer(bars):
    """fn(bars) -> [event] for the live registry (1h bars). Bad bars are dropped, too few bars / any error -> []."""
    try:
        bars = _clean(bars)
        if len(bars) < MIN_BARS_NEEDED:
            return []
        closes = [float(b["c"]) for b in bars]
        ts = [int(b["t"]) for b in bars]
        rsi = rsi_core(closes, RSI_PERIOD)
        par = _params()
        out = []
        for lv in RSI_LEVELS:
            for e in rsi_events(rsi, ts, level=lv, tolerance=RSI_TOL):
                name = e["event"] + (("_" + e["direction"]) if e["event"] == "cross" else "")
                out.append({"t": int(e["t"]), "event": "cf_rsi_%s_%d" % (name, int(lv)), "code": "RSI_%s_%d" % (
                    name.upper(), int(lv)), "source": "MALKAN", "label": "levels SOURCED, tolerance OURS",
                    "penetration": e.get("penetration")})
        for kind in MALKAN_KINDS:
            mn, mx, diff = par["reverse" if kind in ("prd", "nrd") else "regular"]
            for e in rsi_divergence(closes, rsi, ts, mn, mx, kind, diff):
                out.append({"t": int(e["t"]), "event": "cf_malkan_%s" % MALKAN_CODE[kind].lower().replace("-", "_"),
                            "code": MALKAN_CODE[kind], "source": "MALKAN",
                            "label": "OURS+UNVERIFIED window" if kind in ("prd", "nrd") else "SOURCED",
                            "bars": e["bars"], "chain": e["chain"], "rsi_a": e["rsi_a"], "rsi_b": e["rsi_b"]})
        mn, mx, diff = par["krown"]
        for kind in KROWN_KINDS:
            for e in krown_hidden_divergence(closes, rsi, ts, mn, mx, kind, diff):
                out.append({"t": int(e["t"]), "event": "cf_krown_%s" % KROWN_CODE[kind].lower().replace("-", "_"),
                            "code": KROWN_CODE[kind], "source": "KROWN-CONFLUENCE", "label": "OURS",
                            "bars": e["bars"], "chain": e["chain"], "rsi_a": e["rsi_a"], "rsi_b": e["rsi_b"]})
        for e in out:
            e["collection_only"] = True          # no "side" key on purpose
            e["feed"] = "rsi_malkan_confluence"
        out.sort(key=lambda x: (x["t"], x["event"]))
        return out
    except Exception:  # noqa: BLE001 - fail closed: a broken feed is silent, never a partial or sided event
        return []


adapter = confluence_feed_layer


def annotate_levels_events(level_events, feed_events, window_ms, feed_tf_ms=TF_MS["1h"]):
    """Copy of each levels-confluence event with "confluence": sorted flag codes whose feed bar had CLOSED
    (feed t + feed_tf_ms <= event t) within the last window_ms. Never adds or changes a side. None feed -> []."""
    if window_ms < 0 or feed_tf_ms <= 0:
        raise ValueError("window_ms must be >= 0 and feed_tf_ms > 0")
    feed = [f for f in (feed_events or ()) if isinstance(f.get("t"), (int, float)) and f.get("code")]
    out = []
    for ev in level_events or ():
        t = ev["t"]
        codes = sorted({f["code"] for f in feed if f["t"] + feed_tf_ms <= t <= f["t"] + feed_tf_ms + window_ms})
        out.append({**ev, "confluence": codes})
    return out


def load_flags_csv(path):
    """Rows of a malkan_div_flags CSV (n,code,tf,date_A,date_B,event_known_on,...) as
    {code, tf, t (UTC open of the confirming bar), usable_from (t + tf length, when that bar has closed)}.
    Missing / unreadable / unknown-tf rows are skipped; a bad file -> []."""
    rows = []
    try:
        with open(path, newline="", encoding="utf-8") as f:
            for r in csv.DictReader(f):
                tf_ms = TF_MS.get(r.get("tf"))
                try:
                    d = dt.datetime.strptime(r["event_known_on"], "%Y-%m-%d").replace(tzinfo=dt.timezone.utc)
                except (KeyError, TypeError, ValueError):
                    continue
                if tf_ms is None or not r.get("code"):
                    continue
                t = int(d.timestamp() * 1000)
                rows.append({"code": r["code"], "tf": r["tf"], "t": t, "usable_from": t + tf_ms})
    except (OSError, csv.Error, UnicodeDecodeError):
        return []
    return rows
