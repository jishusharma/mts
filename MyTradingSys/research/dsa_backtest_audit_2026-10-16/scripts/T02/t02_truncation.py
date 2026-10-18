"""T02 truncation + poison test of every testnet layer (live_runner_cli.build_default_registry) on SYNTHETIC seeded bars.

Run from the worktree root:  python MyTradingSys/research/dsa_backtest_audit_2026-10-16/scripts/T02/t02_truncation.py [--seed 20261016] [--quick]
Writes out/trunc_results.csv, out/trunc_detail.json; synthetic bars go to %TEMP%/dsa_audit/T02/.

Test (per layer L, bars B, cut index k, T = open time of B[k], which is a CLOSED bar):
  full     = L(B[s:])                      events on all data (s = window start; 0 unless the layer needs a fixed window)
  trunc_k  = L(B[s:k+1])                   data cut after the bar that closed at T
  nan_k    = L(B[s:k+1] + NaN tail)        every bar after k replaced by NaN
  x10_k    = L(B[s:k+1] + tail x10)        every bar after k with o/h/l/c x 10
  Look-ahead  <=> events stamped t <= T differ between full / nan_k / x10_k and trunc_k.
  late    = in full (t<=T) but not in trunc_k   (event is only knowable after T: confirmation lag)
  repaint = in trunc_k but not in full (t<=T)    (a later bar changes or removes a past signal)
Lag of an event = first dense cut index at which it shows up minus its own bar index. It is compared with the layer's
declared confirm_lag_bars (+1 bar of slack in live_runner_core.run_registry once the key has state).
"""
import argparse
import copy
import csv
import json
import math
import os
import random
import sys
import tempfile
import time
import traceback

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), *([".."] * 5)))
sys.path.insert(0, ROOT)
OUT = os.path.join(os.path.dirname(__file__), "out")
TMP = os.path.join(tempfile.gettempdir(), "dsa_audit", "T02")
os.makedirs(OUT, exist_ok=True)
os.makedirs(TMP, exist_ok=True)

STEP = {"1m": 60000, "5m": 300000, "15m": 900000, "1h": 3600000}
T0 = 1704067200000  # 2024-01-01 00:00 UTC (Monday)


def synth(n, step_ms, seed, with_flow=False):
    rnd = random.Random(seed)
    price, vol, out = 40000.0, 0.0015, []
    ph = rnd.random() * 6.28
    for i in range(n):
        vol = max(0.0004, min(0.006, vol * math.exp(rnd.gauss(0, 0.08))))
        drift = 0.0006 * math.sin(i / 37.0 + ph) + 0.0003 * math.sin(i / 11.0)
        r = drift + rnd.gauss(0, vol)
        o = price * (1 + rnd.gauss(0, 0.0004))  # small open gap: with o == prev close the body-swing detectors find no swing at all
        c = o * math.exp(r)
        hi = max(o, c) * (1 + abs(rnd.gauss(0, vol * 0.6)))
        lo = min(o, c) * (1 - abs(rnd.gauss(0, vol * 0.6)))
        v = math.exp(rnd.gauss(3.0, 0.5)) * (4.0 if rnd.random() < 0.04 else 1.0)
        frac = min(0.95, max(0.05, 0.5 + 0.25 * math.tanh(r / vol) + rnd.gauss(0, 0.08)))
        b = {"t": T0 + i * step_ms, "o": o, "h": hi, "l": lo, "c": c, "v": v, "tbv": v * frac}
        if with_flow:
            lo_bin = math.floor(lo / 10.0) * 10.0
            hi_bin = math.floor(hi / 10.0) * 10.0
            nb = int((hi_bin - lo_bin) / 10.0) + 1
            parts = []
            for j in range(nb):
                share = v / nb
                parts.append("%d:%.4f:%.4f" % (lo_bin + 10 * j, share * frac, share * (1 - frac)))
            b.update({"fp": "|".join(parts), "delta": v * (2 * frac - 1), "buy_vol": v * frac,
                      "sell_vol": v * (1 - frac), "b99_buy_vol": 0.0, "b99_sell_vol": 0.0, "thr_days": 5})
        out.append(b)
        price = c
    return out


def canon(e):
    def f(x):
        if isinstance(x, float):
            return None if math.isnan(x) else round(x, 9)
        if isinstance(x, dict):
            return {k: f(v) for k, v in sorted(x.items())}
        if isinstance(x, (list, tuple)):
            return [f(v) for v in x]
        return x
    return json.dumps(f(e), sort_keys=True, default=str)


def keyed(events, T):
    """{(t, event): canonical json} for events stamped <= T."""
    d = {}
    for e in events:
        if e.get("t") is not None and e["t"] <= T:
            d[(e["t"], e.get("event"))] = canon(e)
    return d


