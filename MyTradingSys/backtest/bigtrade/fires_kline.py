"""
MyTradingSys/backtest/bigtrade/fires_kline.py - worker B1 of the big-trade backtest
(session MTS-2026-10-08-1933Z-APP-ANA-bigtrade-bt, research/bigtrade_2026-10-09/PLAN.md sections 2B, 3b, 5, 6).

FIRE HISTORY of the kline-only live layers on the CURRENT live parameters, so the capture matrix (worker A) can
score recall of big legs. NEW CODE ONLY: it imports the live registry and the layer modules READ-ONLY and never
writes into the live tree (no HALT files, no orders, no keys).

How a fire is produced (the same way the live runner produces an alert):
  * live_runner_cli.main polls every 60 s, fetches the last `--limit` (default 100) klines per timeframe, drops the
    newest (possibly open) row, so every layer function sees a SLIDING WINDOW of the newest 99 CLOSED bars;
  * live_runner_core.run_registry calls the registry entry's `fn(window)`, keeps events that are new against the
    previous call and not older than (confirm_lag_bars + 1) bars behind the newest closed bar (bars-closed-only),
    and de-duplicates on (key, t, event).
  `replay_key` re-implements exactly that decision per closed bar, with the registry's own `fn`, `confirm_lag_bars`
  and `params_id`. `t_fire_ms` = close time of the bar on which the event was first reported = the earliest moment a
  live alert could exist. Entry is the NEXT bar open at the earliest (never the signal bar).

Data: Binance USD-M PERP 1m klines (Dumps/backtest/raw_1m_2022 + Dumps/backtest/raw), resampled here with a
numpy aggregator that also carries `tbv` (layers/timeframe/tf_resample.py drops it; tested equal on o/h/l/c/v).
VENUE CAVEAT (finding F-BT-05): the live runner polls SPOT api.binance.com/api/v3/klines, history is perp.

Parity gate: `parity` compares the replay of the newest days with MyTradingSys/runtime/alerts/*.jsonl.

CLI (run from the repo root):
  python -m MyTradingSys.backtest.bigtrade.fires_kline cache
  python -m MyTradingSys.backtest.bigtrade.fires_kline run [--workers 5] [--keys rsi|rsi_events|5m,...]
  python -m MyTradingSys.backtest.bigtrade.fires_kline parity [--days 5] [--since-date 2026-09-29]
"""
import sys
sys.dont_write_bytecode = True  # never write .pyc into the live tree while importing live modules

import argparse
import bisect
import csv
import datetime as dt
import glob
import hashlib
import inspect
import json
import math
import multiprocessing
import os
import re
import subprocess
import time
from pathlib import Path

import numpy as np

REPO = Path(__file__).resolve().parents[3]
DATA_ROOT = Path(os.environ.get("BIGTRADE_DATA", r"F:\MTS\data\bigtrade"))
# VENUE: "perp" = Binance USD-M archive on disk (default). The live runner polls SPOT api.binance.com (finding F-BT-05):
# to re-run everything on spot history set BIGTRADE_VENUE=spot and BIGTRADE_KLINE_DIRS=<dir1>;<dir2> (1m kline CSVs,
# microsecond timestamps are converted). Cache and output folders are separated per venue.
VENUE = os.environ.get("BIGTRADE_VENUE", "perp")
FIRES_DIR = DATA_ROOT / ("fires" if VENUE == "perp" else "fires_" + VENUE)
CACHE_DIR = DATA_ROOT / "cache" / VENUE
_DEFAULT_KLINE_DIRS = [REPO / "Dumps" / "backtest" / "raw_1m_2022" / "klines", REPO / "Dumps" / "backtest" / "raw" / "klines"]
KLINE_DIRS = ([Path(x) for x in os.environ["BIGTRADE_KLINE_DIRS"].split(";") if x]
              if os.environ.get("BIGTRADE_KLINE_DIRS") else _DEFAULT_KLINE_DIRS)
DATA_VENUE = {"perp": "binance_usdm_perp_1m_archive", "spot": "binance_spot_1m_archive"}.get(VENUE, VENUE)
LIVE_ALERTS_DIR = REPO / "MyTradingSys" / "runtime" / "alerts"

# live_runner_cli.main: --limit default 100, fetch_closed_bars drops the newest row => 99 closed bars per window.
LIVE_LIMIT = 100
WINDOW = LIVE_LIMIT - 1
WARM = 150  # state warm-up calls before a chunk (> WINDOW + any confirm lag); results are discarded
ATR_PERIOD = 14
TF_MS = {"1m": 60000, "5m": 300000, "15m": 900000, "1h": 3600000}

