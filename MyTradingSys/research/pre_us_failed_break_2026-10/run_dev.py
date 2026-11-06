"""Pre-US failed-break short, DEV only. Rules: PRE_REG.md sections 2-7 (frozen 2026-10-28). Nothing here chooses a parameter.

Usage: python run_dev.py --count   (signals/episodes only, no outcome column)
       python run_dev.py --full    (all cells, ledger.csv, DATA_MANIFEST.csv, sim_desk result json)
The loader refuses any bar with open >= 2024-07-01 (VALIDATION/HOLDOUT sealed).

Reading decisions where PRE_REG is silent (DECISION (OURS), most conservative reading, logged in RESULT.md):
 - ATR for a bar's decision = hourly Wilder ATR14 of the last hourly bar closed at or before the close of that 1m bar; break/E/dead use the
   ATR at the break bar, entry sizing/target use the ATR at the signal bar t.
 - ASH level at break bar b = max(high) of 00:00..b-1 UTC, valid only if the bar that set it (first occurrence) is <= b-60.
 - Swing levels: strict hourly pivot (above both neighbours), usable from the start of hour k+3 (2 h after the bar closed), looked up among
   hourly bars starting within the last 5 UTC days before 00:00 of the day, plus the current day.
 - "Within 3 bars after the break bar (inclusive)" = break bar b and b+1..b+3 (4 closes tested). One track per (level kind, value); after a break whose 4 closes did not fail the track expires and the same level may break again (new track).
 - Fills (tranches 2-4, target) are tested on bars after the entry bar only (t+2 ...). If one bar touches both the target and a pending tranche,
   the target fills first on the current size and the unfilled tranches are cancelled (adverse order for the rule).
 - Gap through a limit fills at the bar open (sell limit: max(limit, open); buy limit: min(limit, open)).
 - Variants: window end 12:00 (signals + time cap at 12:00). The "window end 13:00" variant of PRE_REG section 10 is the primary cell itself.
"""
import argparse
import csv
import datetime as dt
import hashlib
import json
import re
import sys
import warnings
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
sys.path.insert(0, str(REPO))
sys.path.insert(0, str(REPO / "MyTradingSys" / "backtest" / "bt"))

from MyTradingSys.backtest import fees  # noqa: E402
from MyTradingSys.backtest import research_kit as rk  # noqa: E402
from MyTradingSys.backtest import splits  # noqa: E402

ARCH = Path("F:/MTS/data/tom_raw/klines")
DAILY_ARCH = Path("F:/MTS/Dumps/backtest/raw_1d/klines")
FUND_BASE = Path("F:/MTS/Dumps/backtest")
DAYMIN = 1440
MS = 60_000
DAY = 86_400_000
TS0 = int(dt.datetime(2022, 1, 1, tzinfo=dt.timezone.utc).timestamp() * 1000)
CUTOFF_MS = int(dt.datetime(2024, 7, 1, tzinfo=dt.timezone.utc).timestamp() * 1000)
NDAYS_DEV = (dt.date(2024, 7, 1) - dt.date(2022, 1, 1)).days          # 912
FIRST_DAY = 5                      # PRE_REG section 6: first 5 days ineligible
W_START = 7 * 60                   # 07:00 UTC (minute of day), OURS
TICK = 0.1                         # PRE_REG section 3
ATR_N = 14                         # OURS
MIN_BREAK_ATR = 0.10               # OURS
MIN_LEVEL_ATR = 0.5                # OURS
DEAD_ATR = 1.5                     # OURS
FAIL_BARS = 3                      # OURS
MAX_SIGNALS = 3
NT = 4                             # tranches
TR_STEP_ATR = 0.5                  # OURS
TARGET_MIN_ATR = 1.0               # OURS
TARGET_DEFAULT_ATR = 1.5           # OURS
MARKET_LEG_EXTRA_BPS = 2.0               # OURS
TAKER_BPS = fees.BINANCE_TAKER * 1e4   # SOURCED fees.py (5 bps)
MAKER_BPS = fees.BINANCE_MAKER * 1e4   # SOURCED fees.py (2 bps)
N_MIN = 250                        # PRE_REG section 7
T_MIN = 2.0
SWING_DAYS = 5                     # OURS
SWING_LAG_H = 3                    # bar k usable from minute (k+3)*60: closes at k+1, +2 h