def poison(tail, mode):
    out = []
    for b in tail:
        nb = dict(b)
        if mode == "nan":
            for k in ("o", "h", "l", "c", "v", "tbv", "delta", "buy_vol", "sell_vol"):
                if k in nb:
                    nb[k] = float("nan")
        else:
            for k in ("o", "h", "l", "c"):
                nb[k] = b[k] * 10.0
        out.append(nb)
    return out


def build_layers(funding_box, wlow_box, flow=False):
    """Registry from the real build_default_registry; network-bound entries get injected fetchers that answer as of the cut."""
    from MyTradingSys.backtest.layers.alerts import live_runner_cli as cli

    def fetch_funding(symbol, limit):
        return [(t, r) for (t, r) in funding_box["series"] if t <= funding_box["now"]]

    reg = cli.build_default_registry(fetch_funding=fetch_funding, history_fetch=lambda *a, **k: [])
    reg["wlow_bounce|bbrsi60|1h"]["fn"] = cli.make_wlow_bounce_layer(
        fetch_candles=lambda: wlow_box["bars"], fetch_oi=lambda K: (None, None), log_path=None)
    reg["fabio|v3_grid|1m"]["fn"] = cli.make_fabio_v3_layer(flow_fn=lambda bars: bars)
    for k, e in reg.items():
        raw = getattr(e["fn"], "raw", None)
        e["need"] = cli.HIST_NEED_BARS.get({"session_levels|session_levels|1m": "session_levels",
                                            "candle_close|candle_close|1m": "candle_close",
                                            "levels|confluence|1m": "levels_confluence"}.get(k, ""), 0)
        e["call"] = raw or e["fn"]
    return reg


