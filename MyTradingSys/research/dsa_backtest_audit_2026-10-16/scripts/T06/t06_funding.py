"""T06 lead L1: real signed 8h funding vs the flat 1 bp both-sides substitute. DEV only (< 2024-07-01).

Reruns (a) the gross-effect screen primary cell and (b) the four chart-read G5 screens, with
   cost to a trade of side s  =  s * sum(rate of settlements in (entry, exit]) * 100   [% of notional]
(long pays a positive rate, short receives it). Reruns write to scripts/T06/out/, never over a result file.
Run from the worktree root:  python MyTradingSys/research/dsa_backtest_audit_2026-10-16/scripts/T06/t06_funding.py
"""
import contextlib
import csv
import importlib.util
import io
import json
import shutil
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[4]
RES = ROOT / "MyTradingSys" / "research"
OUT = HERE / "out"
FUND_DIR = Path("C:/Users/E-ngineers/IdeaProjects/BinanceDataFeed/Dumps/backtest/raw/fundingRate")   # live tree, read-only
sys.path.insert(0, str(RES / "gross_effect_screen_2026-10-15"))
sys.path.insert(0, str(RES / "chart_read_g5_2026-10-16"))
import screen as S  # noqa: E402
import common as K  # noqa: E402

CUT = S.CUTOFF_MS
PER = 8 * 3600 * 1000


def load_funding():
    ts, rate, itv = [], [], []
    for f in sorted(FUND_DIR.glob("BTCUSDT-fundingRate-*.csv")):
        with open(f, newline="", encoding="utf-8") as fh:
            for r in csv.DictReader(fh):
                t = int(r["calc_time"])
                if t >= CUT:                     # DEV only: never read a later rate
                    continue
                ts.append(t)
                rate.append(float(r["last_funding_rate"]))
                itv.append(int(r["funding_interval_hours"]))
    o = np.argsort(ts)
    return np.array(ts, np.int64)[o], np.array(rate)[o], np.array(itv)[o]


FT, FR, FI = load_funding()
CUM = np.concatenate(([0.0], np.cumsum(FR)))


def rate_sum(te_ms, tx_ms):
    """Sum of rates of settlements s with te < s <= tx (same boundary rule as the flat tx//per - te//per count)."""
    a = np.searchsorted(FT, np.asarray(te_ms, np.int64), side="right")
    b = np.searchsorted(FT, np.asarray(tx_ms, np.int64), side="right")
    return CUM[b] - CUM[a]


def real_funding_pct(e, x, side):
    """Signed funding cost % of notional for 1m entry/exit indices e, x."""
    te = S.TS0 + np.asarray(e, np.int64) * S.MS
    tx = S.TS0 + np.asarray(x, np.int64) * S.MS
    return np.asarray(side) * rate_sum(te, tx) * 100.0


def data_facts():
    off = FT % PER
    return dict(n=int(len(FT)), first=int(FT[0]), last=int(FT[-1]), intervals=sorted(set(FI.tolist())),
                off_boundary=int((off != 0).sum()), rate_min_bp=float(FR.min() * 1e4), rate_max_bp=float(FR.max() * 1e4),
                rate_mean_bp=float(FR.mean() * 1e4), share_negative=float((FR < 0).mean()),
                gaps_not_8h=int((np.diff(FT) != PER).sum()))


