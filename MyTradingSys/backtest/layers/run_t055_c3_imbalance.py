"""
C3b: quarter-hour opening order-imbalance (Kim & Hansen, arXiv 2607.09426) on BTCUSDT 1m klines.
Proxy: taker-buy-volume imbalance = (2*tbv - v)/v over the opening window of each quarter hour
(1 or 5 one-minute bars starting at minute-of-quarter 0). Entry = close of the last window bar;
direction = sign(imbalance) (momentum) or opposite (contrarian) - the abstract gives no sign, so
both are grid variants chosen on IS only. Non-overlapping trades (flat before next entry).
Costs/verdict/PBO reuse run_t055.py. Alert-only research; never a Tom filter.
"""
import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO))
from MyTradingSys.backtest.layers import run_t055 as R
from MyTradingSys.backtest.layers.turn_of_candle.turn_of_candle import minute_of_quarter

BAR_MS = 60000
HORIZONS = (1, 2, 5, 240, 480, 720)


def imbalance_events(bars, window=1, min_abs=0.0, direction="mom"):
    ev = []
    n = len(bars)
    for i in range(n - window + 1):
        if minute_of_quarter(bars[i]["t"]) != 0:
            continue
        w = bars[i:i + window]
        if w[-1]["t"] - w[0]["t"] != (window - 1) * BAR_MS:
            continue
        v = sum(b["v"] for b in w)
        if v <= 0:
            continue
        imb = (2 * sum(b["tbv"] for b in w) - v) / v
        if abs(imb) < min_abs or imb == 0:
            continue
        s = 1 if imb > 0 else -1
        if direction == "contra":
            s = -s
        ev.append({"i": i + window - 1, "side": "long" if s > 0 else "short"})
    return ev


def nonoverlap(ev, bars, h):
    out, free = [], -1
    for e in ev:
        i = e["i"]
        if i < free or i + h >= len(bars) or bars[i + h]["t"] - bars[i]["t"] != h * BAR_MS:
            continue
        out.append(e)
        free = i + h
    return out


def run(bars, funding):
    net_return = R._cost_fn()
    n_is = int(len(bars) * 0.7)
    bis, boos = bars[:n_is], bars[n_is:]
    grid = [{"window": w, "min_abs": m, "direction": d} for w in (1, 5) for m in (0.0, 0.1) for d in ("mom", "contra")]
    variants, cols = [], []
    for p in grid:
        ev = imbalance_events(bis, **p)
        for h in HORIZONS:
            tr = R.score_trades(nonoverlap(ev, bis, h), bis, h, BAR_MS, funding, net_return)
            st = R.summarize(tr)
            variants.append({"params": p, "h": h, "st": st})
            cols.append(R.daily_matrix_column(tr, bis))
    pbo = R.compute_pbo(cols, 16)
    res = {"pbo": pbo, "n_bars": len(bars), "n_is": n_is, "grid": variants}
    per_h = {}
    for h in HORIZONS:
        vs = [v for v in variants if v["h"] == h and v["st"]["n"] >= 20 and v["st"]["mean_net"] is not None]
        if not vs:
            continue
        best = max(vs, key=lambda v: v["st"]["mean_net"])
        tr = R.score_trades(nonoverlap(imbalance_events(boos, **best["params"]), boos, h), boos, h, BAR_MS, funding, net_return)
        o = R.summarize(tr)
        yrs = R.yearly_net(tr)
        per_h[h] = {"params": best["params"], "is": best["st"], "oos": o, "years": yrs}
    res["per_h"] = per_h
    return res


def main():
    bars, funding = R.load_data("c3", str(REPO / "Dumps/backtest/raw_1m_2022"), str(REPO / "Dumps/backtest/raw"), "1m")
    res = run(bars, funding)
    # per-horizon PBO: columns limited to that horizon
    out = REPO / "Dumps/backtest/runs/t055_c3_imb"
    out.mkdir(parents=True, exist_ok=True)
    with open(out / "result.json", "w", newline="\n") as f:
        json.dump(res, f, indent=1, default=str)
    print("bars", res["n_bars"], "IS", res["n_is"], "pooled PBO", res["pbo"])
    for h, r in res["per_h"].items():
        o, i = r["oos"], r["is"]
        pos = sum(1 for y in r["years"].values() if y["mean_net"] > 0)
        print(h, json.dumps(r["params"]), "IS n", i["n"], "net", round(i["mean_net"] * 100, 4), "| OOS n", o["n"],
              "gross", None if o["mean_gross"] is None else round(o["mean_gross"] * 100, 4),
              "net", None if o["mean_net"] is None else round(o["mean_net"] * 100, 4),
              "sh", o["sharpe_net"], "posyears", pos, {y: (v["n"], round(v["mean_net"] * 100, 3)) for y, v in r["years"].items()})


if __name__ == "__main__":
    main()