def run_layer(reg, key, bars, funding_box, wlow_box):
    e = reg[key]
    if key.startswith("positioning|"):
        funding_box["now"] = bars[-1]["t"] + STEP[e["tf"]]  # as of the close of the last bar
    if key.startswith("wlow_bounce|"):
        wlow_box["bars"] = bars
    return e["call"](bars)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--seed", type=int, default=20261016)
    ap.add_argument("--quick", action="store_true")
    ap.add_argument("--only", default="")
    a = ap.parse_args()
    print("seed", a.seed, "root", ROOT)
    rnd = random.Random(a.seed)
    n_rand = 12 if a.quick else 200
    funding_box = {"series": [], "now": 0}
    wlow_box = {"bars": []}
    reg = build_layers(funding_box, wlow_box)
    rows, detail = [], {}
    series_cache = {}
    for key, ent in reg.items():
        if a.only and a.only not in key:
            continue
        tf, need = ent["tf"], ent["need"]
        flow = key.startswith("fabio|v3_grid")
        heavy = need >= 2000
        n = (need + 450) if need else (1500 if tf != "1h" else 1600)
        if key.startswith("fabio|v3_grid"):
            n = 700
        ck = (tf, n, flow)
        if ck not in series_cache:
            sd = a.seed + len(series_cache)
            series_cache[ck] = synth(n, STEP[tf], sd, with_flow=flow)
            with open(os.path.join(TMP, "synth_%s_%d%s_seed%d.json" % (tf, n, "_flow" if flow else "", sd)), "w") as fh:
                json.dump(series_cache[ck], fh)
        B = series_cache[ck]
        funding_box["series"] = [(T0 + j * 8 * 3600000, 0.0001 * math.sin(j / 5.0) + (0.0006 if (j // 9) % 3 == 0 else -0.0004))
                                 for j in range(-4, n * STEP[tf] // (8 * 3600000) + 3)]
        warm = max(120, need) if need else 120
        cuts_rand = sorted(set(rnd.randrange(warm if not need else n - 320, n - 1) for _ in range(n_rand)))
        dense_lo = n - 150 if not heavy else n - 40
        dense = list(range(dense_lo, n - 1)) if not (a.quick and not heavy) else list(range(n - 40, n - 1))
        if heavy:
            cuts_rand = sorted(set(cuts_rand[:(6 if a.quick else 30)]))
            dense = dense[::4] if not a.quick else dense[::10]
        if flow:   # 54 engine runs per call: bounded cut count (DECISION OURS, time cap)
            cuts_rand, dense = cuts_rand[:3], list(range(n - 8, n - 1))
        cuts = sorted(set(cuts_rand) | set(dense))
        t_start = time.time()
        res = {"key": key, "n_bars": n, "cuts": len(cuts), "late": 0, "repaint": 0, "nan_diff": 0, "x10_diff": 0,
               "nan_err": 0, "x10_err": 0, "trunc_err": 0, "max_lag": 0, "n_events_full": 0, "notes": ""}
        try:
            s0 = (lambda k: max(0, k + 1 - need) if need else 0)
            first_seen, seen_last, lag_by_event = {}, {}, {}
            full0 = None
            for k in cuts:
                s = s0(k)
                T = B[k]["t"]
                if need:
                    full = run_layer(reg, key, B[s:], funding_box, wlow_box)
                else:
                    if full0 is None:
                        full0 = run_layer(reg, key, B, funding_box, wlow_box)
                    full = full0
                try:
                    tr = run_layer(reg, key, B[s:k + 1], funding_box, wlow_box)
                except Exception as exc:  # noqa: BLE001
                    res["trunc_err"] += 1
                    res["notes"] = ("trunc_err: %s" % exc)[:120]
                    continue
                Ft, At = keyed(full, T), keyed(tr, T)
                res["n_events_full"] = max(res["n_events_full"], len(full))
                for kk in set(Ft) - set(At):
                    res["late"] += 1
                    idx = (kk[0] - T0) // STEP[tf]
                    lag_by_event.setdefault(kk, None)
                for kk in set(At) - set(Ft):
                    res["repaint"] += 1
                    detail.setdefault(key, []).append({"k": k, "repaint": [kk[0], kk[1]]})
                for kk in At:
                    if kk not in first_seen:
                        first_seen[kk] = k
                for mode in ("nan", "x10"):
                    try:
                        pz = run_layer(reg, key, B[s:k + 1] + poison(B[k + 1:], mode), funding_box, wlow_box)
                    except Exception as exc:  # noqa: BLE001
                        res[mode + "_err"] += 1
                        res["notes"] = (res["notes"] + " %s_err:%s" % (mode, str(exc)[:60]))[:160]
                        continue
                    Pt = keyed(pz, T)
                    if Pt != At:
                        res[mode + "_diff"] += 1
                        detail.setdefault(key, []).append({"k": k, "mode": mode, "extra": [list(x) for x in set(Pt) - set(At)][:3],
                                                           "missing": [list(x) for x in set(At) - set(Pt)][:3]})
            # lag of each event stamped inside the dense range: first cut at which it appeared minus its own index
            fullall = run_layer(reg, key, B[s0(n - 1):], funding_box, wlow_box)
            lags = []
            for e in fullall:
                kk = (e["t"], e.get("event"))
                idx = (e["t"] - T0) // STEP[tf]
                if idx >= dense[0] and kk in first_seen:
                    lags.append(first_seen[kk] - idx)
            if lags:
                res["max_lag"] = max(lags)
                res["lag_hist"] = {str(x): lags.count(x) for x in sorted(set(lags))}
        except Exception as exc:  # noqa: BLE001
            res["notes"] = ("HARNESS_ERR %s: %s" % (type(exc).__name__, exc))[:200]
            detail.setdefault(key, []).append({"traceback": traceback.format_exc()[-800:]})
        res["declared_lag"] = int(ent.get("confirm_lag_bars", 0))
        res["secs"] = round(time.time() - t_start, 1)
        if res["n_events_full"] == 0 and not res["notes"]:
            res["verdict"] = "VACUOUS (0 events on synthetic bars)"
        elif res["notes"].startswith("HARNESS_ERR"):
            res["verdict"] = "HARNESS_ERR"
        elif res["repaint"] > 0:
            res["verdict"] = "FAIL (repaint)"
        elif res["late"] > 0:   # lag is only read when an event was missing at a cut at/after its stamp (sparse cuts alias the lag)
            res["verdict"] = ("PASS-LAG (lag %d <= declared %d)" if res["max_lag"] <= res["declared_lag"] else "FAIL-LAG (lag %d > declared %d)") % (res["max_lag"], res["declared_lag"])
        elif res["nan_diff"] or res["x10_diff"]:
            res["verdict"] = "FAIL (poison)"
        else:
            res["verdict"] = "PASS"
        print("%-44s n=%d cuts=%d events=%d late=%d repaint=%d nan_diff=%d x10_diff=%d lag=%d/%d err(tr/nan/x10)=%d/%d/%d %s  %.1fs"
              % (key, n, len(cuts), res["n_events_full"], res["late"], res["repaint"], res["nan_diff"], res["x10_diff"],
                 res["max_lag"], res["declared_lag"], res["trunc_err"], res["nan_err"], res["x10_err"], res["verdict"], res["secs"]), flush=True)
        rows.append(res)
    suffix = ("_quick" if a.quick else "") + (("_" + "".join(ch for ch in a.only if ch.isalnum())) if a.only else "")
    with open(os.path.join(OUT, "trunc_results%s.csv" % suffix), "w", newline="\n") as fh:
        cols = ["key", "n_bars", "cuts", "n_events_full", "late", "repaint", "nan_diff", "x10_diff", "trunc_err", "nan_err",
                "x10_err", "max_lag", "declared_lag", "verdict", "secs", "notes"]
        w = csv.DictWriter(fh, fieldnames=cols, extrasaction="ignore", lineterminator="\n")
        w.writeheader()
        w.writerows(rows)
    with open(os.path.join(OUT, "trunc_detail%s.json" % suffix), "w", newline="\n") as fh:
        json.dump({"seed": a.seed, "rows": rows, "detail": {k: v[:25] for k, v in detail.items()}}, fh, indent=1, default=str)


if __name__ == "__main__":
    main()
