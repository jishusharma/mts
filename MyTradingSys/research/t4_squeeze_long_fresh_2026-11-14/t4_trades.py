"""T4 step A: read the wave cache, write the trade lists. Prints counts only; NO pooled statistic is computed here.

Outputs (in this folder):
  trades.csv          fresh coins, non-bear gate (UP_E UP_L MIX_E MIX_L), RIDE and T3R rows (column kind)
  trades_control.csv  fresh coins, DOWN_E / DOWN_L gate (control row, descriptive)
  trades_old20.csv    the miner's 20 coins, non-bear gate, same code and rules (descriptive)
  coverage.json       per-coin bar counts, funding span, onset and trade counts, dropped coins with the reason
Usage: python t4_trades.py [--wave DIR] [--miner DIR] [--brain CSV] [--out DIR]
"""
import argparse
import json
import os
import sys
import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import t4_core as C  # noqa: E402

WAVE = r"F:\MTS\data_cache\binance\wave2-1114"
MINER = r"F:\MTS\data_cache\binance\combo-edge-miner-1114"
BRAIN = r"F:\MTS\data_cache\mts_brains\phase_daily.csv"


def load_brain(path):
    if not os.path.isfile(path):
        return None
    d = pd.read_csv(path, usecols=["date", "label", "cycle"]).fillna("")
    return {r.date: (r.label, r.cycle) for r in d.itertuples()}


def coin_inputs(sym, root):
    """(4h bars, 1d bars, funding) or (None, None, None, reason)."""
    p4 = os.path.join(root, "spot_4h", f"{sym}USDT.csv")
    p1 = os.path.join(root, "spot_1d", f"{sym}USDT.csv")
    pf = os.path.join(root, "funding", f"{sym}USDT.csv")
    if not os.path.isfile(p4):
        return None, "no 4h spot file"
    if not os.path.isfile(p1):
        return None, "no 1d spot file"
    if not os.path.isfile(pf):
        return None, "no funding file"
    D4, d1, fund = C.load_bars(p4, "4h"), C.load_bars(p1, "1d"), C.load_funding(pf)
    if len(D4["c"]) < 400:
        return None, f"too short ({len(D4['c'])} 4h bars)"
    if len(fund[0]) == 0:
        return None, "no funding prints"
    return (D4, d1, fund), ""


def run_universe(syms, root, table, brain, gates):
    """gates: list of (name, allowed labels). Returns {gate: rows}, per-coin coverage dict, dropped dict."""
    rows = {g: [] for g, _ in gates}
    cov, dropped = {}, {}
    for s in syms:
        inp, why = coin_inputs(s, root)
        if inp is None:
            dropped[s] = why
            continue
        D4, d1, fund = inp
        coin = C.build_coin(s, D4, d1, fund, table)
        info = dict(bars_4h=int(coin.n), first_4h=C.utc_str(int(coin.ts[0])), last_4h=C.utc_str(int(coin.ts[-1])),
                    bars_1d=int(len(d1["c"])), funding_prints=int(len(fund[0])), funding_first=C.utc_str(int(fund[0][0])),
                    funding_last=C.utc_str(int(fund[0][-1])), onsets_all=int(coin.onset.sum()),
                    onsets_eligible=int((coin.onset & coin.elig).sum()))
        for g, allowed in gates:
            for kind in C.KINDS:
                r = C.make_trades(coin, kind, allowed, g, brain)
                rows[g] += r
                info[f"trades_{g}_{kind}"] = len(r)
        cov[s] = info
    return rows, cov, dropped


def write_csv(rows, path):
    df = pd.DataFrame(rows, columns=C.COLUMNS)
    df.to_csv(path, index=False, float_format="%.10g")
    return df


def counts(df, label):
    print(f"[{label}] rows {len(df)}")
    for k in C.KINDS:
        d = df[df.kind == k]
        print(f"  {k}: DEV {int((d.split == 'DEV').sum())} VAL {int((d.split == 'VAL').sum())} coins {d.coin.nunique()}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--wave", default=WAVE)
    ap.add_argument("--miner", default=MINER)
    ap.add_argument("--brain", default=BRAIN)
    ap.add_argument("--out", default=HERE)
    ap.add_argument("--no-old20", action="store_true")
    a = ap.parse_args()
    C.lower_priority()
    btc = C.load_bars(os.path.join(a.miner, "spot_1d", "BTCUSDT.csv"), "1d")
    table = C.phase_table(btc["ts"], btc["c"])
    brain = load_brain(a.brain)
    nonbear = ("nonbear", C.NONBEAR)
    bear = ("bear", C.BEAR)
    rows, cov, dropped = run_universe(C.FRESH, a.wave, table, brain, [nonbear, bear])
    df = write_csv(rows["nonbear"], os.path.join(a.out, "trades.csv"))
    counts(df, "fresh non-bear")
    dc = write_csv(rows["bear"], os.path.join(a.out, "trades_control.csv"))
    counts(dc, "fresh control (DOWN)")
    meta = dict(fresh_kept=sorted(cov), fresh_dropped=dropped, coins=cov, btc_last_close_day=C.utc_str(int(btc["ts"][-1]))[:10],
                data_end=C.utc_str(C.DATA_END_MS), cost12=C.COST12, seed=C.SEED)
    if not a.no_old20:
        rows20, cov20, dropped20 = run_universe(C.OLD20, a.miner, table, brain, [nonbear])
        d20 = write_csv(rows20["nonbear"], os.path.join(a.out, "trades_old20.csv"))
        counts(d20, "old-20 non-bear")
        meta.update(old20_kept=sorted(cov20), old20_dropped=dropped20, old20_coins=cov20)
    meta["trades_fund_not_covered"] = int((~df.fund_covered).sum()) if len(df) else 0
    with open(os.path.join(a.out, "coverage.json"), "w", encoding="utf-8") as f:
        json.dump(meta, f, indent=1, sort_keys=True)
    print(f"fresh coins kept {len(cov)} dropped {len(dropped)}: {dropped}")
    print("trades by year (fresh, RIDE, entry year):", df[df.kind == "RIDE"].entry_utc.str[:4].value_counts().sort_index().to_dict())
    print("trades whose exit is beyond the funding file:", meta["trades_fund_not_covered"])


if __name__ == "__main__":
    main()
