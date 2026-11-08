"""malkan-level-short-4h-count-1109: count every firing of the Malkan level-short stack on BTCUSDT 4h 2017-2026.
Data: Binance spot klines from data-api.binance.vision (closed bars only), fetched 2026-11-08 to F:/MTS/data/binance_api_spot.
Usage: python MyTradingSys/research/malkan_level_shorts_2026-11-09/count.py [data_dir]  -> writes COUNT.json next to this file.
"""
import csv
import datetime as dt
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
from MyTradingSys.backtest.layers.rsi import malkan_level_short as M  # noqa: E402

DATA = Path(sys.argv[1] if len(sys.argv) > 1 else "F:/MTS/data/binance_api_spot")


def load(iv):
    with open(DATA / f"BTCUSDT_{iv}.csv", newline="") as f:
        return [{"t": int(x["t"]), "o": float(x["o"]), "h": float(x["h"]), "l": float(x["l"]), "c": float(x["c"])}
                for x in csv.DictReader(f)]


def regime_fn(b1d):
    """bull/bear = last closed daily close above/below its 200-day SMA at the trigger close."""
    closes, rows = [], []
    for x in b1d:
        closes.append(x["c"])
        sma = sum(closes[-200:]) / 200 if len(closes) >= 200 else None
        rows.append((x["t"] + 86400000, x["c"], sma))

    def at(t_close):
        last = None
        for r in rows:
            if r[0] > t_close:
                break
            last = r
        if not last or last[2] is None:
            return "warmup"
        return "bull" if last[1] > last[2] else "bear"
    return at


def summarise(rows):
    n = len(rows)
    if not n:
        return {"n": 0}
    net = [r["net_r"] for r in rows]
    return {"n": n, "hit_1r": round(sum(r["hit_1r"] for r in rows) / n, 3),
            "win_2r": round(sum(r["exit"] == "target" for r in rows) / n, 3),
            "gross_r": round(sum(r["gross_r"] for r in rows) / n, 3),
            "net_r": round(sum(net) / n, 3), "total_net_r": round(sum(net), 1),
            "median_risk_pct": round(sorted(r["risk_pct"] for r in rows)[n // 2], 2)}


ARMS = {
    "base level+trigger": dict(layers=M.BASE),
    "+structure either": dict(layers=M.BASE | {"structure"}),
    "+structure div 3-10 close": dict(layers=M.BASE | {"structure"}, structure="div"),
    "+structure div 5-50 close": dict(layers=M.BASE | {"structure"}, structure="div", div_window=(5, 50)),
    "+structure div 5-50 wick": dict(layers=M.BASE | {"structure"}, structure="div", div_window=(5, 50), price_mode="wick"),
    "+structure sweep": dict(layers=M.BASE | {"structure"}, structure="sweep"),
    "+wavetrend": dict(layers=M.BASE | {"wavetrend"}),
    "+htf": dict(layers=M.BASE | {"htf"}),
    "FULL (5 layers)": dict(layers=M.FULL),
    "FULL div 5-50 wick": dict(layers=M.FULL, structure="div", div_window=(5, 50), price_mode="wick"),
}


def main():
    b4, b1d, b1w = load("4h"), load("1d"), load("1w")
    reg = regime_fn(b1d)
    out = {"bars_4h": len(b4), "from": b4[0]["t"], "to": b4[-1]["t"], "fee_per_side": M.FEE, "target_r": M.TARGET_R,
           "max_bars": M.MAX_BARS, "arms": {}}
    for name, kw in ARMS.items():
        rows = []
        for s in M.signals(b4, b1d, b1w, **kw):
            o = M.outcome(b4, s["j"], s["entry"], s["stop"])
            tc = b4[s["i"]]["t"] + 4 * 3600 * 1000
            o.update(year=dt.datetime.fromtimestamp(s["t_trigger"] / 1000, dt.timezone.utc).year, regime=reg(tc),
                     risk_pct=100 * (s["stop"] - s["entry"]) / s["entry"], t=s["t_trigger"])
            rows.append(o)
        arm = {"all": summarise(rows)}
        for key in ("regime", "year"):
            for v in sorted({r[key] for r in rows}, key=str):
                arm[f"{key}={v}"] = summarise([r for r in rows if r[key] == v])
        out["arms"][name] = arm
        a = arm["all"]
        print(f"{name:28s} n={a.get('n')} hit1R={a.get('hit_1r')} win2R={a.get('win_2r')} gross={a.get('gross_r')} net={a.get('net_r')}")
    (Path(__file__).parent / "COUNT.json").write_text(json.dumps(out, indent=1), encoding="utf-8")


if __name__ == "__main__":
    main()