# Not replayable from klines alone: handed to worker B2 (order-flow / funding layers).
B2_KEYS = {
    "fabio|v3_grid|1m": "needs aggTrades order-flow columns (buy_vol, b99_*, thr_days, fp)",
    "positioning|funding_cvd_fade|1h": "needs funding history; live fetches it over the network (default_fetch_funding)",
    # W3 2026-10-16: layers wired for testnet sampling; they read history beyond the 99-bar window (HistoryStore) or their
    # own fetch (wlow), so a 99-bar replay would not reproduce them. Not part of the bigtrade kline replay.
    "wlow_bounce|bbrsi60|1h": "own 1h candle + OI fetch (169+ bars), not the 99-bar window",
    "rsi_divergence|rsi_divergence|1h": "wave-1 adapter, not in the kline replay (sampling layer, no parity run)",
    "bb_top_reversal|bb_top_reversal|15m": "wave-1 adapter, not in the kline replay (sampling layer, no parity run)",
    "session_levels|session_levels|1m": "needs 2 UTC days of 1m history (HistoryStore), not the 99-bar window",
    "candle_close|candle_close|1m": "needs 7 days of 1m history (HistoryStore), not the 99-bar window",
    "levels|confluence|1m": "needs 17 days of 1m history (HistoryStore), not the 99-bar window",
}

# Repo split (OPERATOR_DECISIONS.md:878): DEV 2022-01-01..2024-06-30, VALIDATION 2024-07-01..2025-06-30, HOLDOUT after.
# Label names kept (TRAIN = DEV, VALIDATE = VALIDATION) because the fire CSV "split" column and callers use them.
# DECISION (OURS) 2026-10-17: the old PLAN-section-4 split (TRAIN to 2025-01-01) leaked 2024-07..12 VALIDATION into TRAIN
# (see SPLIT_ALIGNMENT_2026-10-17.md). POST = after the stated range (data runs to 2026-10-07).
SPLITS = (("TRAIN", "2022-01-01", "2024-07-01"), ("VALIDATE", "2024-07-01", "2025-07-01"),
          ("HOLDOUT", "2025-07-01", "2026-10-01"))

CSV_COLUMNS = [
    "layer", "key", "tf", "event", "side", "tradable", "t_fire_ms", "t_event_ms", "t_confirm_open_ms", "split",
    "price", "entry_price", "stop", "target", "atr", "atr_kind", "atr_pct", "stop_dist_atr", "stop_dist_pct", "fee_R",
    "cost_R", "fee_R_1atr", "fee_dominated", "rsi", "rsi_ma", "extra", "params_id", "params_json", "code_commit",
    "data_venue",
]
EXTRA_KEYS = ("imbalance", "direction", "penetration", "level_value", "tolerance_used", "kind", "level_price",
              "level_kind", "delta_k", "volume_k", "cvd_prev", "cvd_cur", "price_prev", "price_cur", "r_first",
              "regime", "rule_id", "level", "sampling")


# ----------------------------------------------------------------------------------------------------------------
# keys and parameters
# ----------------------------------------------------------------------------------------------------------------
def to_plan_key(reg_key):
    """'rsi|rsi_events|5m' -> 'layer:rsi:rsi_events:5m' (PLAN section 5 / auto_trader source naming)."""
    layer, sub, tf = reg_key.split("|")
    return "layer:%s:%s:%s" % (layer, sub, tf)


def key_slug(reg_key):
    return "_".join(reg_key.split("|"))


def kline_registry():
    """The live registry (built by the live code itself, read-only), minus the keys that need more than klines."""
    from MyTradingSys.backtest.layers.alerts.live_runner_cli import build_default_registry
    reg = build_default_registry(fetch_funding=lambda symbol, limit: [])
    return {k: e for k, e in reg.items() if k not in B2_KEYS}


def _defaults(fn, *names):
    sig = inspect.signature(fn).parameters
    return {n: sig[n].default for n in names if n in sig and sig[n].default is not inspect.Parameter.empty}


def cost_params():
    from MyTradingSys.backtest.layers.positioning import trade_costs
    d = _defaults(trade_costs.net_return, "fee_rt", "slip_rt")
    return float(d["fee_rt"]), float(d["slip_rt"])


