"""T09 live/backtest parity harness (audit 2026-10-16). Read-only on repo code and data; writes only to scripts/T09/out/.

Replays 30 fixed DEV days (before 2024-07-01) bar by bar through the LIVE code path
(live_runner_cli.build_default_registry + poll_once, with a fake fetch_fn, every network path patched to raise),
then runs each layer's BACKTEST-side signal code on the same days and diffs the signals.

Run from the worktree root:  python MyTradingSys/research/dsa_backtest_audit_2026-10-16/scripts/T09/parity_core.py
"""
import bisect
import datetime as dt
import json
import os
import random
import socket
import sys
import tempfile
import urllib.request
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[4]
sys.path.insert(0, str(REPO))

OUT = HERE / "out"
RESULT = OUT / "parity_result.json"
KLINE_ROOT = os.environ.get("T09_KLINE_ROOT", "F:/MTS/data/tom_raw")
FUNDING_DIR = Path(os.environ.get("T09_FUNDING_DIR", "F:/MTS/Dumps/backtest/raw/fundingRate"))
DEV_END_MS = int(dt.datetime(2024, 7, 1, tzinfo=dt.timezone.utc).timestamp() * 1000)
SEED = 20261016
TF_MS = {"1m": 60000, "5m": 300000, "15m": 900000, "1h": 3600000}
DAY_MS = 86400000
WARM_MIN = 180            # minutes of state warm-up before each replay day (alerts discarded)
BT_WINDOW_BARS = 2000     # backtest-side warm-up window (bars of the layer's own tf) before each day
# Live keys not replayed (need history fetches or footprint data outside DEV); reason is printed in the report.
SKIP_KEYS = {
    "session_levels|session_levels|1m": "needs 2.9k 1m bars of history per step (HistoryStore paging); no backtest twin in scope",
    "candle_close|candle_close|1m": "needs 10.2k 1m bars per step (HistoryStore); study FAIL 0/126 arms (candle_close_2026-10-14)",
    "levels|confluence|1m": "needs 24.5k 1m bars per step; footprint-window study only",
    "fabio|v3_grid|1m": "needs order-flow columns (footprint 2024-12-02..2025-03-31 only), absent in DEV: silent on klines",
}


# ----------------------------------------------------------------------------- data
def load_dev_1m():
    from MyTradingSys.backtest.bt.bt_data import load_klines
    return load_klines(KLINE_ROOT, "klines", end_ms=DEV_END_MS)


def resample(bars1m, tf):
    ms = TF_MS[tf]
    n = ms // 60000
    out, cur, cnt = [], None, 0
    for b in bars1m:
        k = b["t"] // ms * ms
        if cur is None or cur["t"] != k:
            if cur is not None and cnt == n:
                out.append(cur)
            cur, cnt = {"t": k, "o": b["o"], "h": b["h"], "l": b["l"], "c": b["c"], "v": b["v"], "tbv": b["tbv"]}, 1
        else:
            cur["h"] = max(cur["h"], b["h"]); cur["l"] = min(cur["l"], b["l"]); cur["c"] = b["c"]
            cur["v"] += b["v"]; cur["tbv"] += b["tbv"]; cnt += 1
    if cur is not None and cnt == n:
        out.append(cur)
    return out


def load_funding(end_ms):
    import csv
    rows = []
    for f in sorted(FUNDING_DIR.glob("*.csv")):
        with open(f, newline="", encoding="utf-8") as fh:
            for r in csv.DictReader(fh):
                t = int(r["calc_time"])
                if t < end_ms:
                    rows.append((t, float(r["last_funding_rate"])))
    return sorted(rows)


