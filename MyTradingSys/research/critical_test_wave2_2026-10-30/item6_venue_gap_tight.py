"""Card venue-gap-tight-stop-rerun-on-deribit: tight-stop and wick-touch rerun of item6 on DEV month 2024-05.

Copy of item6_venue_gap.py (which stays unchanged) with two new parameters: stop_pct and wick_touch.
Wick-touch entry (OURS): the event is taken only when the next 1m bar's low (long) or high (short) comes within
WICK_PCT of the 1h signal close, and the entry price is that wick extreme; otherwise the event is skipped.
Run: python MyTradingSys/research/critical_test_wave2_2026-10-30/item6_venue_gap_tight.py
"""
import csv
import json
import statistics
import sys
import time
import urllib.request
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO / "MyTradingSys" / "backtest"))
sys.path.insert(0, str(REPO / "MyTradingSys" / "backtest" / "bt"))
import fees  # noqa: E402
import bt_engine  # noqa: E402

MONTH = "2024-05"
T0 = 1714521600000
T1 = 1717200000000
DEV_END = 1719792000000
BIN_DIR = Path("F:/MTS/data/tom_raw/klines")
DER_CACHE = Path("F:/MTS/data/deribit") / f"BTC-PERPETUAL-1m-{MONTH}.csv"
FUND_ROOT = Path("F:/MTS/Dumps/backtest/raw")
OUT = Path(__file__).resolve().parent
DER_FUND_CACHE = OUT / f"deribit_funding_{MONTH}.csv"
RESULT_OUT = REPO / "sim_desk" / "results" / "venue-gap-tight-stop-deribit.json"
RSI_N, RSI_LO, RSI_HI = 14, 30.0, 70.0
TARGET_R, MAX_BARS = 2.0, 960
WICK_PCT = 0.01
VARIANTS = [
    {"name": "stop_1p0", "stop_pct": 0.01, "wick_touch": False},
    {"name": "stop_0p10", "stop_pct": 0.001, "wick_touch": False},
    {"name": "stop_0p15", "stop_pct": 0.0015, "wick_touch": False},
    {"name": "wick_touch_1p0", "stop_pct": 0.01, "wick_touch": True},
]


def get(url):
    with urllib.request.urlopen(url, timeout=30) as r:
        return json.loads(r.read().decode())


def refuse_after_dev(t):
    if t >= DEV_END:
        raise ValueError(f"bar {t} at or after DEV end 2024-07-01: refused")


def load_binance():
    bars = {}
    with open(BIN_DIR / f"BTCUSDT-1m-{MONTH}.csv", newline="") as f:
        for row in csv.DictReader(f):
            t = int(row["open_time"])
            refuse_after_dev(t)
            if T0 <= t < T1:
                bars[t] = {"t": t, "o": float(row["open"]), "h": float(row["high"]),
                           "l": float(row["low"]), "c": float(row["close"])}
    return bars


def load_deribit():
    bars = {}
    with open(DER_CACHE, newline="") as f:
        for row in csv.DictReader(f):
            t = int(row["t"])
            refuse_after_dev(t)
            if T0 <= t < T1:
                bars[t] = {"t": t, "o": float(row["o"]), "h": float(row["h"]),
                           "l": float(row["l"]), "c": float(row["c"])}
    return bars


def funding_binance():
    import bt_data
    return [r for r in bt_data.load_funding(FUND_ROOT) if T0 - 86400000 <= r[0] < min(T1 + 86400000, DEV_END)]


def funding_deribit():
    if DER_FUND_CACHE.exists():
        rows = []
        with open(DER_FUND_CACHE, newline="") as f:
            for row in csv.DictReader(f):
                rows.append((int(row["t"]), float(row["rate"])))
        return rows
    out = []
    for s in range(T0 - 86400000, T1 + 86400000, 10 * 86400000):
        e = min(s + 10 * 86400000, T1 + 86400000)
        d = get("https://www.deribit.com/api/v2/public/get_funding_rate_history?instrument_name=BTC-PERPETUAL"
                f"&start_timestamp={s}&end_timestamp={e}")["result"]
        out += [(int(x["timestamp"]), float(x["interest_1h"])) for x in d]
        time.sleep(0.2)
    out = sorted(set(out))
    with open(DER_FUND_CACHE, "w", newline="\n") as fh:
        w = csv.writer(fh, lineterminator="\n")
        w.writerow(["t", "rate"])
        w.writerows(out)
    return out


def q(xs, p):
    xs = sorted(xs)
    return xs[min(len(xs) - 1, int(p * len(xs)))]