def layer_params(reg_key):
    """Actual parameter values behind one live key (module defaults read with inspect, plus the literal constants
    live_layers.py passes). Printed into every row as params_json; the parity gate is what proves they are right."""
    from MyTradingSys.backtest.layers.alerts import live_layers as ll
    from MyTradingSys.backtest.layers.cryptocred import cc_setups, cc_retest, cc_structure
    from MyTradingSys.backtest.layers.fabio import fabio_cvd_absorption, fabio_escalation, fabio_volume_fvg
    from MyTradingSys.backtest.layers.rsi import malkan_40_60, rsi_core
    from MyTradingSys.backtest.layers.session import session_momentum
    from MyTradingSys.backtest.layers.turn_of_candle import turn_of_candle
    layer, sub, tf = reg_key.split("|")
    p = {"window_bars": WINDOW, "live_limit": LIVE_LIMIT, "tf": tf}
    if sub == "turn_of_candle":
        p.update(_defaults(turn_of_candle.turn_of_candle_events, "lead_minutes"))
        p["side_rule"] = "sign of minute-0 taker imbalance (2*tbv-v)/v; 0/none -> no side"
    elif sub == "rsi_events":
        p.update({"rsi_period": _defaults(rsi_core.rsi_core, "period")["period"], "level": ll.RSI_LEVEL,
                  "tolerance": ll.RSI_TOL, "side_rule": "only 'failure' events carry a side"})
    elif sub in ("malkan_bull", "malkan_bear"):
        fn = malkan_40_60.malkan_setup_bull if sub == "malkan_bull" else malkan_40_60.malkan_setup_bear
        p.update({"rsi_period": 14}, **_defaults(fn, "level", "tolerance"))
        p.update(_defaults(malkan_40_60.malkan_regime, "lo", "hi", "lookback"))
    elif sub == "escalation":
        p.update(_defaults(fabio_escalation.escalation_events, "left", "right", "use_body", "level_tolerance",
                           "aggression_k", "record_lookback"))
    elif sub == "cvd_absorption":
        p.update(_defaults(fabio_cvd_absorption.cvd_absorption_events, "left", "right", "use_body",
                           "price_tolerance"))
        p["cvd_anchor"] = "window start (differences only)"
    elif sub == "volume_fvg":
        p.update({"left": 2, "right": 2, "use_body": True, "n_bins": _defaults(ll.volume_fvg_layer, "n_bins")["n_bins"],
                  "va_pct": _defaults(fabio_volume_fvg.value_area, "pct")["pct"], "touch_scan_bars": 200})
    elif sub == "session_momentum":
        p.update(_defaults(session_momentum.session_momentum_events, "session_start_min", "first_min", "entry_min",
                           "min_abs"))
        p["bar_min"] = 15
    elif sub in ("sr_flip", "fib_pullback", "failed_msb"):
        fn = {"sr_flip": cc_setups.setup1_sr_flip, "fib_pullback": cc_setups.setup2_fib_pullback,
              "failed_msb": cc_setups.setup3_failed_msb_reversal}[sub]
        p.update(_defaults(fn, "stop_buffer_pct", "target_r", "fib_lo", "fib_hi", "failure_lookback"))
        p.update({"msb_" + k: v for k, v in _defaults(cc_structure.classify_msb, "require_prior_sequence",
                                                      "filter_range_noise").items()})
        p.update({"swing_" + k: v for k, v in _defaults(cc_structure.find_swings, "left", "right",
                                                       "use_body").items()})
        if sub == "sr_flip":
            p.update({"retest_" + k: v for k, v in _defaults(cc_retest.find_retest, "tolerance_pct",
                                                              "invalidate_pct", "expiry_bars").items()})
        p["target_emitted_by_live_layer"] = False
    return p


def _git(*args):
    return subprocess.run(["git"] + list(args), cwd=str(REPO), capture_output=True, text=True).stdout.strip()


def code_commit():
    """HEAD short hash, '+dirty' if any layer module imported by the replay differs from HEAD (staged or not)."""
    head = _git("rev-parse", "--short", "HEAD")
    files = sorted({m.__file__ for n, m in list(sys.modules.items())
                    if n.startswith("MyTradingSys.backtest.layers") and getattr(m, "__file__", None)})
    dirty = bool(files) and bool(_git("status", "--porcelain", "--untracked-files=no", "--", *files))
    return head + ("+dirty" if dirty else "")


# ----------------------------------------------------------------------------------------------------------------
# data: 1m klines -> numpy, resample (with tbv), Wilder ATR
# ----------------------------------------------------------------------------------------------------------------
def _read_csv(path):
    with open(path, "r", encoding="utf-8") as fh:
        first = fh.readline()
    skip = 0 if first.split(",")[0].strip().isdigit() else 1
    a = np.loadtxt(path, delimiter=",", skiprows=skip, usecols=(0, 1, 2, 3, 4, 5, 9), dtype=np.float64, ndmin=2)
    return a


