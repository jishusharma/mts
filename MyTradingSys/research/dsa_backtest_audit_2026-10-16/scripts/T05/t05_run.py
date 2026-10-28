"""T05 placebo run, one study per call (chunks): python t05_run.py <mal_bb|opr_bb|wlow|preopen|screen|candle> [--sets 1000]
Writes scripts/T05/out/placebo_<study>.csv and out/tpool_<study>.npz. DEV only (the studies' loaders refuse bars >= 2024-07-01).
SEED is printed. Run from the repo root."""
import csv
import importlib.util
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
RES = HERE.parents[2]                       # MyTradingSys/research
OUT = HERE / "out"
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(RES / "chart_read_g5_2026-10-16"))
import t05_core as C  # noqa: E402
import common as K  # noqa: E402

SEED = 20261016
B_BOOT = 2000
STUDY_DIR = {"mal_bb": "mal_bb_mid_engulf_2026-10-16", "opr_bb": "opr_bb_mtf_center_2026-10-16",
             "wlow": "opr_weekly_low_round_sweep_2026-10-16", "preopen": "opr_preopen_tops_2026-10-16"}


def load_mod(key):
    p = RES / STUDY_DIR[key] / "study.py"
    spec = importlib.util.spec_from_file_location("study_" + key, p)
    m = importlib.util.module_from_spec(spec)
    sys.modules["study_" + key] = m
    spec.loader.exec_module(m)
    return m


def published(key):
    f = RES / STUDY_DIR[key] / "trials.csv"
    rows = list(csv.DictReader(open(f, encoding="utf-8")))
    return {r["cell"]: r for r in rows}, len(rows)


def arm(study, name, t, side, h, cd, ctrl_t=None, ctrl_side=None, pub=None, mode="gap", d=1, primary=False):
    t = np.asarray(t, np.int64)
    side = np.broadcast_to(np.asarray(side), t.shape).copy() if np.ndim(side) == 0 else np.asarray(side)
    return dict(study=study, name=name, t=t, side=side, h=h, d=d, cd=cd, mode=mode, ctrl_t=ctrl_t, ctrl_side=ctrl_side, pub=pub,
                primary=primary)


def horizon_arms(study, label, t, side, hs, primary_h, cd, ctrl_t, pubs, pub_primary_name, sec_fmt):
    out = []
    for h in hs:
        nm = pub_primary_name if h == primary_h else sec_fmt.format(h=h)
        out.append(arm(study, f"{label} h={h}", t, side, h, cd, ctrl_t, side, pubs.get(nm), primary=(h == primary_h)))
    return out


