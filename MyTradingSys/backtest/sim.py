import sys
sys.dont_write_bytecode = True
"""Trade simulation over Dumps/backtest/replay_rows.json.

Entry rules:
  A = enter on the first SETUP_FORMING snapshot while flat
  B = enter on the second consecutive SETUP_FORMING (same setup, same dir),
      mirroring the live loop's 2-cycle verdict persistence (B025)
One position at a time. Stop/target = rank-1 candidate's math.stop/target.
Price path = snapshot current_price at ~60 s spacing (Binance BTCUSDT).
A gap > 180 s ends the trade as censored_gap (machine was off).
Censored trades are counted in the outcomes line but EXCLUDED from the
resolved-R lines. On 2026-09-26, resolving the 18 censored rule-A trades
against the archived 5m/15m/1h klines (stop first if both hit in one bar)
gave 15 stop, 1 target, 2 unresolved - including them makes results worse.

Known limits (T051): 60 s sampling misses intra-minute wicks; signals and
fills are both on Binance prices, not Deribit; fee model is Deribit's
published BTC-PERPETUAL schedule (maker 0, taker 0.05%, verified
2026-09-26 via public/get_instrument) - market entry, maker target,
taker stop.

Run: python MyTradingSys/backtest/sim.py [--stops observed|ideal]
"""
import json, math, statistics as st, argparse
from collections import Counter, defaultdict
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from snapshots import OUT_DIR  # noqa: E402

GAP, TIMEOUT = 180, 12 * 3600


def wilson(k, n, z=1.96):
    if n < 0 or k < 0 or k > n:
        raise ValueError("wilson needs 0 <= k <= n, got k=%d n=%d" % (k, n))
    if n == 0:
        return (0.0, 0.0)
    p = k / n; d = 1 + z * z / n; c = p + z * z / (2 * n)
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n))
    return ((c - h) / d, (c + h) / d)


def geom_ok(d, e, s, t):
    return (d == "long" and s < e < t) or (d == "short" and t < e < s)


def run(rows, rule, stops, taker, maker):
    for a, b in zip(rows, rows[1:]):
        if b["t"] < a["t"]:
            raise ValueError("rows out of order: t=%s follows t=%s" % (b["t"], a["t"]))
    trades, i, n = [], 0, len(rows)
    while i < n:
        r = rows[i]
        ok = r["verdict"] == "SETUP_FORMING" and r["stop"] and r["target"]
        if ok and rule == "B":
            p = rows[i - 1] if i > 0 else None
            ok = (p is not None and p["verdict"] == "SETUP_FORMING" and p["setup"] == r["setup"]
                  and p["dir"] == r["dir"] and r["t"] - p["t"] <= GAP)
        if not ok:
            i += 1; continue
        d, e, s, t = r["dir"], r["price"], float(r["stop"]), float(r["target"])
        if not geom_ok(d, e, s, t):
            i += 1; continue
        risk, res, j, last = abs(e - s), None, i + 1, r
        while j < n:
            q = rows[j]
            if q["t"] - last["t"] > GAP:
                res = ("censored_gap", last["price"]); break
            if q["t"] - r["t"] > TIMEOUT:
                res = ("timeout", q["price"]); break
            px = q["price"]
            if (d == "long" and px <= s) or (d == "short" and px >= s):
                res = ("stop", s if stops == "ideal" else px); break
            if (d == "long" and px >= t) or (d == "short" and px <= t):
                res = ("target", t); break
            last = q; j += 1
        if res is None:
            res = ("censored_end", last["price"]); j = n - 1
        kind, x = res
        gross = ((x - e) if d == "long" else (e - x)) / risk
        fee_pct = taker + (maker if kind == "target" else taker)
        fee_R = fee_pct * e / risk
        trades.append(dict(ts=r["ts"], setup=r["setup"], dir=d, kind=kind, gross=gross,
                           net=gross - fee_R, fee_R=fee_R, risk_pct=100 * risk / e))
        i = j + 1
    return trades


def report(trades, label):
    print("\n=== %s ===" % label)
    print("trades:", len(trades), "| outcomes:", dict(Counter(x["kind"] for x in trades)))
    res = [x for x in trades if x["kind"] in ("stop", "target")]
    if not res:
        return
    w = sum(1 for x in res if x["kind"] == "target")
    lo, hi = wilson(w, len(res))
    wins = [x["gross"] for x in res if x["kind"] == "target"]
    aw = st.mean(wins) if wins else 0.0
    print("resolved %d | win rate %.0f%% (95%% CI %.0f-%.0f%%) | breakeven before fees %.0f%%" % (
        len(res), 100.0 * w / len(res), 100 * lo, 100 * hi, 100.0 / (1 + aw) if aw else float("nan")))
    print("sum gross R %.2f | avg fee %.2f R | avg net R %.2f | sum net R %.2f" % (
        sum(x["gross"] for x in res), st.mean(x["fee_R"] for x in res),
        st.mean(x["net"] for x in res), sum(x["net"] for x in res)))
    print("stop distance %% of price: median %.3f" % st.median(x["risk_pct"] for x in trades))
    by = defaultdict(list)
    for x in trades:
        by[x["setup"]].append(x)
    for k, L in sorted(by.items(), key=lambda kv: -len(kv[1])):
        print("  %-12s n=%2d %s sum net R %.2f" % (k, len(L), dict(Counter(y["kind"] for y in L)), sum(y["net"] for y in L)))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--stops", choices=["observed", "ideal"], default="observed")
    from MyTradingSys.backtest.fees import DERIBIT_TAKER, DERIBIT_MAKER
    ap.add_argument("--taker", type=float, default=DERIBIT_TAKER)
    ap.add_argument("--maker", type=float, default=DERIBIT_MAKER)
    a = ap.parse_args()
    rows = json.load(open(OUT_DIR / "replay_rows.json", encoding="utf-8"))
    for rule in ("A", "B"):
        report(run(rows, rule, a.stops, a.taker, a.maker),
               "rule %s, stops=%s, taker=%.4f maker=%.4f" % (rule, a.stops, a.taker, a.maker))


if __name__ == "__main__":
    main()