# ---------------------------------------------------------------- (a) gross screen
def gross_screen():
    A = S.load_dev(S.dev_files())
    led = S.build_ledger(A, S.NDAYS_DEV)
    cells = S.compute_cells(A, led, S.NDAYS_DEV)
    base = S.evaluate(cells, A, S.NDAYS_DEV)
    t, side = led["t"], led["side"]
    real = {}
    for (d, h) in cells["G"]:
        e = t + 1 + d
        real[(d, h)] = real_funding_pct(e, e + h, side)
    flat_primary = cells["FUND"][S.PRIMARY].copy()
    cells2 = dict(cells)
    cells2["FUND"] = real
    new = S.evaluate(cells2, A, S.NDAYS_DEV)
    arms = {}
    for arm in ("T", "notF", "C"):
        m = S.arm_masks(led)[arm] & ~np.isnan(cells["G"][S.PRIMARY])
        arms[arm] = dict(n_base=base[arm]["n"], mean_flat=base[arm]["mean"], mean_real=new[arm]["mean"],
                         delta=new[arm]["mean"] - base[arm]["mean"], t_cost_flat=base[arm]["t_cost"], t_cost_real=new[arm]["t_cost"],
                         mean_flat_fund=float(flat_primary[m].mean()), mean_real_fund=float(real[S.PRIMARY][m].mean()),
                         be_rt_pct=new[arm]["mean"])
    grid = []
    for (d, h), G in cells["G"].items():
        for arm in ("T", "C"):
            m = S.arm_masks(led)[arm] & ~np.isnan(G)
            grid.append(dict(d=d, h=h, arm=arm, mean_flat=float((G - cells["FUND"][(d, h)])[m].mean()),
                             mean_real=float((G - real[(d, h)])[m].mean())))
    return dict(base_verdict=base["verdict"], real_verdict=new["verdict"], diff_flat=base["diff"], diff_real=new["diff"],
                t_diff_flat=base["t_diff"], t_diff_real=new["t_diff"], arms=arms, grid=grid, side_counts=
                {int(s): int((side == s).sum()) for s in (-1, 1)})


# ---------------------------------------------------------------- (b) four G5 screens
STUDIES = ["mal_bb_mid_engulf_2026-10-16", "opr_bb_mtf_center_2026-10-16", "opr_preopen_tops_2026-10-16",
           "opr_weekly_low_round_sweep_2026-10-16"]


def signed_net_cells(A, t, side, hs, d=K.DELAY):
    t = np.asarray(t, np.int64)
    side = np.asarray(side)
    return {h: K.trade_gross(A["O"], t, side, h, d) - real_funding_pct(t + 1 + d, t + 1 + d + h, side) for h in hs}


def signed_placebo(A, t, side, h, lags=(-7, 7), d=K.DELAY):
    gs, ds, ts = [], [], []
    side = np.asarray(side)
    for lag in lags:
        tt = np.asarray(t, np.int64) + lag * K.DAYMIN
        ok = (tt >= 0) & (tt + 1 + d + h < len(A["O"]))
        g = K.trade_gross(A["O"], tt[ok], side[ok], h, d) - real_funding_pct(tt[ok] + 1 + d, tt[ok] + 1 + d + h, side[ok])
        gs.append(g)
        ds.append((tt[ok] + 1 + d) // K.DAYMIN)
        ts.append(tt[ok])
    return np.concatenate(gs), np.concatenate(ds), np.concatenate(ts)


def run_study(name, real, A_cache={}):
    tag = ("real" if real else "flat")
    od = OUT / f"g5_{tag}" / name
    od.mkdir(parents=True, exist_ok=True)
    shutil.copy(RES / name / "PRE_REG.md", od / "PRE_REG.md")
    spec = importlib.util.spec_from_file_location("st_" + name.replace("-", "_"), RES / name / "study.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    mod.HERE = od                                            # all writes land in out/, committed results untouched
    rec = []
    orig = (K.net_cells, K.placebo_gross, K.arm_row)
    if real:
        K.net_cells, K.placebo_gross = signed_net_cells, signed_placebo
    K.arm_row = lambda nm, r, _o=orig[2]: (rec.append((nm, dict(r))), _o(nm, r))[1]
    buf = io.StringIO()
    try:
        with contextlib.redirect_stdout(buf):
            rc = mod.main(["--full"])
    finally:
        K.net_cells, K.placebo_gross, K.arm_row = orig
    return dict(rc=rc, arms=rec, stdout=buf.getvalue()[:400])


def main():
    OUT.mkdir(exist_ok=True)
    res = dict(facts=data_facts())
    print("funding facts", res["facts"], flush=True)
    res["gross"] = gross_screen()
    print("gross done", res["gross"]["base_verdict"], res["gross"]["real_verdict"], flush=True)
    res["g5"] = {}
    for st in STUDIES:
        res["g5"][st] = {"flat": run_study(st, False), "real": run_study(st, True)}
        print("done", st, flush=True)
    with open(OUT / "funding_rerun.json", "w", encoding="utf-8", newline="\n") as fh:
        json.dump(res, fh, indent=1, default=float)
    return 0


if __name__ == "__main__":
    sys.exit(main())
