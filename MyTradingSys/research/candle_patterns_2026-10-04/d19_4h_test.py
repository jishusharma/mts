import sys
sys.dont_write_bytecode = True
import csv, math, bisect
from pathlib import Path
REPO = Path(r"C:\Users\E-ngineers\IdeaProjects\BinanceDataFeed")
BT = REPO / "Dumps" / "backtest"
def load_csv(path):
    bars = []
    with open(path, newline="") as f:
        for row in csv.reader(f):
            if not row or not row[0].isdigit():
                continue
            bars.append({"t": int(row[0]), "o": float(row[1]), "h": float(row[2]), "l": float(row[3]), "c": float(row[4])})
    return bars
def load_1m(start_ms, end_ms):
    seen = {}
    for d in [BT / "raw_1m_2022" / "klines", BT / "raw" / "klines"]:
        for p in sorted(d.glob("BTCUSDT-1m-*.csv")):
            for b in load_csv(p):
                if start_ms <= b["t"] < end_ms:
                    seen[b["t"]] = b
    return [seen[k] for k in sorted(seen)]
def resample_4h(bars):
    out, cur, cur_start = [], [], None
    tf = 4 * 3600000
    for b in bars:
        s = (b["t"] // tf) * tf
        if s != cur_start:
            if cur:
                out.append({"t": cur_start, "o": cur[0]["o"], "h": max(x["h"] for x in cur), "l": min(x["l"] for x in cur), "c": cur[-1]["c"]})
            cur, cur_start = [], s
        cur.append(b)
    if cur:
        out.append({"t": cur_start, "o": cur[0]["o"], "h": max(x["h"] for x in cur), "l": min(x["l"] for x in cur), "c": cur[-1]["c"]})
    return out
def load_daily():
    bars = []
    d = BT / "raw_1d" / "klines"
    for p in sorted(d.glob("BTCUSDT-1d-*.csv")):
        bars.extend(load_csv(p))
    bars.sort(key=lambda x: x["t"])
    return bars
def sma(bars, idx, n, key="c"):
    if idx + 1 < n:
        return None
    return sum(b[key] for b in bars[idx - n + 1:idx + 1]) / n
def sma_at_daily(daily_bars, ts, n):
    lo = 0
    for i, b in enumerate(daily_bars):
        if b["t"] <= ts:
            lo = i
        else:
            break
    if lo + 1 < n:
        return None
    return sum(b["c"] for b in daily_bars[lo - n + 1:lo + 1]) / n
def bull_engulf(bars, i):
    if i < 1:
        return False
    p, x = bars[i-1], bars[i]
    return p["c"] < p["o"] and x["c"] > x["o"] and x["o"] <= p["c"] and x["c"] >= p["o"] and abs(x["c"]-x["o"]) > abs(p["c"]-p["o"])
def bear_engulf(bars, i):
    if i < 1:
        return False
    p, x = bars[i-1], bars[i]
    return p["c"] > p["o"] and x["c"] < x["o"] and x["o"] >= p["c"] and x["c"] <= p["o"] and abs(x["c"]-x["o"]) > abs(p["c"]-p["o"])
def bull_kicker(bars, i):
    if i < 1:
        return False
    p, x = bars[i-1], bars[i]
    return p["c"] < p["o"] and x["c"] > x["o"] and x["o"] > p["o"] and x["c"] > p["o"]
def bear_kicker(bars, i):
    if i < 1:
        return False
    p, x = bars[i-1], bars[i]
    return p["c"] > p["o"] and x["c"] < x["o"] and x["o"] < p["o"] and x["c"] < p["o"]
def near_level(price, level, tol):
    return level is not None and abs(price - level) <= tol
def run(bars4h, daily, fee_side):
    SUP_N = 20
    trades = []
    in_pos = False
    entry = None
    entry_i = None
    for i in range(SUP_N, len(bars4h)):
        x = bars4h[i]
        sup = min(b["l"] for b in bars4h[i-SUP_N:i])
        sma200 = sma_at_daily(daily, x["t"], 200)
        touched = (x["l"] <= sup) or (sma200 is not None and x["l"] <= sma200)
        sig = (bull_engulf(bars4h, i) or bull_kicker(bars4h, i)) and touched
        if not in_pos and sig and i + 1 < len(bars4h):
            entry = bars4h[i+1]["o"]
            entry_i = i + 1
            in_pos = True
        elif in_pos and (bear_engulf(bars4h, i) or bear_kicker(bars4h, i)) and i + 1 < len(bars4h):
            exit_px = bars4h[i+1]["o"]
            ret = (exit_px - entry) / entry - 2 * fee_side
            trades.append(ret)
            in_pos = False
    if in_pos and entry is not None:
        exit_px = bars4h[-1]["c"]
        ret = (exit_px - entry) / entry - 2 * fee_side
        trades.append(ret)
    return trades
def metrics(trades, bh):
    n = len(trades)
    if n == 0:
        return {"n": 0, "win": 0.0, "pf": 0.0, "net_r": 0.0, "bh": bh}
    wins = [t for t in trades if t > 0]
    losses = [t for t in trades if t <= 0]
    wr = len(wins) / n
    gp = sum(wins)
    gl = -sum(losses)
    pf = (gp / gl) if gl > 0 else float("inf")
    net_r = sum(trades)
    return {"n": n, "win": wr, "pf": pf, "net_r": net_r, "bh": bh}
def main():
    start_ms = 1640995200000
    end_ms = 1759449600000
    bars1m = load_1m(start_ms, end_ms)
    print("1m bars:", len(bars1m))
    bars4h = resample_4h(bars1m)
    print("4h bars:", len(bars4h))
    daily = load_daily()
    print("daily bars:", len(daily))
    bh = (bars4h[-1]["c"] - bars4h[0]["o"]) / bars4h[0]["o"]
    out = []
    for fee_side, label in [(0.00025, "0.05pct_roundtrip"), (0.00050, "0.10pct_roundtrip")]:
        tr = run(bars4h, daily, fee_side)
        m = metrics(tr, bh)
        out.append((label, m))
        print(label, m)
    rp = REPO / "MyTradingSys" / "research" / "candle_patterns_2026-10-04"
    lines = []
    lines.append("# D19 - 4h long-only bullish engulfing / kicker at support or 200d SMA")
    lines.append("")
    lines.append("NO-SOURCE research. Never a live layer. Data window 2022-01-01 to 2026-10-02 (1m available range).")
    lines.append("Task asked 2018-2026; 1m klines start 2022-01, so the window is the available one.")
    lines.append("")
    lines.append("| Fee side | n | win rate | PF | net R | buy-and-hold |")
    lines.append("|---|---|---|---|---|---|")
    for label, m in out:
        lines.append("| %s | %d | %.3f | %.3f | %.4f | %.4f |" % (label, m["n"], m["win"], m["pf"], m["net_r"], m["bh"]))
    (rp / "D19_4H_RESULTS.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("wrote D19_4H_RESULTS.md")
if __name__ == "__main__":
    main()