def specs_for(study):
    A = K.load()
    if study == "mal_bb":
        m = load_mod("mal_bb")
        st = m.build(A)
        S = m.sets(st)
        pubs, ntr = published("mal_bb")
        a1 = horizon_arms("mal_bb", "A1", m.tdec(S["e1"]), -1, m.HS, 60, 60, m.tdec(S["ctrl1"]), pubs,
                          "A1: engulf (a) close, SHORT, h=60", "A1 h={h}")
        a2 = horizon_arms("mal_bb", "A2", m.tdec(S["e2"] + 1), -1, m.HS, 60, 60, m.tdec(S["e2c"] + 1), pubs,
                          "A2: second break close, SHORT, h=60", "A2 h={h}")
        return A, a1 + a2, ntr
    if study == "opr_bb":
        m = load_mod("opr_bb")
        P = m.prep(A)
        S = m.sets(P)
        pubs, ntr = published("opr_bb")
        td = lambda ks: (np.asarray(ks) + 1) * 60 - 1
        au = horizon_arms("opr_bb", "AU", td(S["up_keep"]), 1, m.HS, 120, 120, td(S["up_ctrl"]), pubs,
                          "AU: touch bar closes above its mid, LONG at its close, h=120", "AU h={h}")
        ad = horizon_arms("opr_bb", "AD", td(S["dn_keep"]), -1, m.HS, 120, 120, td(S["dn_ctrl"]), pubs,
                          "AD: touch bar closes below its mid, SHORT at its close, h=120", "AD h={h}")
        return A, au + ad, ntr
    if study == "wlow":
        m = load_mod("wlow")
        Lw = m.week_low_prior(A["L"])
        j, lvl, fam = m.pooled(A, m.P_PRIMARY, Lw)
        Cw = m.win(A["C"], j, m.WINDOW + 1)
        cls, r, s = m.abc_parts(Cw, lvl)
        okw = ~np.isnan(Cw).any(1)
        rl, rl_c = (r <= m.K_PRIMARY) & okw, (r > m.K_PRIMARY) & okw
        acc = m.accepted_first3(Cw, lvl)
        asm, as_c = acc & okw, ~acc & okw
        t_rl, t_rl_c, t_as = j + np.minimum(r, m.K_PRIMARY), j + m.K_PRIMARY, j + 2
        pubs, ntr = published("wlow")
        rlA = horizon_arms("wlow", "RL", t_rl[rl], 1, m.HS, 60, 60, t_rl_c[rl_c], pubs,
                           "RL: reclaim within 5 min, LONG at the reclaim close, h=60", "RL h={h}")
        asA = horizon_arms("wlow", "AS", t_as[asm], -1, m.HS, 60, 60, t_as[as_c], pubs,
                           "AS: first three closes below, SHORT at the third close, h=60", "AS h={h}")
        return A, rlA + asA, ntr
    if study == "preopen":
        m = load_mod("preopen")
        ev, cnt, aux = m.build(A)
        g1 = m.groups(ev["S1"])
        t = ev["t"]
        pubs, ntr = published("preopen")
        h1 = horizon_arms("preopen", "H1", t[g1 == "quick"], -1, m.HS, 60, 60, t[g1 != "quick"], pubs,
                          "H1: S1 quick, SHORT at the break close, h=60", "S1 quick SHORT h={h}")
        h2 = horizon_arms("preopen", "H2", t[g1 == "slow"], 1, m.HS, 60, 60, t[g1 != "slow"], pubs,
                          "H2: S1 slow, LONG at the break close, h=60", "S1 slow LONG h={h}")
        return A, h1 + h2, ntr
    if study == "screen":
        S = K.S
        led = S.build_ledger(A, S.NDAYS_DEV)
        F = led["F"]
        arms = []
        for nm, mk in (("T (flow-confirmed)", F), ("notF", ~F), ("C (all encounters)", np.ones(len(F), bool))):
            arms.append(arm("screen", nm + " d=1 h=60", led["t"][mk], led["side"][mk], 60, 60, None, None, None, primary=True))
        return A, arms, 3 * len(S.DS) * len(S.HS)
    raise SystemExit("unknown study")


def candle_specs(A):
    import pandas as pd
    f = RES / "layer_lab/candle_close_2026-10-14/events.csv.gz"
    e = pd.read_csv(f, usecols=["time", "side", "tf", "family", "signature", "gross"])
    tm = pd.to_datetime(e["time"], utc=True)
    e["i"] = ((tm - pd.Timestamp("2022-01-01", tz="UTC")) / pd.Timedelta(minutes=1)).round().astype(np.int64)
    e = e[(e["i"] >= 0) & (e["i"] < len(A["O"]))]
    arms = []
    for (tf, fam, sig), g in e.groupby(["tf", "family", "signature"], sort=True):
        arms.append(arm("candle", f"tf{tf} {fam} {sig}", g["i"].to_numpy(), g["side"].to_numpy(), 60, 0, None, None,
                        dict(n=len(g), mean=float(g["gross"].mean() * 100)), mode="day", d=-1, primary=True))
    return arms, 126


class Tabs:
    def __init__(self, A, no_fund=False):
        self.O, self.nf, self.c = A["O"], no_fund, {}

    def get(self, h, d):
        k = (h, d)
        if k not in self.c:
            raw = C.raw_table(self.O, h, d)
            fund = np.zeros(len(raw)) if self.nf else C.fund_table(len(raw), h, d)
            self.c[k] = (raw, fund, C.Pools(np.nonzero(~np.isnan(raw))[0]))
        return self.c[k]


