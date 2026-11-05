"""pz-4 Pizzino layer backtest, BTCUSDT spot daily (PRE_REG.md in this folder; rules = SPEC.md section 6).

Data: public SPOT klines 2017-08.. (F:/MTS/Dumps/backtest/spot_2017/BTCUSDT/1d). The loader end is the window end, so a
window's later bars are never loaded. Passes: `count` (trades and days per cell, no returns), `dev` (returns, DEV-stage
2017-08..<2024-07-01), `val` (VALIDATION 2024-07-01..<2025-07-01, the chosen cell only). HOLDOUT is never loaded here.
Every parameter not in SPEC.md as SOURCED is OURS.
"""
import argparse
import csv
import json
import math
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO))
from MyTradingSys.backtest.layers.pizzino import pizzino_indicators as pz  # noqa: E402

HERE = Path(__file__).resolve().parent
SPOT = Path("F:/MTS/Dumps/backtest/spot_2017/BTCUSDT")
DAY = 86_400_000
DEV_END = 1_719_792_000_000      # 2024-07-01 UTC (backtest/splits.py DEV_END)
VAL_END = 1_751_328_000_000      # 2025-07-01 UTC (splits.py HOLDOUT start)
COST_PCT = 0.14                  # round trip, SOURCED research_kit.TAKER_RT_PCT

DEFAULT = dict(ns=(1, 2, 3), dm=3, N=2, tol=0.005, R=20, conf=2, rr=1.0, fb=2.0, TS=20, B=None, W=50, tf="1d")
CELLS = {                        # PRE_REG.md family, frozen before any return
    "C0_default": {},
    "C1_conf3": dict(conf=3),
    "C2_conf1": dict(conf=1),
    "C3_n2-5-13": dict(ns=(2, 5, 13)),
    "C4_n3-8-21": dict(ns=(3, 8, 21)),
    "C5_rr1.5": dict(rr=1.5),
    "C6_TS10": dict(TS=10),
    "C7_count_req": dict(B=5),
    "C8_tf4h": dict(tf="4h"),
    "C9_tf1h": dict(tf="1h"),
}


def load(end_ms, tf="1d"):
    from MyTradingSys.backtest.bt.bt_data import load_klines
    bars = [b for b in load_klines(SPOT / tf, end_ms=end_ms) if b["t"] < end_ms]
    assert bars and bars[-1]["t"] < end_ms
    return bars


class Pivots:
    """Pivots known at the close of bar i, built incrementally; equals pz.pivots_known(high, low, n, i)."""

    def __init__(self, high, low, n):
        self.raw = pz._raw_pivots(high, low, n)
        self.k = 0
        self.alt = []

    def at(self, i):
        while self.k < len(self.raw) and self.raw[self.k].confirmed_at <= i:
            p = self.raw[self.k]
            if self.alt and self.alt[-1].kind == p.kind:
                if (p.price > self.alt[-1].price) if p.kind == "H" else (p.price < self.alt[-1].price):
                    self.alt[-1] = p
            else:
                self.alt.append(p)
            self.k += 1
        return self.alt


def signals(bars, prm, start_ms):
    """Entries (signal bar i, side, entry index, stop, target) with signal-bar open >= start_ms; one position at a time
    is enforced in simulate()."""
    H = [b["h"] for b in bars]; L = [b["l"] for b in bars]; C = [b["c"] for b in bars]
    piv = [Pivots(H, L, n) for n in prm["ns"]]
    st_hist = [[], [], []]
    out = []
    for i in range(len(bars) - 1):
        full = [p.at(i) for p in piv]
        known = [a[-4:] for a in full]  # alternating, so the last 4 hold the last 2 of each kind
        states = []
        for d, alt in enumerate(known):
            s, _ = pz.swing_state([p.price for p in alt if p.kind == "H"], [p.price for p in alt if p.kind == "L"], C[i])
            states.append(s); st_hist[d].append(s)
        if bars[i]["t"] < start_ms:
            continue
        conf = pz.nested_conf(states)
        dmk = known[prm["dm"] - 1]
        ph3 = [p.price for p in dmk if p.kind == "H"]; pl3 = [p.price for p in dmk if p.kind == "L"]
        ph1 = [p.price for p in known[0] if p.kind == "H"]; pl1 = [p.price for p in known[0] if p.kind == "L"]
        if not (ph3 and pl3 and ph1 and pl1):
            continue
        mid = pz.mid_line(ph3[-1], pl3[-1])
        s0 = max(0, i - prm["R"] - prm["N"] - 1)
        for side in ("long", "short"):
            sg = 1 if side == "long" else -1
            if sg * conf < prm["conf"] or (C[i] > mid) != (sg == 1) or C[i] == mid:
                continue
            levels = (ph1[-1], mid) if sg == 1 else (pl1[-1], mid)
            hit = False
            for X in levels:
                r = pz.break_retest(X, C[s0:i + 1], H[s0:i + 1], L[s0:i + 1], N=prm["N"], tol=prm["tol"], R=prm["R"],
                                    direction="up" if sg == 1 else "down")
                if r["retest_bar"] is not None and s0 + r["retest_bar"] == i and r["outcome"] == "hold":
                    hit = True
                    break
            if not hit:
                continue
            if prm["B"]:
                T = jason_count_ok(H, L, full[2], i, sg, prm)
                if not T:
                    continue
            entry = bars[i + 1]["o"]
            stop = pl1[-1] if sg == 1 else ph1[-1]
            pool = [p.price for p in full[0] if p.kind == ("H" if sg == 1 else "L")]
            plan = pz.plan_trade(side, entry, stop, pool, rr_min=prm["rr"], fallback_r=prm["fb"])
            if plan["take"]:
                out.append((i, side, i + 1, stop, plan["target"]))
    return out


