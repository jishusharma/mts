"""Backtest C (PLAN.md section 2): same fires, different exit policies, net of fees.

Question: do any of the existing layer fires pay once the exit is managed, instead of the live 8-bar timer?
Inputs: F:\\MTS\\data\\bigtrade\\fires_spot\\fires_*.csv (tradable rows with a side) and the spot bar cache
F:\\MTS\\data\\bigtrade\\cache\\spot\\klines_<tf>.npz. Entry = open of the first bar after the fire bar closed (market).
Path = bars of the fire's own TF; a stop and a target in the same bar -> stop first (conservative).
R = 1 ATR(14, Wilder, own TF) at the fire bar unless the policy is a percent stop.
Costs: taker both legs 5 bp + 1 bp slippage per leg = 12 bp of price round trip (fees.py DERIBIT_TAKER 0.0005; slippage is an
assumption, printed). Funding is not modelled (holds <= 96 bars).
Splits (repo split, aligned 2026-10-17): TRAIN 2022-01..2024-06, VALIDATE 2024-07..2025-06. HOLDOUT (2025-07..) is NOT read. Every (key x policy) cell is a registered
trial and is printed. Analysis settings, not live parameters; a positive cell is a candidate for D, not a rule.
Usage: python MyTradingSys/backtest/bigtrade/exit_policies.py   -> research/bigtrade_2026-10-09/EXIT_POLICIES_REPORT.md"""
import csv
import datetime as dt
import glob
import os
import sys
from collections import defaultdict
from pathlib import Path

import numpy as np

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[3]
FIRES = Path(os.environ.get("BIGTRADE_FIRES", r"F:\MTS\data\bigtrade\fires_spot"))
CACHE = Path(os.environ.get("BIGTRADE_CACHE", r"F:\MTS\data\bigtrade\cache\spot"))
OUT = ROOT / "MyTradingSys" / "research" / "bigtrade_2026-10-09" / "EXIT_POLICIES_REPORT.md"
FEE_RT = 0.0010          # 2 x 5 bp taker
SLIP_RT = 0.0002         # 2 x 1 bp assumed
COST = FEE_RT + SLIP_RT
TRAIN_END = dt.datetime(2024, 7, 1, tzinfo=dt.timezone.utc).timestamp() * 1000
VALID_END = dt.datetime(2025, 7, 1, tzinfo=dt.timezone.utc).timestamp() * 1000
DEV_ONLY = os.environ.get("EXIT_POLICIES_DEV_ONLY") == "1"   # rerun 2026-10-17: DEV (TRAIN) only, VALIDATE column not read
if DEV_ONLY:
    VALID_END = TRAIN_END
    OUT = OUT.with_name("EXIT_POLICIES_RERUN_DEV_2026-10-17.md")

# name -> dict(kind, stop (ATR or fraction of price), target (ATR/fraction or None), hold (bars), pct (bool))
POLICIES = {
    "live_like_1pct_2pct_8bars": dict(kind="bracket", stop=0.01, target=0.02, hold=8, pct=True),
    "bracket_1atr_2atr_24": dict(kind="bracket", stop=1.0, target=2.0, hold=24, pct=False),
    "bracket_1.5atr_3atr_24": dict(kind="bracket", stop=1.5, target=3.0, hold=24, pct=False),
    "time_24_wide_stop_2atr": dict(kind="bracket", stop=2.0, target=None, hold=24, pct=False),
    "time_96_wide_stop_2atr": dict(kind="bracket", stop=2.0, target=None, hold=96, pct=False),
    "be1atr_trail2atr_96": dict(kind="trail", stop=1.0, be_at=1.0, trail=2.0, hold=96),
}


def load_bars():
    out = {}
    for tf in ("1m", "5m", "15m", "1h"):
        z = np.load(CACHE / f"klines_{tf}.npz")
        out[tf] = dict(t=z["t"], o=z["o"].tolist(), h=z["h"].tolist(), l=z["l"].tolist(), c=z["c"].tolist())
    return out


