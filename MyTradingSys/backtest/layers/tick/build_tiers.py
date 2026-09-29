"""
MyTradingSys/backtest/layers/tick/build_tiers.py - T040 Q6: compute the tier table (tiers.json) per the tick layer spec.

Offline tool; does not touch execution/ or the live runner. Sources:
  * price/net_delta/cvd_change/volume tiers, 1/2/3/5/10/15m: ALL-TIME 1m klines (2022-01..now). net_delta = 2*tbv - v is
    EXACT aggressor delta (taker-buy volume is the aggressor sum), so it is identical to the aggTrades 1m delta; this is
    cross-checked bar by bar against the aggTrades order-flow bars (F:\\MTS\\data\\orderflow_1m) in tiers_meta.json.
  * oi_delta tiers 5/10/15m from the 5m OI metrics (Dumps/backtest/raw/metrics, 2025-09..now).
  * tiers_aggtrades_window.json: same table built only from the aggTrades window (shows the window is not all-time).
Output shape = tick_flagger.replay tiers_table: {tf: {indicator: {"high": [...], "low": [...]}}} (no metadata keys;
metadata goes in tiers_meta.json). Flags are CONTEXT ONLY (never gate Tom).
"""
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

REPO = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(REPO))

from MyTradingSys.backtest.bt.bt_data import load_klines, load_metrics
from MyTradingSys.backtest.layers.fabio.orderflow_bars import load_days
from MyTradingSys.backtest.layers.tick import tick_extremes as TE
from MyTradingSys.backtest.layers.tick import tick_flagger as TF
from MyTradingSys.backtest.layers.tick import tick_oi_extremes as TO

HERE = Path(__file__).resolve().parent
OF_DIR = r"F:\MTS\data\orderflow_1m"
INDICATORS = ("net_delta", "cvd_change", "volume", "price_change_pct")


def klines_all():
    a = load_klines(REPO / "Dumps" / "backtest" / "raw_1m_2022")
    b = load_klines(REPO / "Dumps" / "backtest" / "raw")
    last = a[-1]["t"] if a else 0
    a += [x for x in b if x["t"] > last]
    a.sort(key=lambda x: x["t"])
    return a


def of_as_klines(days):
    return [{"t": d["t"], "o": d["o"], "h": d["h"], "l": d["l"], "c": d["c"], "v": d["buy_vol"] + d["sell_vol"],
             "tbv": d["buy_vol"]} for d in days]


def flag_rate(bars_1m, table, tfs=(1, 2, 3, 5, 10, 15)):
    """Replay the flagger over bars_1m (1m klines-shaped) -> flags per day by (tf, indicator, side, tier)."""
    hist = []
    for tf in tfs:
        for b in TE.resample(bars_1m, tf):
            for ind in INDICATORS:
                hist.append({"t": b["t"], "tf": str(tf), "indicator": ind, "value": b[ind]})
    hist.sort(key=lambda x: x["t"])
    flags = TF.replay(hist, table)
    n_days = (bars_1m[-1]["t"] - bars_1m[0]["t"]) / 86400000
    by = {}
    for f in flags:
        k = f"{f['tf']}m {f['indicator']} {f['side']} T{f['tier']}"
        by[k] = by.get(k, 0) + 1
    return {"days": round(n_days, 1), "flags": len(flags), "per_day": round(len(flags) / n_days, 2), "by": by}


def main():
    kl = klines_all()
    print("klines", len(kl), kl[0]["t"], kl[-1]["t"], flush=True)
    table = TE.build_tier_table(kl, timeframes=[1, 2, 3, 5, 10, 15], indicators=list(INDICATORS), top_n=20)
    oi = TO.build_oi_tier_table(load_metrics(REPO / "Dumps" / "backtest" / "raw"), timeframes=[5, 10, 15], top_n=20)
    for tf, t in oi.items():
        table.setdefault(tf, {})["oi_delta"] = t

    days = load_days(OF_DIR)
    of_bars = of_as_klines([d for d in days if d["thr_days"] >= 30])
    kl_by_t = {b["t"]: b for b in kl}
    n_cmp = n_missing = 0
    max_diff = 0.0
    for b in of_bars:
        k = kl_by_t.get(b["t"])
        if k is None:
            n_missing += 1
            continue
        n_cmp += 1
        max_diff = max(max_diff, abs((2 * b["tbv"] - b["v"]) - (2 * k["tbv"] - k["v"])))
    window_table = TE.build_tier_table(of_bars, timeframes=[1, 2, 3, 5, 10, 15], indicators=list(INDICATORS), top_n=20)

    (HERE / "tiers.json").write_text(json.dumps(table, indent=1), encoding="utf-8", newline="\n")
    (HERE / "tiers_aggtrades_window.json").write_text(json.dumps(window_table, indent=1), encoding="utf-8", newline="\n")
    meta = {"built_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "kline_bars": len(kl), "kline_first": kl[0]["t"], "kline_last": kl[-1]["t"],
            "aggtrades_bars": len(of_bars), "aggtrades_first": of_bars[0]["t"], "aggtrades_last": of_bars[-1]["t"],
            "delta_crosscheck": {"bars_compared": n_cmp, "missing_in_klines": n_missing,
                                 "max_abs_delta_diff_btc": max_diff},
            "flag_rate_alltime_tiers_on_aggtrades_window": flag_rate(of_bars, table),
            "top_n": 20, "gap_factor": 1.5}
    (HERE / "tiers_meta.json").write_text(json.dumps(meta, indent=1), encoding="utf-8", newline="\n")
    print(json.dumps(meta, indent=1)[:3000])


if __name__ == "__main__":
    main()