def jason_count_ok(H, L, alt3, i, sg, prm):
    """three_bar in the trade direction reached within the last B bars, from the latest significant degree-3 pivot."""
    kind = "L" if sg == 1 else "H"
    ps = [p for p in alt3 if p.kind == kind]
    if not ps:
        return False
    t = ps[-1].index
    if not pz.is_significant(L if kind == "L" else H, t, kind, prm["W"]):
        return False
    cnt = pz.bar_count_from(H[: i + 1], L[: i + 1], t, kind)
    for k, v in enumerate(cnt):
        if abs(v) >= 3:
            return i - (t + k) < prm["B"]
    return False


def simulate(bars, sigs, prm):
    trades, free_at = [], -1
    for (i, side, e, stop, tgt) in sigs:
        if i < free_at:
            continue
        sg = 1 if side == "long" else -1
        entry = bars[e]["o"]
        risk = sg * (entry - stop)
        if risk <= 0:
            continue
        exit_px, j, why = None, e, "open_end"
        last = min(len(bars) - 1, e + prm["TS"])
        for j in range(e, last + 1):
            b = bars[j]
            if j == e + prm["TS"]:
                exit_px, why = b["o"], "time"; break
            o = b["o"]
            if sg * (o - stop) <= 0:
                exit_px, why = o, "stop_gap"; break
            if (b["l"] <= stop) if sg == 1 else (b["h"] >= stop):
                exit_px, why = stop, "stop"; break
            if sg * (o - tgt) >= 0:
                exit_px, why = o, "target_gap"; break
            if (b["h"] >= tgt) if sg == 1 else (b["l"] <= tgt):
                exit_px, why = tgt, "target"; break
        if exit_px is None:
            continue                      # trade runs past the loaded window: dropped, counted in RESULT as open_end
        gross = sg * (exit_px - entry) / risk
        cost = COST_PCT / 100 * entry / risk
        trades.append(dict(signal_t=bars[i]["t"], entry_t=bars[e]["t"], exit_t=bars[j]["t"], side=side, entry=entry,
                           stop=stop, target=tgt, exit=exit_px, why=why, gross_R=gross, cost_R=cost, net_R=gross - cost))
        free_at = j
    return trades


def stats(tr):
    n = len(tr)
    if n == 0:
        return dict(n=0)
    x = [t["net_R"] for t in tr]
    m = sum(x) / n
    sd = math.sqrt(sum((v - m) ** 2 for v in x) / (n - 1)) if n > 1 else float("nan")
    return dict(n=n, gross_R=sum(t["gross_R"] for t in tr) / n, cost_R=sum(t["cost_R"] for t in tr) / n, net_R=m,
                sd_R=sd, t=m / (sd / math.sqrt(n)) if n > 1 and sd > 0 else float("nan"),
                win=sum(1 for v in x if v > 0) / n, long=sum(1 for t in tr if t["side"] == "long"))


def run(pass_, cells):
    end, start = (DEV_END, 0) if pass_ in ("count", "dev") else (VAL_END, DEV_END)
    cache, res = {}, {}
    for name in cells:
        prm = dict(DEFAULT, **CELLS[name])
        bars = cache.setdefault(prm["tf"], None) or cache.__setitem__(prm["tf"], load(end, prm["tf"])) or cache[prm["tf"]]
        tr = simulate(bars, signals(bars, prm, start), prm)
        if pass_ == "count":
            res[name] = dict(n=len(tr), days=len({t["entry_t"] // DAY for t in tr}),
                             stop_pct_median=sorted(abs(t["entry"] - t["stop"]) / t["entry"] * 100 for t in tr)[len(tr) // 2] if tr else None)
        else:
            res[name] = dict(stats(tr), trades=tr)
            with open(HERE / f"trades_{pass_}_{name}.csv", "w", newline="\n") as f:
                w = csv.DictWriter(f, fieldnames=list(tr[0].keys()) if tr else ["none"], lineterminator="\n")
                w.writeheader(); w.writerows(tr)
    return res


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--pass", dest="p", choices=["count", "dev", "val"], required=True)
    ap.add_argument("--cell", action="append")
    a = ap.parse_args()
    if a.p == "val" and (not a.cell or len(a.cell) != 1):
        sys.exit("val reads ONE pre-chosen cell")
    r = run(a.p, a.cell or list(CELLS))
    for k, v in r.items():
        print(k, json.dumps({x: (round(y, 4) if isinstance(y, float) else y) for x, y in v.items() if x != "trades"}))