def rsi_events(bars):
    hrs = sorted(t for t in bars if t % 3600000 == 3600000 - 60000)
    closes = [(t, bars[t]["c"]) for t in hrs]
    ev, gains, losses, prev = [], [], [], None
    for i in range(1, len(closes)):
        ch = closes[i][1] - closes[i - 1][1]
        gains.append(max(ch, 0.0))
        losses.append(max(-ch, 0.0))
        if len(gains) < RSI_N:
            continue
        g, l_ = statistics.fmean(gains[-RSI_N:]), statistics.fmean(losses[-RSI_N:])
        r = 100.0 if l_ == 0 else 100.0 - 100.0 / (1 + g / l_)
        if prev is not None:
            if r < RSI_LO <= prev:
                ev.append((closes[i][0], "long"))
            elif r > RSI_HI >= prev:
                ev.append((closes[i][0], "short"))
        prev = r
    return ev


def run_layer(bars, funding, events, stop_pct, wick_touch):
    seq = [bars[t] for t in sorted(bars)]
    out = []
    for t_sig, side in events:
        nxt = bars.get(t_sig + 60000)
        if nxt is None:
            continue
        sgn = 1 if side == "long" else -1
        px = nxt["o"]
        if wick_touch:
            ref = bars[t_sig]["c"]
            touch = nxt["l"] if side == "long" else nxt["h"]
            if abs(touch - ref) / ref > WICK_PCT:
                continue
            px = touch
        stop = px * (1 - sgn * stop_pct)
        tgt = px * (1 + sgn * stop_pct * TARGET_R)
        r = bt_engine.simulate_trade(side, px, nxt["t"] - 1, stop, [(tgt, 1.0)],
                                     [b for b in seq if b["t"] >= nxt["t"]],
                                     funding=funding, taker_fee=fees.DERIBIT_TAKER, maker_fee=fees.DERIBIT_MAKER,
                                     max_bars=MAX_BARS)
        out.append({"t_sig": t_sig, "side": side, "entry": px, "net_r": r["net_r"], "exit": r["exit_reason"]})
    return out


def summary(tr):
    nr = [x["net_r"] for x in tr if x["net_r"] is not None]
    stops = sum(1 for x in tr if x["exit"] == "stop")
    return {"events_used": len(tr), "n": len(nr), "stops": stops,
            "net_r_sum": sum(nr) if nr else 0.0,
            "mean_r": statistics.fmean(nr) if nr else None}


def main():
    b, d = load_binance(), load_deribit()
    common = sorted(set(b) & set(d))
    close_gap = [abs((d[t]["c"] - b[t]["c"]) / b[t]["c"] * 1e4) for t in common]
    gap_used = {"field": "close (Deribit minus Binance, bps of Binance)", "n": len(close_gap),
                "abs_p50_bps": q(close_gap, 0.5), "abs_p95_bps": q(close_gap, 0.95)}
    fb, fd = funding_binance(), funding_deribit()
    ev_b, ev_d = rsi_events(b), rsi_events(d)
    res = {"card": "venue-gap-tight-stop-rerun-on-deribit", "month": MONTH,
           "bars_binance": len(b), "bars_deribit": len(d), "gap_used": gap_used,
           "funding_month_pct": {"binance": sum(r for t, r in fb if T0 < t <= T1) * 100,
                                 "deribit": sum(r for t, r in fd if T0 < t <= T1) * 100},
           "events": {"binance": len(ev_b), "deribit": len(ev_d)},
           "variants": []}
    for v in VARIANTS:
        sb = summary(run_layer(b, fb, ev_b, v["stop_pct"], v["wick_touch"]))
        sd = summary(run_layer(d, fd, ev_d, v["stop_pct"], v["wick_touch"]))
        row = {"name": v["name"], "stop_pct": v["stop_pct"], "wick_touch": v["wick_touch"],
               "binance": sb, "deribit": sd,
               "delta_mean_r_deribit_minus_binance": (None if sb["mean_r"] is None or sd["mean_r"] is None
                                                     else sd["mean_r"] - sb["mean_r"])}
        res["variants"].append(row)
        print(f"{row['name']:16s} binance n={sb['n']:3d} netR={sb['net_r_sum']:+7.3f} meanR={sb['mean_r']:+.4f} | "
              f"deribit n={sd['n']:3d} netR={sd['net_r_sum']:+7.3f} meanR={sd['mean_r']:+.4f} | "
              f"d-b meanR={row['delta_mean_r_deribit_minus_binance']:+.4f}")
    RESULT_OUT.parent.mkdir(parents=True, exist_ok=True)
    RESULT_OUT.write_text(json.dumps(res, indent=1), encoding="utf-8", newline="\n")
    print(f"gap used: close D-B abs p50={gap_used['abs_p50_bps']:.2f} bps p95={gap_used['abs_p95_bps']:.2f} bps "
          f"on {gap_used['n']} common 1m bars")
    print(f"wrote {RESULT_OUT}")


if __name__ == "__main__":
    main()
