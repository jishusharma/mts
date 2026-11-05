"""Critical test wave 2 item 6: Binance USD-M BTCUSDT perp vs Deribit BTC-PERPETUAL on one DEV month.

Gap table per field (1m open/high/low/close, wick extremes, funding) and one layer stand-in
(rsi_levels: 1h RSI(14) touch, entry at the next 1m bar open = one-bar fill delay) run through
bt_engine.simulate_trade on both venues with each venue's own funding and Deribit fees (orders go to Deribit).
Public market data only. DEV window only: the loader refuses bars at or after 2024-07-01.
Run: python MyTradingSys/research/critical_test_wave2_2026-10-30/item6_venue_gap.py
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

MONTH = "2024-05"                 # OURS: one DEV month, the last full month with both venues cached
T0 = 1714521600000                # 2024-05-01T00:00Z
T1 = 1717200000000                # 2024-06-01T00:00Z
DEV_END = 1719792000000           # 2024-07-01T00:00Z (backtest/splits.py)
BIN_DIR = Path("F:/MTS/data/tom_raw/klines")
DER_CACHE = Path("F:/MTS/data/deribit") / f"BTC-PERPETUAL-1m-{MONTH}.csv"
FUND_ROOT = Path("F:/MTS/Dumps/backtest/raw")
OUT = Path(__file__).resolve().parent
RSI_N, RSI_LO, RSI_HI = 14, 30.0, 70.0   # OURS (common default, not a trader's number)
STOP_FRAC, TARGET_R, MAX_BARS = 0.01, 2.0, 960   # OURS


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
    if not DER_CACHE.exists():
        DER_CACHE.parent.mkdir(parents=True, exist_ok=True)
        rows = []
        for s in range(T0, T1, 86400000):
            e = s + 86400000 - 60000
            d = get("https://www.deribit.com/api/v2/public/get_tradingview_chart_data?instrument_name=BTC-PERPETUAL"
                    f"&start_timestamp={s}&end_timestamp={e}&resolution=1")["result"]
            rows += zip(d["ticks"], d["open"], d["high"], d["low"], d["close"])
            time.sleep(0.2)
        with open(DER_CACHE, "w", newline="\n") as f:
            w = csv.writer(f, lineterminator="\n")
            w.writerow(["t", "o", "h", "l", "c"])
            w.writerows(sorted(set(rows)))
    bars = {}
    with open(DER_CACHE, newline="") as f:
        for row in csv.DictReader(f):
            t = int(row["t"])
            refuse_after_dev(t)
            if T0 <= t < T1:
                bars[t] = {"t": t, "o": float(row["o"]), "h": float(row["h"]), "l": float(row["l"]), "c": float(row["c"])}
    return bars


def funding_binance():
    """Binance USD-M archive (data.binance.vision fundingRate monthly files; fapi is unreachable from this host)."""
    import bt_data
    return [r for r in bt_data.load_funding(FUND_ROOT) if T0 - 86400000 <= r[0] < min(T1 + 86400000, DEV_END)]


def funding_deribit():
    out = []
    for s in range(T0 - 86400000, T1 + 86400000, 10 * 86400000):
        e = min(s + 10 * 86400000, T1 + 86400000)
        out += [(int(x["timestamp"]), float(x["interest_1h"]))
                for x in get("https://www.deribit.com/api/v2/public/get_funding_rate_history?instrument_name=BTC-PERPETUAL"
                             f"&start_timestamp={s}&end_timestamp={e}")["result"]]
    return sorted(set(out))


def q(xs, p):
    xs = sorted(xs)
    return xs[min(len(xs) - 1, int(p * len(xs)))]


def gap_row(name, xs):
    a = [abs(x) for x in xs]
    return {"field": name, "n": len(xs), "mean_bps": statistics.fmean(xs), "abs_p50": q(a, 0.5),
            "abs_p95": q(a, 0.95), "abs_p99": q(a, 0.99), "abs_max": max(a)}


def rsi_events(bars):
    """1h closes from 1m bars; event at 1h close when RSI crosses into <30 (long) or >70 (short)."""
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


def run_layer(bars, funding, events):
    seq = [bars[t] for t in sorted(bars)]
    out = []
    for t_sig, side in events:
        nxt = bars.get(t_sig + 60000)          # one-bar fill delay: open of the next 1m bar
        if nxt is None:
            continue
        px = nxt["o"]
        sgn = 1 if side == "long" else -1
        stop = px * (1 - sgn * STOP_FRAC)
        tgt = px * (1 + sgn * STOP_FRAC * TARGET_R)
        r = bt_engine.simulate_trade(side, px, nxt["t"] - 1, stop, [(tgt, 1.0)], [b for b in seq if b["t"] >= nxt["t"]],
                                     funding=funding, taker_fee=fees.DERIBIT_TAKER, maker_fee=fees.DERIBIT_MAKER,
                                     max_bars=MAX_BARS)
        out.append({"t_sig": t_sig, "side": side, "entry": px, "net_r": r["net_r"], "exit": r["exit_reason"],
                    "funding_pct": r["funding_paid_pct"]})
    return out


def main():
    b, d = load_binance(), load_deribit()
    common = sorted(set(b) & set(d))
    bps = lambda x, y: (x - y) / y * 1e4  # noqa: E731  Deribit minus Binance, in bps of Binance
    rows = [gap_row(f, [bps(d[t][k], b[t][k]) for t in common]) for f, k in
            (("open", "o"), ("high", "h"), ("low", "l"), ("close", "c"))]
    rng_b = [b[t]["h"] - b[t]["l"] for t in common]
    rng_d = [d[t]["h"] - d[t]["l"] for t in common]
    rows.append(gap_row("range (USD, D-B)", [y - x for x, y in zip(rng_b, rng_d)]))
    wick5 = sum(1 for t in common if abs(bps(d[t]["h"], b[t]["h"])) > 5 or abs(bps(d[t]["l"], b[t]["l"])) > 5)
    rb = [bps(b[t]["c"], b[t]["o"]) for t in common]
    rd = [bps(d[t]["c"], d[t]["o"]) for t in common]
    corr = statistics.correlation(rb, rd)
    sign_flip = sum(1 for x, y in zip(rb, rd) if x * y < 0)
    fb, fd = funding_binance(), funding_deribit()
    fb_m = sum(r for t, r in fb if T0 < t <= T1)
    fd_m = sum(r for t, r in fd if T0 < t <= T1)
    ev_b, ev_d = rsi_events(b), rsi_events(d)
    tr_b, tr_d = run_layer(b, fb, ev_b), run_layer(d, fd, ev_d)
    same = {(x["t_sig"], x["side"]) for x in tr_b} & {(x["t_sig"], x["side"]) for x in tr_d}
    paired = [(x, y) for x in tr_b for y in tr_d if (x["t_sig"], x["side"]) == (y["t_sig"], y["side"])]
    dif = [y["net_r"] - x["net_r"] for x, y in paired if x["net_r"] is not None and y["net_r"] is not None]
    nr = lambda tr: [x["net_r"] for x in tr if x["net_r"] is not None]  # noqa: E731
    res = {"month": MONTH, "bars_binance": len(b), "bars_deribit": len(d), "bars_common": len(common),
           "gap_rows": rows, "wick_gt5bps_share": wick5 / len(common), "ret_corr_1m": corr,
           "ret_sign_flip_share": sign_flip / len(common),
           "funding_month_binance_pct": fb_m * 100, "funding_month_deribit_pct": fd_m * 100,
           "funding_n_binance": sum(1 for t, _ in fb if T0 < t <= T1), "funding_n_deribit": sum(1 for t, _ in fd if T0 < t <= T1),
           "layer": {"events_binance": len(ev_b), "events_deribit": len(ev_d), "events_both": len(same),
                     "trades_binance": len(nr(tr_b)), "net_r_sum_binance": sum(nr(tr_b)),
                     "trades_deribit": len(nr(tr_d)), "net_r_sum_deribit": sum(nr(tr_d)),
                     "paired": len(dif), "paired_mean_diff_r": statistics.fmean(dif) if dif else None,
                     "paired_max_abs_diff_r": max(map(abs, dif)) if dif else None,
                     "trades_b": tr_b, "trades_d": tr_d}}
    (OUT / "item6_result.json").write_text(json.dumps(res, indent=1), encoding="utf-8", newline="\n")
    print(json.dumps({k: v for k, v in res.items() if k != "layer"}, indent=1))
    print(json.dumps({k: v for k, v in res["layer"].items() if not k.startswith("trades_")}, indent=1))


if __name__ == "__main__":
    main()