def load_1m(dirs=None):
    """All 1m kline CSVs -> dict of arrays sorted by open time, duplicates removed (first wins, like
    bt_data.load_klines) plus a coverage dict. Microsecond timestamps (Binance spot archives from 2025) are converted
    to ms; non-minute-aligned open times raise."""
    dirs = KLINE_DIRS if dirs is None else dirs
    files = []
    for d in dirs:
        files += sorted(glob.glob(str(Path(d) / "*.csv")))
    chunks = [_read_csv(f) for f in files]
    allr = np.concatenate([c for c in chunks if len(c)])
    n_raw = len(allr)
    t_all = allr[:, 0].astype(np.int64)
    us_rows = int((t_all > 10 ** 14).sum())  # Binance SPOT archives switched to microseconds on 2025-01-01
    t_all = np.where(t_all > 10 ** 14, t_all // 1000, t_all)
    allr[:, 0] = t_all
    if (t_all % 60000 != 0).any():
        raise ValueError("non-minute-aligned open time in the kline files")
    order = np.argsort(t_all, kind="stable")
    t_sorted = t_all[order]
    keep = np.ones(len(t_sorted), dtype=bool)
    keep[1:] = np.diff(t_sorted) != 0
    sel = order[keep]
    rows = allr[sel]
    dup_rows = n_raw - len(sel)
    # conflicting duplicates (same t, different values) are a data defect, count them
    conflicts = 0
    if dup_rows:
        dup_t = t_sorted[1:][np.diff(t_sorted) == 0]
        seen = {}
        for i in np.flatnonzero(np.isin(t_all, dup_t)):
            tt = int(t_all[i])
            tup = tuple(allr[i, 1:])
            if tt in seen and seen[tt] != tup:
                conflicts += 1
            seen.setdefault(tt, tup)
    t = rows[:, 0].astype(np.int64)
    d = np.diff(t)
    gap_idx = np.flatnonzero(d != 60000)
    out = {"t": t, "o": rows[:, 1], "h": rows[:, 2], "l": rows[:, 3], "c": rows[:, 4], "v": rows[:, 5],
           "tbv": rows[:, 6]}
    cov = {"files": len(files), "rows_raw": int(n_raw), "rows": int(len(t)), "duplicate_rows": int(dup_rows),
           "microsecond_rows_converted": us_rows, "venue": VENUE,
           "conflicting_duplicates": int(conflicts), "first_t": int(t[0]), "last_t": int(t[-1]),
           "gaps": int(len(gap_idx)), "missing_minutes": int((d[gap_idx] // 60000 - 1).sum()) if len(gap_idx) else 0,
           "zero_volume_bars": int((out["v"] == 0).sum()), "tbv_gt_v": int((out["tbv"] > out["v"] + 1e-9).sum()),
           "h_lt_l": int((out["h"] < out["l"]).sum())}
    return out, cov


def resample_arrays(a, tf_ms):
    """Aggregate 1m arrays to tf_ms buckets (epoch aligned, like Binance klines), CLOSED buckets only.
    o = first open, h = max, l = min, c = last close, v = sum, tbv = sum. Also returns `n` = 1m bars per bucket."""
    t = a["t"]
    if tf_ms == 60000:
        return {k: a[k].copy() for k in ("t", "o", "h", "l", "c", "v", "tbv")} | {"n": np.ones(len(t), dtype=np.int64)}
    b = t // tf_ms
    chg = np.flatnonzero(np.diff(b)) + 1
    starts = np.concatenate(([0], chg)).astype(np.int64)
    ends = np.concatenate((chg, [len(t)])).astype(np.int64)
    out = {"t": b[starts] * tf_ms, "o": a["o"][starts], "c": a["c"][ends - 1],
           "h": np.maximum.reduceat(a["h"], starts), "l": np.minimum.reduceat(a["l"], starts),
           "v": np.add.reduceat(a["v"], starts), "tbv": np.add.reduceat(a["tbv"], starts), "n": ends - starts}
    closed = (out["t"] + tf_ms) <= (t[-1] + 60000)
    return {k: v[closed] for k, v in out.items()}


def wilder_atr(h, l, c, period=ATR_PERIOD):
    """Wilder ATR: TR_0 = h-l, TR_i = max(h-l, |h-c_prev|, |l-c_prev|); ATR_(period-1) = mean(TR_0..TR_(period-1));
    ATR_i = (ATR_(i-1)*(period-1) + TR_i)/period. NaN before index period-1. Causal (value at i uses bars <= i)."""
    n = len(c)
    out = np.full(n, np.nan)
    if n < period:
        return out
    hh, ll, cc = h.tolist(), l.tolist(), c.tolist()
    tr = [hh[0] - ll[0]] + [max(hh[i] - ll[i], abs(hh[i] - cc[i - 1]), abs(ll[i] - cc[i - 1])) for i in range(1, n)]
    atr = sum(tr[:period]) / period
    res = [float("nan")] * n
    res[period - 1] = atr
    k = period - 1
    for i in range(period, n):
        atr = (atr * k + tr[i]) / period
        res[i] = atr
    return np.array(res)


def _source_signature():
    parts = []
    for d in KLINE_DIRS:
        for f in sorted(glob.glob(str(Path(d) / "*.csv"))):
            st = os.stat(f)
            parts.append("%s:%d:%d" % (os.path.basename(f), st.st_size, int(st.st_mtime)))
    return hashlib.sha1("|".join(parts).encode("ascii")).hexdigest()


def build_cache(force=False):
    """1m arrays + resampled 5m/15m/1h (+ ATR per tf) -> npz in CACHE_DIR. Returns the coverage dict."""
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    sig = _source_signature()
    meta_path = CACHE_DIR / "meta.json"
    if not force and meta_path.exists():
        meta = json.loads(meta_path.read_text(encoding="utf-8"))
        if meta.get("signature") == sig and all((CACHE_DIR / ("klines_%s.npz" % tf)).exists() for tf in TF_MS):
            return meta["coverage"]
    a, cov = load_1m()
    for tf, ms in TF_MS.items():
        r = resample_arrays(a, ms)
        r["atr"] = wilder_atr(r["h"], r["l"], r["c"])
        np.savez(CACHE_DIR / ("klines_%s.npz" % tf), **r)
        cov["bars_" + tf] = int(len(r["t"]))
    with open(meta_path, "w", encoding="utf-8", newline="\n") as fh:
        json.dump({"signature": sig, "coverage": cov}, fh, indent=1, sort_keys=True)
    return cov


_ARR = {}


def load_tf(tf):
    """Cached resampled arrays of one timeframe (per process)."""
    if tf not in _ARR:
        z = np.load(CACHE_DIR / ("klines_%s.npz" % tf))
        _ARR[tf] = {k: z[k] for k in z.files}
    return _ARR[tf]


def to_bars(a, i0, i1):
    """List of closed-kline dicts {t,o,h,l,c,v,tbv} for array rows [i0, i1)."""
    t, o, h, l, c, v, tbv = (a[k][i0:i1].tolist() for k in ("t", "o", "h", "l", "c", "v", "tbv"))
    return [{"t": t[i], "o": o[i], "h": h[i], "l": l[i], "c": c[i], "v": v[i], "tbv": tbv[i]} for i in range(len(t))]


# ----------------------------------------------------------------------------------------------------------------
# replay: live_runner_core.run_registry decision for ONE key, per closed bar
# ----------------------------------------------------------------------------------------------------------------
def replay_key(fn, lag, bars, i0=None, i1=None, window=WINDOW, warm=WARM, with_rsi=True):
    """Fires of one registry entry over `bars` (ascending closed bars, list of dicts).

    For every newest-closed-bar index idx in [i0, i1) the layer sees bars[idx-window+1 : idx+1] (what the live runner
    fetches: the 99 newest closed bars) and the decision is the one in live_runner_core.run_registry:
      fresh = new_alerts(prev_events, events); keep t >= latest - allowed*bar_ms with allowed = lag + 1 (max(lag, 1) on
      a fresh state); skip (t, event) already emitted; a raising fn counts as an error and leaves the state unchanged.
    Calls start `warm` bars before i0 so the state matches a single pass (those fires are discarded).
    Returns (fires, n_errors); fire = {"idx", "t_confirm", "event"(dict), "rsi", "rsi_ma"}."""
    from MyTradingSys.backtest.layers.alerts.alert_emitter import new_alerts
    from MyTradingSys.backtest.layers.rsi.rsi_core import rsi_core
    from MyTradingSys.backtest.layers.rsi.rsi_ma import rsi_ma as _rsi_ma
    n = len(bars)
    i0 = window - 1 if i0 is None else max(i0, window - 1)
    i1 = n if i1 is None else min(i1, n)
    start = max(window - 1, i0 - warm)
    prev = None
    emitted = set()
    fires = []
    n_err = 0
    for idx in range(start, i1):
        win = bars[idx - window + 1: idx + 1]
        latest = win[-1]["t"]
        try:
            events = fn(win)
            if not isinstance(events, list):
                raise TypeError("layer must return a list")
        except Exception:  # noqa: BLE001 - run_registry records the error and keeps the state
            n_err += 1
            continue
        fresh = new_alerts(prev if prev is not None else [], events)
        bar_ms = win[-1]["t"] - win[-2]["t"]
        allowed = max(lag, 1) if prev is None else lag + 1
        fresh = [e for e in fresh if e.get("t") is not None and e["t"] >= latest - allowed * bar_ms]
        if fresh and idx >= i0:
            rv = rma = None
            if with_rsi:
                try:
                    rs = rsi_core([b["c"] for b in win], period=14)
                    rv = rs[-1] if rs else None
                    ma = _rsi_ma(rs, "SMA", 14)
                    rma = ma[-1] if ma else None
                except (KeyError, ValueError, TypeError):
                    rv = rma = None
        for e in fresh:
            ek = (e.get("t"), e.get("event"))
            if ek in emitted:
                continue
            emitted.add(ek)
            if idx >= i0:
                fires.append({"idx": idx, "t_confirm": latest, "event": e, "rsi": rv, "rsi_ma": rma})
        prev = events
    return fires, n_err


# ----------------------------------------------------------------------------------------------------------------
# rows
# ----------------------------------------------------------------------------------------------------------------
def split_of(t_ms):
    d = dt.datetime.fromtimestamp(t_ms / 1000.0, dt.timezone.utc).strftime("%Y-%m-%d")
    for name, lo, hi in SPLITS:
        if lo <= d < hi:
            return name
    return "PRE" if d < SPLITS[0][1] else "POST"


def _num(x):
    return "" if x is None or (isinstance(x, float) and math.isnan(x)) else repr(float(x))


def cost_fields(price, entry_price, stop, atr, fee_rt, slip_rt):
    """stop distance and fee metrics for one fire. R = round-trip fee / stop distance (PLAN section 3).
    All blank when the layer emits no stop. fee_R_1atr = fee per R when R = 1 ATR of the layer TF."""
    out = {"stop_dist_atr": None, "stop_dist_pct": None, "fee_R": None, "cost_R": None, "fee_dominated": None,
           "fee_R_1atr": None}
    if atr is not None and not math.isnan(atr) and atr > 0:
        out["fee_R_1atr"] = fee_rt * price / atr
    if stop is not None:
        ref = entry_price if entry_price is not None else price
        dist = abs(ref - stop)
        if dist > 0 and ref > 0:
            pct = dist / ref
            out["stop_dist_pct"] = pct
            out["fee_R"] = fee_rt / pct
            out["cost_R"] = (fee_rt + slip_rt) / pct
            # "under the round-trip fee" is strict; a stop exactly at the fee (sr_flip: level -/+ 0.1 %) is a tie that
            # float rounding of |entry-stop|/entry must not turn into "under" (relative tolerance 1e-9)
            out["fee_dominated"] = 1 if pct < fee_rt * (1.0 - 1e-9) else 0
            if atr is not None and not math.isnan(atr) and atr > 0:
                out["stop_dist_atr"] = dist / atr
        else:
            out["fee_dominated"] = 1
    return out


def fire_row(reg_key, entry, fire, tf_ms, bar, atr, fee_rt, slip_rt, params_json, commit):
    layer, sub, tf = reg_key.split("|")
    ev = fire["event"]
    side = ev.get("side") or ""
    price = bar["c"]
    entry_price = ev.get("entry_price")
    stop = ev.get("stop")
    target = ev.get("target")
    cf = cost_fields(price, entry_price, stop, atr, fee_rt, slip_rt)
    extra = {k: ev[k] for k in EXTRA_KEYS if k in ev and isinstance(ev[k], (int, float, str, bool))}
    t_fire = fire["t_confirm"] + tf_ms
    atr_v = None if atr is None or math.isnan(atr) else atr
    return {
        "layer": layer, "key": to_plan_key(reg_key), "tf": tf, "event": ev.get("event") or ev.get("kind") or "",
        "side": side, "tradable": 1 if side else 0, "t_fire_ms": t_fire, "t_event_ms": ev.get("t", ""),
        "t_confirm_open_ms": fire["t_confirm"], "split": split_of(t_fire), "price": _num(price),
        "entry_price": _num(entry_price), "stop": _num(stop), "target": _num(target), "atr": _num(atr_v),
        "atr_kind": "wilder", "atr_pct": _num(atr_v / price) if atr_v and price else "", "stop_dist_atr": _num(cf["stop_dist_atr"]),
        "stop_dist_pct": _num(cf["stop_dist_pct"]), "fee_R": _num(cf["fee_R"]), "cost_R": _num(cf["cost_R"]),
        "fee_R_1atr": _num(cf["fee_R_1atr"]),
        "fee_dominated": "" if cf["fee_dominated"] is None else cf["fee_dominated"],
        "rsi": _num(fire["rsi"]), "rsi_ma": _num(fire["rsi_ma"]),
        "extra": json.dumps(extra, sort_keys=True, separators=(",", ":")), "params_id": entry["params_id"],
        "params_json": params_json, "code_commit": commit, "data_venue": DATA_VENUE,
    }


def run_range(reg_key, i0, i1, entry=None, arrays=None, params_json=None, commit=None):
    """Fires of one key for TF-array rows [i0, i1) (global indices). Returns (rows, n_errors)."""
    if entry is None:
        entry = kline_registry()[reg_key]
    tf = entry["tf"]
    a = arrays if arrays is not None else load_tf(tf)
    a0 = max(0, i0 - WARM - WINDOW)
    a1 = min(len(a["t"]), i1)
    bars = to_bars(a, a0, a1)
    fires, n_err = replay_key(entry["fn"], int(entry.get("confirm_lag_bars", 0)), bars, i0=i0 - a0, i1=i1 - a0)
    fee_rt, slip_rt = cost_params()
    pj = params_json if params_json is not None else json.dumps(layer_params(reg_key), sort_keys=True,
                                                                separators=(",", ":"), default=str)
    cm = commit if commit is not None else code_commit()
    rows = []
    for f in fires:
        g = a0 + f["idx"]
        atr = float(a["atr"][g]) if "atr" in a else None
        rows.append(fire_row(reg_key, entry, f, TF_MS[tf], bars[f["idx"]], atr, fee_rt, slip_rt, pj, cm))
    return rows, n_err


# ----------------------------------------------------------------------------------------------------------------
# parallel run over the whole history
# ----------------------------------------------------------------------------------------------------------------
def _low_priority():
    try:
        import ctypes
        ctypes.windll.kernel32.SetPriorityClass(ctypes.windll.kernel32.GetCurrentProcess(), 0x00004000)  # BELOW_NORMAL
    except Exception:  # noqa: BLE001
        pass


def _task(args):
    reg_key, i0, i1, commit = args
    t0 = time.time()
    rows, n_err = run_range(reg_key, i0, i1, commit=commit)
    return reg_key, i0, i1, rows, n_err, time.time() - t0


CHUNK_BARS = {"1m": 150000, "5m": 100000, "15m": 40000, "1h": 50000}


COST_WEIGHT = {"sr_flip": 3.0, "fib_pullback": 3.0, "failed_msb": 3.0, "escalation": 2.0, "volume_fvg": 2.0,
               "cvd_absorption": 1.5}


def plan_tasks(reg, n_by_tf, keys=None, first_idx=None, commit=None):
    """[(reg_key, i0, i1, commit)] chunks, most expensive first (keeps the pool busy to the end)."""
    tasks = []
    for k, e in reg.items():
        if keys and k not in keys:
            continue
        tf = e["tf"]
        n = n_by_tf[tf]
        lo = (first_idx or {}).get(tf, 0)
        step = CHUNK_BARS[tf]
        s = lo
        while s < n:
            tasks.append((k, s, min(n, s + step), commit))
            s += step
    tasks.sort(key=lambda t: -(t[2] - t[1]) * COST_WEIGHT.get(t[0].split("|")[1], 1.0))
    return tasks


def write_csv(path, rows):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=CSV_COLUMNS, lineterminator="\n")
        w.writeheader()
        for r in rows:
            w.writerow(r)


def _chunk_file(resume_dir, reg_key, i0, i1):
    return Path(resume_dir) / ("%s_%d_%d.json" % (key_slug(reg_key), i0, i1))


def run_all(workers=5, keys=None, out_dir=None, resume_dir=None):
    """resume_dir: finished chunks are stored there as JSON and skipped on the next call (a killed run can continue;
    use a fresh folder after any code change)."""
    out_dir = Path(out_dir) if out_dir else FIRES_DIR
    cov = build_cache()
    reg = kline_registry()
    n_by_tf = {tf: cov["bars_" + tf] for tf in TF_MS}
    commit = code_commit()
    tasks = plan_tasks(reg, n_by_tf, keys=set(keys) if keys else None, commit=commit)
    by_key = {}
    errs = {}
    if resume_dir:
        Path(resume_dir).mkdir(parents=True, exist_ok=True)
        todo = []
        for t in tasks:
            f = _chunk_file(resume_dir, t[0], t[1], t[2])
            if f.exists():
                d = json.loads(f.read_text(encoding="utf-8"))
                by_key.setdefault(t[0], []).extend(d["rows"])
                errs[t[0]] = errs.get(t[0], 0) + d["n_err"]
            else:
                todo.append(t)
        print("resume: %d of %d chunks already done" % (len(tasks) - len(todo), len(tasks)), flush=True)
        tasks = todo
    print("tasks", len(tasks), "workers", workers, flush=True)
    t0 = time.time()
    with multiprocessing.Pool(workers, initializer=_low_priority) as pool:
        for reg_key, i0, i1, rows, n_err, secs in pool.imap_unordered(_task, tasks):
            by_key.setdefault(reg_key, []).extend(rows)
            errs[reg_key] = errs.get(reg_key, 0) + n_err
            if resume_dir:
                with open(_chunk_file(resume_dir, reg_key, i0, i1), "w", encoding="utf-8", newline="\n") as fh:
                    json.dump({"rows": rows, "n_err": n_err}, fh)
            print("  %-34s [%8d,%8d) fires=%6d errors=%d %.0fs (elapsed %.0fs)" % (
                reg_key, i0, i1, len(rows), n_err, secs, time.time() - t0), flush=True)
    summary = {"coverage": cov, "keys": {}, "code_commit": commit, "window_bars": WINDOW,
               "fee_rt": cost_params()[0], "slip_rt": cost_params()[1], "b2_keys": B2_KEYS}
    for reg_key, rows in by_key.items():
        rows.sort(key=lambda r: (r["t_fire_ms"], r["t_event_ms"], r["event"]))
        # a boundary between chunks must never duplicate a fire
        seen = set()
        uniq = []
        for r in rows:
            k = (r["t_event_ms"], r["event"])
            if k in seen:
                continue
            seen.add(k)
            uniq.append(r)
        rows = uniq
        write_csv(out_dir / ("fires_%s.csv" % key_slug(reg_key)), rows)
        per_year = {}
        for r in rows:
            y = dt.datetime.fromtimestamp(r["t_fire_ms"] / 1000.0, dt.timezone.utc).year
            per_year[y] = per_year.get(y, 0) + 1
        per_event = {}
        for r in rows:
            fam = event_family(r["event"])
            per_event[fam] = per_event.get(fam, 0) + 1
        summary["keys"][reg_key] = {
            "plan_key": to_plan_key(reg_key), "fires": len(rows), "tradable": sum(r["tradable"] for r in rows),
            "per_year": {str(k): v for k, v in sorted(per_year.items())}, "per_event": per_event,
            "errors": errs.get(reg_key, 0), "params": layer_params(reg_key),
            "params_id": reg[reg_key]["params_id"], "confirm_lag_bars": int(reg[reg_key].get("confirm_lag_bars", 0)),
            "csv": str(out_dir / ("fires_%s.csv" % key_slug(reg_key))),
        }
    with open(out_dir / "_summary_B1.json", "w", encoding="utf-8", newline="\n") as fh:
        json.dump(summary, fh, indent=1, sort_keys=True, default=str)
    print("done in %.0fs" % (time.time() - t0), flush=True)
    return summary


# ----------------------------------------------------------------------------------------------------------------
# parity gate vs the live alert log
# ----------------------------------------------------------------------------------------------------------------
_NUM_TAIL = re.compile(r"_-?\d+(\.\d+)?$")


def event_family(ev):
    """Event name without a trailing price (escalation_breakout_long_84103.06 -> escalation_breakout_long)."""
    return _NUM_TAIL.sub("", ev or "")


def alert_event_name(a):
    return a.get("event") if a.get("event") is not None else a.get("kind")


def load_live_alerts(alerts_dir=None):
    """Rows of MyTradingSys/runtime/alerts/<tf>.jsonl as dicts with reg key; exact duplicate (key,t,event) dropped."""
    alerts_dir = Path(alerts_dir) if alerts_dir else LIVE_ALERTS_DIR
    rows, seen, dups = [], set(), 0
    for f in sorted(glob.glob(str(alerts_dir / "*.jsonl"))):
        with open(f, "r", encoding="utf-8") as fh:
            for line in fh:
                line = line.strip()
                if not line:
                    continue
                a = json.loads(line)
                key = "%s|%s|%s" % (a["layer"], a["sub"], a["tf"])
                name = alert_event_name(a)
                k = (key, a["t_close"], a.get("event"))
                if k in seen:
                    dups += 1
                    continue
                seen.add(k)
                rows.append({"key": key, "t_event": a["t_close"], "event": name, "side": a.get("side") or "",
                             "t_confirm": a.get("t_confirm"), "raw": a})
    return rows, dups


def compare(replay_rows, live_rows, t0, t1):
    """Per registry key: strict (key, t_event, event), soft (event name without price) and side agreement.
    Only rows whose event time is in [t0, t1] are used on both sides. replay_rows are fire_row dicts."""
    res = {}
    keys = {r["key"] for r in live_rows} | {r["_reg_key"] for r in replay_rows}
    for k in sorted(keys):
        rep = [r for r in replay_rows if r["_reg_key"] == k and t0 <= int(r["t_event_ms"]) <= t1]
        liv = [r for r in live_rows if r["key"] == k and t0 <= r["t_event"] <= t1]
        rep_s = {(int(r["t_event_ms"]), r["event"]): r for r in rep}
        liv_s = {(r["t_event"], r["event"]): r for r in liv}
        matched = sorted(set(rep_s) & set(liv_s))
        only_live = sorted(set(liv_s) - set(rep_s))
        only_rep = sorted(set(rep_s) - set(liv_s))
        # soft pass: pair leftovers on (t_event, family)
        rep_f = {}
        for kk in only_rep:
            rep_f.setdefault((kk[0], event_family(kk[1])), []).append(kk)
        soft = []
        still_live = []
        for kk in only_live:
            fam = (kk[0], event_family(kk[1]))
            if rep_f.get(fam):
                soft.append((kk, rep_f[fam].pop(0)))
            else:
                still_live.append(kk)
        soft_rep = {b for _, b in soft}
        still_rep = [kk for kk in only_rep if kk not in soft_rep]
        side_mismatch = [kk for kk in matched if (rep_s[kk]["side"] or "") != (liv_s[kk]["side"] or "")]
        res[k] = {"replay": len(rep_s), "live": len(liv_s), "matched": len(matched), "soft": soft,
                  "only_live": still_live, "only_replay": still_rep, "side_mismatch": side_mismatch,
                  "matched_keys": matched, "rep_s": rep_s, "liv_s": liv_s}
    return res


def parity_pct(r, soft=False):
    m = r["matched"] + (len(r["soft"]) if soft else 0)
    union = m + len(r["only_live"]) + len(r["only_replay"]) + (0 if soft else len(r["soft"]) * 2)
    return None if union == 0 else 100.0 * m / union


def replay_range_rows(t0_ms, t1_ms, keys=None):
    """Replay every kline key for bars whose open time is in [t0_ms, t1_ms] (all rows, with _reg_key)."""
    build_cache()
    reg = kline_registry()
    out = []
    errs = {}
    commit = code_commit()
    for k, e in reg.items():
        if keys and k not in keys:
            continue
        a = load_tf(e["tf"])
        i0 = int(np.searchsorted(a["t"], t0_ms, side="left"))
        i1 = int(np.searchsorted(a["t"], t1_ms, side="right"))
        rows, n_err = run_range(k, i0, i1, entry=e, arrays=a, commit=commit)
        for r in rows:
            r["_reg_key"] = k
        out += rows
        errs[k] = n_err
    return out, errs


def main(argv=None):
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("cache")
    r = sub.add_parser("run")
    r.add_argument("--workers", type=int, default=5)
    r.add_argument("--keys", default="")
    r.add_argument("--out", default="")
    r.add_argument("--resume-dir", default="")
    p = sub.add_parser("parity")
    p.add_argument("--days", type=int, default=5)
    p.add_argument("--since-date", default="")
    p.add_argument("--out", default="")
    args = ap.parse_args(argv)
    if args.cmd == "cache":
        print(json.dumps(build_cache(force=True), indent=1, sort_keys=True))
        return 0
    if args.cmd == "run":
        run_all(workers=args.workers, keys=[k for k in args.keys.split(",") if k] or None, out_dir=args.out or None,
                resume_dir=args.resume_dir or None)
        return 0
    if args.cmd == "parity":
        from MyTradingSys.backtest.bigtrade import parity_kline
        return parity_kline.main_parity(args)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