def pick_days(bars1m, seed=SEED):
    """30 DEV days: 10 trend, 10 range, 10 high-volatility (seeded draw from the top-30 pool of each class). Skips the first 30 days."""
    by = {}
    for b in bars1m:
        d = b["t"] // DAY_MS
        s = by.setdefault(d, [b["o"], b["h"], b["l"], b["c"], 0])
        s[1] = max(s[1], b["h"]); s[2] = min(s[2], b["l"]); s[3] = b["c"]; s[4] += 1
    days = sorted(d for d, s in by.items() if s[4] == 1440)[30:]
    stat = {d: ((by[d][1] - by[d][2]) / by[d][0], abs(by[d][3] - by[d][0]) / by[d][0]) for d in days}
    rng = random.Random(seed)
    med = sorted(v[0] for v in stat.values())[len(stat) // 2]
    trend = sorted((d for d in days if stat[d][0] >= med), key=lambda d: -stat[d][1] / stat[d][0])[:30]
    quiet = sorted(days, key=lambda d: stat[d][0])[:30]
    vol = sorted(days, key=lambda d: -stat[d][0])[:30]
    chosen, used = [], set()
    for pool, tag in ((trend, "trend"), (quiet, "range"), (vol, "highvol")):
        pool = [d for d in pool if d not in used]
        pick = sorted(rng.sample(pool, 10))
        used.update(pick)
        chosen += [(d, tag) for d in pick]
    return sorted(chosen)


# ----------------------------------------------------------------------------- network block
class NetBlock:
    """Every network path raises; attempts are counted."""
    def __init__(self):
        self.attempts = 0
        self._saved = {}

    def _raiser(self, *a, **k):
        self.attempts += 1
        raise RuntimeError("T09: network call blocked")

    def __enter__(self):
        from MyTradingSys.backtest.layers.alerts import live_runner_cli as cli, live_layers as ll
        targets = [(urllib.request, "urlopen"), (socket.socket, "connect"), (socket, "create_connection"),
                   (cli, "default_fetch_klines"), (cli, "_wlow_default_fetch"), (cli, "_wlow_default_oi"),
                   (cli, "_hist_default_page"), (ll, "default_fetch_funding")]
        for obj, name in targets:
            self._saved[(obj, name)] = getattr(obj, name)
            setattr(obj, name, self._raiser)
        return self

    def __exit__(self, *a):
        for (obj, name), v in self._saved.items():
            setattr(obj, name, v)


# ----------------------------------------------------------------------------- replay
def _no_oi(k):
    raise RuntimeError('T09: OI not available in DEV replay (fake, not a network call)')


class Feed:
    def __init__(self, series):
        self.series = series                       # tf -> list of bars
        self.times = {tf: [b["t"] for b in s] for tf, s in series.items()}
        self.now = 0

    def fetch(self, symbol, interval, limit):
        s, ts = self.series[interval], self.times[interval]
        j = bisect.bisect_right(ts, self.now) - 1   # forming bar (dropped by fetch_closed_bars)
        rows = s[max(0, j - limit + 1): j + 1]
        ms = TF_MS[interval]
        return [[b["t"], b["o"], b["h"], b["l"], b["c"], b["v"], b["t"] + ms - 1, 0, 0, b["tbv"], 0, 0] for b in rows]

    def wlow_candles(self):
        s, ts = self.series["1h"], self.times["1h"]
        j = bisect.bisect_right(ts, self.now) - 1
        return [dict(b) for b in s[max(0, j - 500): j]]     # closed 1h bars only


def replay(days, series, funding, log=print):
    from MyTradingSys.backtest.layers.alerts import live_runner_cli as cli
    from MyTradingSys.execution import auto_trader as at
    feed = Feed(series)
    tmp = Path(tempfile.mkdtemp(prefix="t09_"))
    cfg = at.load_config(REPO / "MyTradingSys" / "execution" / "auto_trader_config.json")
    ftimes = [f[0] for f in funding]

    def fake_funding(symbol, limit):
        j = bisect.bisect_right(ftimes, feed.now)
        return funding[max(0, j - limit): j]

    net = NetBlock()
    rows, decisions = [], []
    with net:
        # wlow shares one process-wide closure; build the registry inside the block so its default fetchers are the blocked ones
        reg = cli.build_default_registry(fetch_funding=fake_funding, history_fetch=net._raiser)
        # wlow: inject the local 1h feed and a failing OI fetch (None OI), log to TEMP
        reg["wlow_bounce|bbrsi60|1h"] = {**reg["wlow_bounce|bbrsi60|1h"],
                                         "fn": cli.make_wlow_bounce_layer(fetch_candles=feed.wlow_candles,
                                                                          fetch_oi=_no_oi,
                                                                          log_path=str(tmp / "wlow.jsonl"))}
        net.attempts = 0                           # building the registry must not count; only replay calls do
        replayed = {k: v for k, v in reg.items() if k not in SKIP_KEYS}
        tfs = sorted({v["tf"] for v in replayed.values()})
        for (d, tag) in days:
            day0 = d * DAY_MS
            state = {"last_t": {}, "prev_events": {}}
            m = day0 - WARM_MIN * 60000
            while m <= day0 + DAY_MS:
                feed.now = m + 5000
                res = cli.poll_once(replayed, "BTCUSDT", tfs, feed.fetch, state, 100)
                state = res["state"]
                if m >= day0:
                    now = dt.datetime.fromtimestamp(feed.now / 1000, dt.timezone.utc)
                    for a in res["alerts"]:
                        side = at.layer_side(a, cfg)
                        sig = at.layer_signal(a, cfg, now)
                        rows.append({"day": d, "key": "%s|%s|%s" % (a["layer"], a["sub"], a["tf"]), "event": a.get("event"),
                                     "t": a["t_close"], "t_confirm": a.get("t_confirm"), "tf": a["tf"],
                                     "side": side, "alert_side": a.get("side"), "collection_only": bool(a.get("collection_only")),
                                     "reject": sig.get("reject"), "source": sig["source"]})
                    for e in res["errors"]:
                        decisions.append({"day": d, "key": e["key"], "error": e["error"][:120]})
                m += 60000
            log("day %s %s done, alerts so far %d" % (dt.datetime.fromtimestamp(day0 / 1000, dt.timezone.utc).date(), tag, len(rows)))
    return {"alerts": rows, "errors": decisions, "network_attempts": net.attempts, "replayed_keys": sorted(replayed),
            "skipped": SKIP_KEYS}


# ----------------------------------------------------------------------------- backtest side
def _ek(bars, i, tf):
    return bars[i]["t"] + TF_MS[tf]


def backtest_events(key, bars_tf, bars_other, funding):
    """Backtest-side signals for one live key on a long window. Returns list of (entry_close_ms, side, label), or None (no backtest twin).
    Entry-close time = signal bar open + tf, so different-tf studies compare on the same clock."""
    layer, sub, tf = key.split("|")
    out = []
    if layer == "rsi" and sub == "rsi_events":
        from MyTradingSys.backtest.layers.rsi.rsi_core import rsi_core
        from MyTradingSys.backtest.layers.rsi.rsi_events import rsi_events
        closes = [b["c"] for b in bars_tf]; ts = [b["t"] for b in bars_tf]
        rsi = rsi_core(closes, period=14)
        tol40 = {"15m": 1.0}.get(tf, 0.5)           # D3 chosen tol: 15m 1.0, 1h 0.5 (5m never tested: 0.5 assumed)
        tol60 = {"15m": 1.0, "1h": 1.5}.get(tf, 0.5)
        for e in rsi_events(rsi, ts, level=40.0, tolerance=tol40):
            if e["event"] == "support":
                out.append((e["t"] + TF_MS[tf], "long", "support@40"))
        for e in rsi_events(rsi, ts, level=60.0, tolerance=tol60):
            if e["event"] == "rejection":
                out.append((e["t"] + TF_MS[tf], "short", "rejection@60"))
        return out
    if layer == "rsi" and sub in ("malkan_bull", "malkan_bear"):
        from MyTradingSys.backtest.layers.rsi.run_rsi_backtest import malkan_events
        evs = malkan_events(bars_tf, {"period": 14, "tolerance": 2.0, "lookback": 20})
        want = "long" if sub == "malkan_bull" else "short"
        return [(_ek(bars_tf, e["i"], tf), e["side"], "malkan") for e in evs if e["side"] == want]
    if layer == "fabio" and sub == "cvd_absorption":
        from MyTradingSys.backtest.layers.fabio.run_backtest import cvd_fn
        return [(_ek(bars_tf, e["i"], tf), e["side"], e.get("kind", "cvd")) for e in cvd_fn(bars_tf, left=2, right=2, price_tolerance=0.001)]
    if layer == "fabio" and sub == "escalation":
        from MyTradingSys.backtest.layers.fabio.run_backtest import escalation_fn
        return [(_ek(bars_tf, e["i"], tf), e["side"], e.get("kind", "esc")) for e in
                escalation_fn(bars_tf, level_tolerance=0.001, aggression_k=2.0, record_lookback=20)]
    if layer == "fabio" and sub == "volume_fvg":
        # verbatim event loop of fabio/run_backtest.py run_fvg (real level, 'bounce' reading, touch scan from start+1)
        from MyTradingSys.backtest.layers.fabio.fabio_volume_fvg import swing_legs, build_profile, value_area, lowest_volume_level
        legs = swing_legs(bars_tf, left=2, right=2, use_body=True)
        closes = [b["c"] for b in bars_tf]
        for leg in legs:
            a_i, b_i = min(leg["a_i"], leg["b_i"]), max(leg["a_i"], leg["b_i"])
            if b_i - a_i < 20:
                continue
            try:
                profile = build_profile(bars_tf, a_i, b_i, n_bins=20)
                lvl = lowest_volume_level(profile, value_area(profile, pct=0.70))
            except ValueError:
                continue
            start = leg["confirmed_i"]
            mid = (lvl["price_lo"] + lvl["price_hi"]) / 2.0
            for i in range(start + 1, min(start + 1 + 200, len(bars_tf) - 1)):
                if bars_tf[i]["l"] <= mid <= bars_tf[i]["h"]:
                    out.append((_ek(bars_tf, i, tf), "long" if closes[start] > mid else "short", "fvg_bounce"))
                    break
        return sorted(out)
    if layer == "session" and sub == "session_momentum":
        from MyTradingSys.backtest.layers.session.session_momentum import session_momentum_events
        return [(_ek(bars_other["5m"], e["i"], "5m"), e["side"], "sm_5m") for e in session_momentum_events(bars_other["5m"], bar_min=5)]
    if layer == "positioning":
        from MyTradingSys.backtest.layers.positioning.funding_cvd_fade import funding_cvd_fade_events
        b15 = bars_other["15m"]
        evs = funding_cvd_fade_events(b15, funding)
        return [(_ek(b15, e["i"], "15m"), e["side"], "fund_15m") for e in evs]
    if layer == "cryptocred":
        from MyTradingSys.backtest.layers.cryptocred import cc_setups as cc
        fn = {"sr_flip": cc.setup1_sr_flip, "fib_pullback": cc.setup2_fib_pullback, "failed_msb": cc.setup3_failed_msb_reversal}[sub]
        return [(s["entry_t"] + TF_MS[tf], s["side"], sub) for s in fn(bars_tf)]
    if layer == "turn_of_candle":
        from MyTradingSys.backtest.layers.turn_of_candle.turn_of_candle import turn_of_candle_events
        for e in turn_of_candle_events(bars_tf, lead_minutes=1):
            i = e["i"]; o = i - 14
            if o >= 0 and bars_tf[i]["t"] - bars_tf[o]["t"] == 14 * 60000 and bars_tf[o]["v"] > 0:
                imb = (2 * bars_tf[o]["tbv"] - bars_tf[o]["v"]) / bars_tf[o]["v"]
                if imb:
                    out.append((_ek(bars_tf, i, tf), "long" if imb > 0 else "short", "toc_c3_imbalance"))
        return out
    return None


def window(bars, day0, tf):
    ts = [b["t"] for b in bars]
    lo = bisect.bisect_left(ts, day0 - BT_WINDOW_BARS * TF_MS[tf])
    hi = bisect.bisect_left(ts, day0 + DAY_MS)
    return bars[lo:hi]


def diff(live, bt, tfms):
    """live, bt: lists of (t, side). exact (t,side) / side_diff (same t) / off_by_one (|dt| == one bar) / live_only / bt_only."""
    L = {}; B = {}
    for t, s in live:
        L.setdefault(t, []).append(s)
    for t, s in bt:
        B.setdefault(t, []).append(s)
    res = {"same": 0, "side_diff": 0, "off_by_one": 0, "live_only": 0, "bt_only": 0}
    ex = {k: [] for k in res}
    lrest, brest = [], []
    for t in sorted(set(L) | set(B)):
        ls, bs = list(L.get(t, [])), list(B.get(t, []))
        for s in list(ls):
            if s in bs:
                bs.remove(s); ls.remove(s); res["same"] += 1
        while ls and bs:
            ls.pop(); bs.pop(); res["side_diff"] += 1
            if len(ex["side_diff"]) < 5:
                ex["side_diff"].append(t)
        lrest += [(t, s) for s in ls]; brest += [(t, s) for s in bs]
    bset = list(brest)
    liveonly = []
    for t, s in lrest:
        hit = next((x for x in bset if abs(x[0] - t) == tfms), None)
        if hit:
            bset.remove(hit); res["off_by_one"] += 1
            if len(ex["off_by_one"]) < 5:
                ex["off_by_one"].append([t, hit[0]])
        else:
            res["live_only"] += 1
            liveonly.append((t, s))
            if len(ex["live_only"]) < 5:
                ex["live_only"].append([t, s])
    res["bt_only"] = len(bset)
    ex["bt_only"] = [[t, s] for t, s in bset[:5]]
    return res, ex, liveonly, sorted(bset)


def compute(log=print):
    bars1m = load_dev_1m()
    days = pick_days(bars1m)
    if os.environ.get('T09_NDAYS'):
        days = days[:: max(1, len(days) // int(os.environ['T09_NDAYS']))][:int(os.environ['T09_NDAYS'])]
    series = {"1m": bars1m, "5m": resample(bars1m, "5m"), "15m": resample(bars1m, "15m"), "1h": resample(bars1m, "1h")}
    funding = load_funding(DEV_END_MS)
    log("days: " + ", ".join("%s:%s" % (dt.datetime.fromtimestamp(d * DAY_MS / 1000, dt.timezone.utc).date(), g) for d, g in days))
    live = replay(days, series, funding, log)
    per = {}
    keys = live["replayed_keys"]
    for key in keys:
        layer, sub, tf = key.split("|")
        L_all = [a for a in live["alerts"] if a["key"] == key]
        rec = {"live_alerts": len(L_all), "live_tradable_side": sum(1 for a in L_all if a["side"]),
               "live_accepted": sum(1 for a in L_all if a["side"] and not a["reject"]),
               "reject_reasons": {}, "events": {}}
        for a in L_all:
            rec["events"][a["event"].split("_")[0] if a["event"] else "?"] = rec["events"].get(a["event"].split("_")[0] if a["event"] else "?", 0) + 1
            if a["reject"]:
                r = a["reject"].split(" ")[0] + " " + (a["reject"].split(" ")[1] if " " in a["reject"] else "")
                rec["reject_reasons"][r.strip()] = rec["reject_reasons"].get(r.strip(), 0) + 1
        bt_all = []
        has_bt = True
        for (d, g) in days:
            day0 = d * DAY_MS
            wb = {t2: window(series[t2], day0, t2) for t2 in ("1m", "5m", "15m", "1h")} if tf != "1m" else {}
            if tf == "1m":
                wb = {"1m": [b for b in series["1m"] if day0 - 120 * 60000 <= b["t"] < day0 + DAY_MS]}
                wb.update({t2: window(series[t2], day0, t2) for t2 in ("5m", "15m", "1h")})
            fund_w = funding
            ev = backtest_events(key, wb[tf], wb, [f for f in fund_w if f[0] < day0 + DAY_MS])
            if ev is None:
                has_bt = False
                break
            bt_all += [(t, s) for (t, s, lab) in ev if day0 < t <= day0 + DAY_MS]
        if not has_bt:
            rec["backtest"] = None
        else:
            live_sig = [(a["t"] + TF_MS[tf], a["side"]) for a in L_all if a["side"]
                        and a["day"] * DAY_MS < a["t"] + TF_MS[tf] <= (a["day"] + 1) * DAY_MS]
            res, ex, lo_items, bo_items = diff(live_sig, bt_all, TF_MS[tf])
            rec["backtest"] = {"n": len(bt_all), **res, "examples": ex}
            ev_at = {}
            for a in L_all:
                if a["side"]:
                    ev_at[(a["t"] + TF_MS[tf], a["side"])] = a["event"].split("_")[0] if a["event"] else "?"
            lo_by = {}
            for it in lo_items:
                lo_by[ev_at.get(it, "?")] = lo_by.get(ev_at.get(it, "?"), 0) + 1
            rec["backtest"]["live_only_by_event"] = lo_by
            tr_by = {}
            for a in L_all:
                if a["side"]:
                    k2 = a["event"].split("_")[0] if a["event"] else "?"
                    tr_by[k2] = tr_by.get(k2, 0) + 1
            rec["tradable_by_event"] = tr_by
            if bo_items and tf in ("5m", "15m", "1h") and layer in ("rsi", "fabio", "cryptocred"):
                # is each backtest-only signal visible in the live 99-bar window ending at its bar?
                ser = series[tf]; tsx = [b["t"] for b in ser]
                inwin = 0
                for (t_ec, sd) in bo_items:
                    idx = bisect.bisect_left(tsx, t_ec - TF_MS[tf])
                    seen = False
                    for end in (idx, idx + 1):
                        w = ser[max(0, end - 98): end + 1]
                        if len(w) < 99 and end - 98 > 0:
                            continue
                        evs = backtest_events(key, w, {}, [])
                        if evs and any(abs(e[0] - t_ec) <= 0 and e[1] == sd for e in evs):
                            seen = True; break
                    inwin += seen
                rec["backtest"]["bt_only_visible_in_99bar_window"] = inwin
                rec["backtest"]["bt_only_needs_longer_history"] = len(bo_items) - inwin
        per[key] = rec
        log("%s live=%d tradable=%d bt=%s" % (key, rec["live_alerts"], rec["live_tradable_side"], rec["backtest"] and {k: v for k, v in rec["backtest"].items() if k != "examples"}))
    return {"days": [[d, g] for d, g in days], "network_attempts": live["network_attempts"], "per_key": per,
            "skipped": live["skipped"], "errors": live["errors"][:50], "n_errors": len(live["errors"]), "seed": SEED,
            "head_sha_note": "replay of worktree HEAD; layers/execution diff vs live checkout sha is empty (see report)"}


def load_or_run():
    if RESULT.exists():
        return json.loads(RESULT.read_text(encoding="utf-8"))
    OUT.mkdir(parents=True, exist_ok=True)
    res = compute()
    RESULT.write_text(json.dumps(res, indent=1), encoding="utf-8", newline="\n")
    return res


if __name__ == "__main__":
    if RESULT.exists() and "--force" not in sys.argv:
        print("result exists; pass --force to rerun")
    else:
        OUT.mkdir(parents=True, exist_ok=True)
        r = compute()
        RESULT.write_text(json.dumps(r, indent=1), encoding="utf-8", newline="\n")
        print("wrote", RESULT, "network_attempts", r["network_attempts"])