# ---------------------------------------------------------------- data
def load_dev(files, ts0=TS0, cutoff=CUTOFF_MS, ndays=NDAYS_DEV):
    n = ndays * DAYMIN
    A = {k: np.full(n, np.nan) for k in ("O", "H", "L", "C")}
    for f in files:
        with open(f, newline="", encoding="utf-8") as fh:
            for r in csv.reader(fh):
                if not r or not r[0][:1].isdigit():
                    continue
                t = int(float(r[0]))
                if t > 1e14:
                    t //= 1000
                if t >= cutoff:
                    raise ValueError(f"bar {t} >= 2024-07-01 refused (VALIDATION/HOLDOUT are sealed): {f}")
                i = (t - ts0) // MS
                if 0 <= i < n:
                    A["O"][i], A["H"][i], A["L"][i], A["C"][i] = float(r[1]), float(r[2]), float(r[3]), float(r[4])
    return A


def dev_files():
    out = []
    for y, m in [(2022, i) for i in range(1, 13)] + [(2023, i) for i in range(1, 13)] + [(2024, i) for i in range(1, 7)]:
        out.append(ARCH / f"BTCUSDT-1m-{y}-{m:02d}.csv")
    return out


# ---------------------------------------------------------------- indicators
class Hourly:
    def __init__(self, O, H, L, C):
        n = len(H) // 60
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            self.H = np.fmax.reduce(H[:n * 60].reshape(n, 60), axis=1)
            self.L = np.fmin.reduce(L[:n * 60].reshape(n, 60), axis=1)
        self.C = C[:n * 60].reshape(n, 60)[:, -1]
        self.n = n
        tr = np.full(n, np.nan)
        pc = self.C[:-1]
        tr[1:] = np.fmax(np.fmax(self.H[1:] - self.L[1:], np.abs(self.H[1:] - pc)), np.abs(self.L[1:] - pc))
        atr = np.full(n, np.nan)
        if n > ATR_N:
            seed = np.nanmean(tr[1:ATR_N + 1])
            atr[ATR_N] = seed
            for k in range(ATR_N + 1, n):
                atr[k] = atr[k - 1] if np.isnan(tr[k]) else (atr[k - 1] * (ATR_N - 1) + tr[k]) / ATR_N   # missing hour: carry
        self.atr = atr
        h, l = self.H, self.L
        sh = np.zeros(n, bool)
        sl = np.zeros(n, bool)
        sh[1:-1] = (h[1:-1] > h[:-2]) & (h[1:-1] > h[2:])
        sl[1:-1] = (l[1:-1] < l[:-2]) & (l[1:-1] < l[2:])
        self.sh, self.sl = sh, sl
        self._cache = {}

    def atr_at(self, m):
        """ATR of the last hourly bar closed at or before minute m (m = minute index of a bar's close time)."""
        k = m // 60 - 1
        if k < 0 or np.isnan(self.atr[k]):
            return None
        return float(self.atr[k])

    def swing(self, m, d0, kind):
        """Highest usable swing high (kind 'h') / lowest swing low ('l') at minute m; start hour >= d0 - 5 days."""
        hr = m // 60
        key = (hr, d0, kind)
        if key in self._cache:
            return self._cache[key]
        k0 = max(0, (d0 - SWING_DAYS * DAYMIN) // 60)
        k1 = hr - SWING_LAG_H
        v = None
        if k1 >= k0:
            flag = self.sh if kind == "h" else self.sl
            arr = self.H if kind == "h" else self.L
            ks = np.nonzero(flag[k0:k1 + 1])[0] + k0
            if len(ks):
                v = float(np.max(arr[ks]) if kind == "h" else np.min(arr[ks]))
        self._cache[key] = v
        return v


# ---------------------------------------------------------------- signals
def find_signals(O, H, L, C, hr, d, wend):
    """Signals of UTC day index d (bars 0..wend-1 of the day are readable). Returns list of (t_rel, kind, level, atr_break)."""
    d0 = d * DAYMIN
    pdh = np.nanmax(H[d0 - DAYMIN:d0]) if not np.all(np.isnan(H[d0 - DAYMIN:d0])) else np.nan
    open0 = O[d0]
    if np.isnan(pdh) or np.isnan(open0):
        return []
    hl = H[d0:d0 + wend].tolist()
    cl = C[d0:d0 + wend].tolist()
    tracks, signals = {}, []
    run_max, run_idx = -1e18, -1
    for j in range(wend - 1):                 # t+1 = j+1 must be inside the window
        if j >= W_START:
            m = d0 + j + 1
            atr = hr.atr_at(m)
            h, c = hl[j], cl[j]
            if atr is not None and not (h != h or c != c):
                # existing tracks
                for key, tk in tracks.items():
                    if tk["st"] != "active":
                        continue
                    tk["emax"] = max(tk["emax"], h)
                    if (tk["emax"] - tk["L"]) > DEAD_ATR * tk["atr"]:
                        tk["st"] = "dead"
                    elif c < tk["L"]:
                        tk["st"] = "signalled"
                        signals.append((j, key[0], tk["L"], tk["atr"]))
                    elif j - tk["b0"] >= FAIL_BARS:
                        tk["st"] = "expired"
                # new crossings
                levels = [("PDH", pdh)]
                if j >= 1 and run_idx <= j - 60:
                    levels.append(("ASH", run_max))
                sw = hr.swing(m, d0, "h")
                if sw is not None:
                    levels.append(("SWH", sw))
                for name, lv in levels:
                    key = (name, round(lv, 2))
                    if key in tracks and tracks[key]["st"] != "expired":
                        continue
                    if lv < open0 + MIN_LEVEL_ATR * atr or not (h > lv + MIN_BREAK_ATR * atr):
                        continue
                    tk = {"L": lv, "b0": j, "emax": h, "atr": atr, "st": "active"}
                    tracks[key] = tk
                    if (h - lv) > DEAD_ATR * atr:
                        tk["st"] = "dead"
                    elif c < lv:
                        tk["st"] = "signalled"
                        signals.append((j, name, lv, atr))
        hj = hl[j]
        if hj == hj and hj > run_max:
            run_max, run_idx = hj, j
    signals.sort(key=lambda s: (s[0], ("PDH", "ASH", "SWH").index(s[1])))
    return signals[:MAX_SIGNALS]


# ---------------------------------------------------------------- position
def manage(O, H, L, hr, d, t_rel, atr, wend, funding, ts0=TS0):
    """Short build after signal bar t (day-relative index t_rel). Returns episode dict or None if the entry bar is missing."""
    from MyTradingSys.backtest.bt.bt_data import funding_cost_pct
    d0 = d * DAYMIN
    e = d0 + t_rel + 1
    p1 = O[e]
    if np.isnan(p1):
        return None
    pending = [p1 + k * TR_STEP_ATR * atr for k in range(1, NT)]
    pdl = np.nanmin(L[d0 - DAYMIN:d0])
    sl = np.nanmin(L[d0:e])
    swl = hr.swing(e, d0, "l")
    cands = [x for x in (pdl, sl, swl) if x is not None and not np.isnan(x) and x <= p1 - TARGET_MIN_ATR * atr]
    target = max(cands) if cands else p1 - TARGET_DEFAULT_ATR * atr
    fills = [(float(p1), e)]
    end_g = d0 + wend
    mae = 0.0
    kind, exit_p, exit_i = None, None, None

    def upr(price):
        return sum((1.0 / NT) * (price - fp) / fp for fp, _ in fills)
    mae = max(mae, 100.0 * upr(float(H[e]))) if not np.isnan(H[e]) else mae
    for j in range(e + 1, end_g):
        o, h, lo = O[j], H[j], L[j]
        if np.isnan(o) or np.isnan(h) or np.isnan(lo):
            continue
        if lo <= target - TICK:
            kind, exit_p, exit_i = "target", min(float(o), float(target)), j
            break
        for pp in list(pending):
            if h >= pp + TICK:
                fills.append((max(float(pp), float(o)), j))
                pending.remove(pp)
        mae = max(mae, 100.0 * upr(float(h)))
    if kind is None:
        o = O[end_g]
        if np.isnan(o):
            return None
        kind, exit_p, exit_i = "cap", float(o), end_g
    gross = cost = fund = 0.0
    for k, (fp, fi) in enumerate(fills):
        w = 1.0 / NT
        gross += w * (fp - exit_p) / fp * 1e4
        cin = (TAKER_BPS + MARKET_LEG_EXTRA_BPS) if k == 0 else MAKER_BPS
        cout = MAKER_BPS if kind == "target" else (TAKER_BPS + MARKET_LEG_EXTRA_BPS)
        cost += w * (cin + cout)
        fund += w * float(funding_cost_pct(funding, ts0 + fi * MS, ts0 + exit_i * MS, -1)) * 100.0   # % -> bps; + = cost
    net = gross - cost - fund
    return {"day": d, "t_rel": t_rel, "e": e, "entry": float(p1), "atr": atr, "target": float(target), "n_tr": len(fills),
            "exit": kind, "exit_price": exit_p, "hold_min": exit_i - e, "gross_bps": gross, "cost_bps": cost,
            "fund_bps": fund, "net_bps": net, "mae_pct": mae}


def run(A, funding, wend=780, outcomes=True, ndays=NDAYS_DEV, first_day=FIRST_DAY):
    O, H, L, C = A["O"], A["H"], A["L"], A["C"]
    hr = Hourly(O, H, L, C)
    eps, nsig, ndays_sig, skipped = [], 0, 0, 0
    for d in range(first_day, ndays):
        sigs = find_signals(O, H, L, C, hr, d, wend)
        if not sigs:
            continue
        ndays_sig += 1
        nsig += len(sigs)
        t_rel, name, lv, atr_b = sigs[0]
        atr_t = hr.atr_at(d * DAYMIN + t_rel + 1)
        if atr_t is None:
            skipped += 1
            continue
        if not outcomes:
            if np.isnan(O[d * DAYMIN + t_rel + 1]):
                skipped += 1
                continue
            eps.append({"day": d, "t_rel": t_rel, "level": name})
            continue
        ep = manage(O, H, L, hr, d, t_rel, atr_t, wend, funding)
        if ep is None:
            skipped += 1
            continue
        ep.update({"level": name, "level_price": lv, "signals_that_day": len(sigs)})
        eps.append(ep)
    return {"episodes": eps, "signals": nsig, "signal_days": ndays_sig, "skipped": skipped}


# ---------------------------------------------------------------- statistics
def mdd_pct_of_k(nets_bps):
    cum = np.concatenate(([0.0], np.cumsum(nets_bps) / 100.0))
    return float(np.max(np.maximum.accumulate(cum) - cum))


def bh_mdd_pct(C):
    c = C[~np.isnan(C)]
    return float(100.0 * np.max((np.maximum.accumulate(c) - c) / np.maximum.accumulate(c)))


def summarize(eps, bh_mdd):
    n = len(eps)
    nets = np.array([e["net_bps"] for e in eps]) if n else np.array([])
    out = {"n": n}
    if n < 2:
        out.update({"verdict": "INCONCLUSIVE"})
        return out
    mean, sd = float(nets.mean()), float(nets.std(ddof=1))
    se = sd / np.sqrt(n)
    t = mean / se if se > 0 else float("nan")
    win, los = nets[nets > 0], nets[nets <= 0]
    cap = [e for e in eps if e["exit"] == "cap"]
    tgt = [e for e in eps if e["exit"] == "target"]
    cap_sum = float(sum(e["net_bps"] for e in cap))
    tgt_sum = float(sum(e["net_bps"] for e in tgt))
    maes = np.array([e["mae_pct"] for e in eps])
    mdd = mdd_pct_of_k([e["net_bps"] for e in sorted(eps, key=lambda x: x["e"])])
    cap_loss = -cap_sum
    ok_n, ok_mean, ok_t = bool(n >= N_MIN), bool(mean > 0), bool(t >= T_MIN)
    ok_cap, ok_mdd = bool(cap_loss < tgt_sum), bool(mdd <= bh_mdd)
    verdict = "INCONCLUSIVE" if not ok_n else ("PASS" if (ok_mean and ok_t and ok_cap and ok_mdd) else "FAIL")
    out.update({"mean_bps": mean, "sd_bps": sd, "se_bps": float(se), "t": float(t), "gross_mean_bps": float(np.mean([e["gross_bps"] for e in eps])),
                "cost_mean_bps": float(np.mean([e["cost_bps"] for e in eps])), "fund_mean_bps": float(np.mean([e["fund_bps"] for e in eps])),
                "win_rate": float(len(win) / n), "mean_winner_bps": float(win.mean()) if len(win) else None,
                "mean_loser_bps": float(los.mean()) if len(los) else None,
                "mae_pct_q": {q: float(np.percentile(maes, q)) for q in (50, 75, 90, 95, 99, 100)},
                "cap_days": len(cap), "cap_sum_bps": cap_sum, "target_days": len(tgt), "target_sum_bps": tgt_sum,
                "mdd_pct_of_k": mdd, "bh_mdd_pct": bh_mdd,
                "pass_parts": {"n>=250": ok_n, "mean>0": ok_mean, "t>=2": ok_t, "cap_loss<target_gain": ok_cap, "mdd<=bh_mdd": ok_mdd},
                "verdict": verdict})
    return out


# ---------------------------------------------------------------- regime context
def regime_context():
    """(regime_at, week mix line). Daily bars from the raw_1d archive (2020-01 .. 2024-06; pre-DEV history only feeds the RSI warm-up)."""
    import pandas as pd
    from MyTradingSys.backtest.layers.rsi.rsi_core import rsi_core
    rows = []
    for f in sorted(DAILY_ARCH.glob("BTCUSDT-1d-*.csv")):
        if not re.fullmatch(r"BTCUSDT-1d-\d{4}-\d{2}\.csv", f.name):
            continue
        with open(f, newline="", encoding="utf-8") as fh:
            for r in csv.reader(fh):
                if r and r[0][:1].isdigit() and int(r[0]) < CUTOFF_MS:
                    rows.append((int(r[0]), float(r[4])))
    rows.sort()
    df = pd.DataFrame(rows, columns=["t", "c"]).drop_duplicates("t")
    df["dt"] = pd.to_datetime(df["t"], unit="ms")
    daily = ([int(x) + DAY for x in df["t"]], [float(x) for x in df["c"]])

    def rsi_series(freq):
        g = df.set_index("dt")["c"].resample(freq, closed="left", label="left").last().dropna()
        ts = [int(x.timestamp() * 1000) for x in g.index]
        r = rsi_core([float(x) for x in g.values], 14)
        keep = [k for k in range(len(ts) - 1) if r[k] is not None]
        return [ts[k + 1] for k in keep], [r[k] for k in keep]
    wk, mo = rsi_series("W-MON"), rsi_series("MS")      # W-MON closed-left, left-labelled bins start Monday 00:00

    cache = {}

    def regime_at(t):
        dd = int(t // DAY)
        if dd not in cache:
            cache[dd] = rk.regime_tag(dd * DAY, daily, wk, mo)["regime"]
        return cache[dd]
    d0 = TS0 // DAY
    d0 += (4 - d0) % 7
    wstarts = [x * DAY for x in range(d0, CUTOFF_MS // DAY, 7)]
    line = rk.regime_mix_line([regime_at(t) for t in wstarts])
    return regime_at, line


def sha256(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


# ---------------------------------------------------------------- main
def main():
    ap = argparse.ArgumentParser()
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--count", action="store_true")
    g.add_argument("--full", action="store_true")
    a = ap.parse_args()
    files = dev_files()
    missing = [str(f) for f in files if not f.exists()]
    if missing:
        print("BLOCKED: missing data", missing)
        return 2
    A = load_dev(files)
    nan_min = int(np.isnan(A["O"]).sum())
    print(f"DEV minutes {len(A['O'])}, missing minutes {nan_min}; max close time read < 2024-07-01 (loader guard)")
    regime_at, mixline = regime_context()
    print("Regime mix (weeks, DEV):", mixline)
    cells = {"primary_07-13": 780, "variant_07-12": 720}
    if a.count:
        for name, wend in cells.items():
            r = run(A, None, wend=wend, outcomes=False)
            print(f"COUNT {name}: episodes n={len(r['episodes'])} signal_days={r['signal_days']} signals={r['signals']} skipped={r['skipped']}")
        print("next: prereg_gate.py with n above, sd 60 (OURS estimate), cost 14, --m auto --new-cells 3")
        return 0
    from MyTradingSys.backtest.bt import bt_data
    funding = bt_data.load_funding_strict(FUND_BASE, CUTOFF_MS)
    bh = bh_mdd_pct(A["C"])
    result = {"bh_mdd_pct": bh, "regime_mix_weeks": mixline, "missing_minutes": nan_min, "cells": {}}
    for name, wend in cells.items():
        r = run(A, funding, wend=wend, outcomes=True)
        s = summarize(r["episodes"], bh)
        s.update({"signals": r["signals"], "signal_days": r["signal_days"], "skipped": r["skipped"]})
        mix = {}
        for e in r["episodes"]:
            e["regime"] = regime_at((TS0 // DAY + e["day"]) * DAY) or "n/a"
            mix.setdefault(e["regime"], []).append(e["net_bps"])
        s["episode_regime"] = {k: {"n": len(v), "mean_bps": float(np.mean(v))} for k, v in sorted(mix.items())}
        lv = {}
        for e in r["episodes"]:
            lv.setdefault(e["level"], []).append(e["net_bps"])
        s["by_level"] = {k: {"n": len(v), "mean_bps": float(np.mean(v))} for k, v in sorted(lv.items())}
        result["cells"][name] = s
        print(f"CELL {name}: " + json.dumps(s, sort_keys=True))
        if name == "primary_07-13":
            cols = ["day", "t_rel", "level", "level_price", "entry", "atr", "target", "n_tr", "exit", "exit_price", "hold_min", "gross_bps",
                    "cost_bps", "fund_bps", "net_bps", "mae_pct", "regime"]
            with open(HERE / "ledger.csv", "w", newline="\n", encoding="utf-8") as fh:
                w = csv.writer(fh)
                w.writerow(cols)
                for e in r["episodes"]:
                    w.writerow([e[c] if not isinstance(e[c], float) else repr(round(e[c], 6)) for c in cols])
    prim = result["cells"]["primary_07-13"]
    print("VERDICT (primary, PRE_REG section 7):", prim["verdict"])
    with open(HERE / "DATA_MANIFEST.csv", "w", newline="\n", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["file", "sha256", "bytes"])
        for f in files:
            w.writerow([f.name, sha256(f), f.stat().st_size])
    out = REPO / "sim_desk" / "results" / "backtest-pre-us-failed-break-dev-run.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    payload = {"study": "backtest-pre-us-failed-break-dev-run", "split_scored": "DEV", "holdout_rows_scored": 0, "verdict": prim["verdict"],
               "n": prim["n"], "mean_net_bps_of_k": prim.get("mean_bps"), "t": prim.get("t"), "fee_regime": "Binance taker 5+2 bps in, maker 2 out; cap taker 5+2",
               "report": "MyTradingSys/research/pre_us_failed_break_2026-10/RESULT.md", "cells": result["cells"], "regime_mix_weeks": mixline}
    out.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8", newline="\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