def run_arm(spec, ordinal, tabs, B):
    raw, fund, pool = tabs.get(spec["h"], spec["d"])
    d = spec["d"]
    t, side = spec["t"], spec["side"]
    inb = (t >= 0) & (t < len(raw))
    t, side = t[inb], side[inb]
    ok = ~np.isnan(raw[t])
    t, side = t[ok], side[ok]
    n = len(t)
    row = dict(study=spec["study"], arm=spec["name"], primary=int(spec["primary"]), h=spec["h"], n=n)
    if n < 5:
        return row, None
    rng = np.random.default_rng([SEED, ordinal])
    m, se = C.set_stats(raw, fund, t[None, :], side, d)
    m, se = float(m[0]), float(se[0])
    dr = C.draw_placebo(rng, t, side, pool, n_sets=B, cd=spec["cd"], mode=spec["mode"], max_rounds=(12 if spec["mode"] == "day" else 200))
    pm, pse = C.set_stats(raw, fund, dr.idx, side, d)
    pt = pm / pse
    g = side * raw[t] - fund[t]
    entry = t + 1 + d
    share, comps = C.overlap(entry, spec["h"])
    sd_boot = C.week_bootstrap_sd(g, entry, B_BOOT, np.random.default_rng([SEED, ordinal, 1]))
    row.update(mean_g=m, se_pub=se, t_gross=m / se, t_net=(m - C.C_PCT) / se,
               placebo_mean=float(pm.mean()), placebo_sd=float(pm.std(ddof=1)), sd_ratio=float(pm.std(ddof=1) / se),
               p_mean=C.empirical_p(m, pm), p_t=C.empirical_p(m / se, pt), pt95=float(np.quantile(pt, 0.95)),
               conflict_share=dr.conflict_share, overlap_share=share, n_eff=comps, boot_sd=sd_boot,
               boot_t_gross=m / sd_boot, boot_t_net=(m - C.C_PCT) / sd_boot)
    if spec["ctrl_t"] is not None and len(spec["ctrl_t"]):
        ct = np.asarray(spec["ctrl_t"], np.int64)
        cs = np.broadcast_to(np.asarray(spec["ctrl_side"]), ct.shape) if np.ndim(spec["ctrl_side"]) == 0 else np.asarray(spec["ctrl_side"])
        okc = (ct >= 0) & (ct < len(raw))
        ct, cs = ct[okc], cs[okc]
        okc = ~np.isnan(raw[ct])
        row["ctrl_mean"] = float((cs[okc] * raw[ct[okc]] - fund[ct[okc]]).mean())
        row["ctrl_n"] = int(okc.sum())
    pub = spec["pub"]
    if pub:
        row["pub_n"] = int(float(pub["n"]))
        row["pub_mean"] = float(pub.get("mean_G", pub.get("mean")))
        row["pub_se"] = float(pub["se"]) if "se" in pub else float("nan")
    hy = C.half_year_table(g, entry) if n >= 100 else {}
    for k, (nn, mu) in hy.items():
        row[f"hy_{k}"] = f"{mu:.4f}|{nn}"
    return row, pt


def main(argv):
    study = argv[0]
    B = int(argv[argv.index("--sets") + 1]) if "--sets" in argv else 1000
    print(f"T05 run study={study} SEED={SEED} sets={B} boot={B_BOOT}", flush=True)
    if study == "candle":
        A = K.load()
        arms, ntr = candle_specs(A)
        tabs = Tabs(A, no_fund=True)
    else:
        A, arms, ntr = specs_for(study)
        tabs = Tabs(A)
    rows, pools = [], {}
    for i, sp in enumerate(arms):
        row, pt = run_arm(sp, i, tabs, B)
        row["n_trials_study"] = ntr
        rows.append(row)
        if pt is not None:
            pools[f"{sp['name']}"] = pt
        print(i, sp["name"], row.get("n"), f"mean={row.get('mean_g', float('nan')):.4f} p={row.get('p_mean', float('nan')):.3f} "
              f"sdr={row.get('sd_ratio', float('nan')):.2f}", flush=True)
    cols = []
    for r in rows:
        for k in r:
            if k not in cols:
                cols.append(k)
    OUT.mkdir(exist_ok=True)
    with open(OUT / f"placebo_{study}.csv", "w", newline="\n", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=cols)
        w.writeheader()
        w.writerows(rows)
    np.savez_compressed(OUT / f"tpool_{study}.npz", **{k: v.astype(np.float32) for k, v in pools.items()})
    print("wrote", OUT / f"placebo_{study}.csv")


if __name__ == "__main__":
    main(sys.argv[1:])