def simulate(pol, side, bars, i0, atr):
    """Returns (net_return_fraction_of_price, risk_fraction_of_price, exit_reason) or None if the path runs off the data."""
    o, h, l, c = bars["o"], bars["h"], bars["l"], bars["c"]
    n = len(o)
    if i0 + pol["hold"] >= n:
        return None
    sgn = 1.0 if side == "long" else -1.0
    e = o[i0]
    dist = pol["stop"] * e if pol.get("pct") else pol["stop"] * atr
    if not dist > 0 or dist >= e:
        return None
    stop = e - sgn * dist
    tgt = None
    if pol["kind"] == "bracket" and pol["target"] is not None:
        tgt = e + sgn * (pol["target"] * e if pol.get("pct") else pol["target"] * atr)
    hw = e
    be_done = False
    last = i0 + pol["hold"]
    for j in range(i0, last + 1):
        hi, lo = h[j], l[j]
        s_hit = (lo <= stop) if sgn > 0 else (hi >= stop)
        if s_hit:                                  # stop first; gap through the stop fills at the open
            px = min(o[j], stop) if sgn > 0 else max(o[j], stop)
            return sgn * (px - e) / e - COST, dist / e, "stop"
        if tgt is not None and ((hi >= tgt) if sgn > 0 else (lo <= tgt)):
            return sgn * (tgt - e) / e - COST, dist / e, "target"
        if pol["kind"] == "trail":
            hw = max(hw, hi) if sgn > 0 else min(hw, lo)
            if not be_done and sgn * (hw - e) >= pol["be_at"] * atr:
                be_done = True
                stop = e
            if be_done:
                tr = hw - sgn * pol["trail"] * atr
                stop = max(stop, tr) if sgn > 0 else min(stop, tr)
    px = c[last]
    return sgn * (px - e) / e - COST, dist / e, "time"


def main():
    bars = load_bars()
    lines = ["# EXIT POLICIES REPORT (backtest C), %s" % dt.date.today().isoformat(), "",
             "Fires: %s. Bars: %s (spot). Entry = open of the bar after the fire bar closes. Costs %.1f bp RT taker + %.1f bp slippage "
             "(assumed). Stop-first on shared bars. HOLDOUT (2025-07..) not read. Policies:" % (FIRES, CACHE, FEE_RT * 1e4, SLIP_RT * 1e4), ""]
    for k, v in POLICIES.items():
        lines.append("- `%s`: %s" % (k, v))
    lines += ["", "Columns: n, mean net return in bp of price, win share (net > 0), mean net in R (R = stop distance), mean fee share of risk.",
              "`BOTH+` = mean net > 0 in TRAIN and VALIDATE with n >= 30 in each (necessary, not sufficient; no PBO yet).", ""]
    rows_out = []
    for f in sorted(glob.glob(str(FIRES / "fires_*.csv"))):
        fires = []
        for r in csv.DictReader(open(f, encoding="utf-8")):
            if r["tradable"] == "1" and r["side"] in ("long", "short") and r["atr"]:
                fires.append((int(r["t_fire_ms"]), r["side"], float(r["atr"]), r["tf"], r["key"]))
        if not fires:
            continue
        key, tf = fires[0][4], fires[0][3]
        b = bars[tf]
        t_arr = b["t"]
        for pname, pol in POLICIES.items():
            acc = {"TRAIN": [], "VALIDATE": []}
            for t_fire, side, atr, _, _ in fires:
                if t_fire >= VALID_END:
                    continue
                i0 = int(np.searchsorted(t_arr, t_fire, side="left"))     # first bar opening at/after the fire-bar close
                if i0 >= len(t_arr) or t_arr[i0] != t_fire:
                    continue
                res = simulate(pol, side, b, i0, atr)
                if res is None:
                    continue
                acc["TRAIN" if t_fire < TRAIN_END else "VALIDATE"].append(res)
            cells = {}
            for sp, xs in acc.items():
                if xs:
                    net = np.array([x[0] for x in xs])
                    risk = np.array([x[1] for x in xs])
                    cells[sp] = (len(xs), net.mean() * 1e4, float((net > 0).mean()), float((net / risk).mean()),
                                 float(COST / risk.mean()))
                else:
                    cells[sp] = (0, float("nan"), float("nan"), float("nan"), float("nan"))
            both = all(cells[s][0] >= 30 and cells[s][1] > 0 for s in cells)
            rows_out.append((key, pname, cells, both))
            print(key, pname, {s: cells[s][:2] for s in cells}, both, flush=True)
    lines += ["| layer key | policy | TRAIN n / bp / win / R | VALIDATE n / bp / win / R | BOTH+ |", "|---|---|---|---|---|"]
    for key, pname, cells, both in rows_out:
        def fmt(c):
            return "%d / %+.1f / %.2f / %+.2f" % (c[0], c[1], c[2], c[3]) if c[0] else "0"
        lines.append("| %s | %s | %s | %s | %s |" % (key, pname, fmt(cells["TRAIN"]), fmt(cells["VALIDATE"]), "YES" if both else ""))
    pos = [(k, p) for k, p, _, bth in rows_out if bth]
    lines += ["", "## Summary", "", "- cells run: %d (all are trials; none dropped)." % len(rows_out),
              "- cells positive in TRAIN and VALIDATE with n >= 30: %d." % len(pos)]
    for k, p in pos:
        lines.append("  - %s / %s" % (k, p))
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")
    print("wrote", OUT)


if __name__ == "__main__":
    main()
