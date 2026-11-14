"""nkp1 analysis. Two stages so VAL cannot influence selection:
  python analyze.py select   -> reads DEV rows ONLY (day < 2024-01-01), writes cells_frozen.json (commit it before stage 2)
  python analyze.py val      -> reads cells_frozen.json, runs Step A tables + VAL once on the frozen cells, writes summary CSVs/JSON."""
import os, sys, json, glob, subprocess
import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import phases as PH
import ctx as CX
import study as S

OUTC = S.OUTC
FEE_T, FEE_M = S.FEE_T, S.FEE_M
MIN_N, MIN_DAYS, TOPK = 150, 40, 3
Z90 = 1.2816


def load(dev_only=False, suffix=""):
    TRs, PLs, meta = [], [], {}
    for sym in S.ALL_SYMS:
        r = pd.read_pickle(os.path.join(OUTC, f"{sym}{suffix}.pkl"))
        tr = r["TR"]
        pl = r["PL"]
        if dev_only:
            tr = tr[tr.day < S.SPLIT_DAY]
            pl = pl.iloc[0:0] if len(pl) else pl
        TRs.append(tr)
        PLs.append(pl)
        meta[sym] = dict(first=r["first"], funding=r["funding"])
    TR = pd.concat(TRs, ignore_index=True)
    PL = pd.concat([p for p in PLs if len(p)], ignore_index=True) if not dev_only else None
    lab = PH.phase_daily()
    lab["day"] = (CX.ms_idx(lab.index) // 86400000).astype(int)
    lab = lab.set_index("day")
    for df in (TR, PL):
        if df is None:
            continue
        df["ph"] = df.day.map(lab.phase_id)
        df["pos40"] = df.day.map(lab.pos40)
    TR = TR[TR.ph.notna()].copy()
    if PL is not None:
        PL = PL[PL.ph.notna()].copy()
    for df in (TR, PL):
        if df is None:
            continue
        df["ph"] = df.ph.astype(int)
        alw = df.ph.map(PH.ALLOWED).to_numpy()
        alw = np.where(alw == 0, np.where(df.pos40.to_numpy() <= 0.5, 1, -1), alw)
        df["ok"] = df.side.to_numpy() == alw
        df["val"] = df.day >= S.SPLIT_DAY
    TR["net"] = (TR.ret - FEE_T - TR.fund) / TR.Rf
    TR["gross"] = TR.ret / TR.Rf
    TR["costR"] = (FEE_T + TR.fund) / TR.Rf
    TR["net_m"] = np.where(TR.filled_m, (TR.ret_m - FEE_M - TR.fund) / TR.Rf_m, np.nan)
    TR["feeR"] = FEE_T / TR.Rf
    return TR, PL, lab, meta


def cluster(x, day):
    """day-cluster ratio estimator: mean, se, n_days."""
    x = np.asarray(x, float)
    if len(x) < 2:
        return (float(x.mean()) if len(x) else np.nan), np.nan, len(x)
    g = pd.DataFrame({"x": x, "d": day}).groupby("d").x.agg(["sum", "count"])
    s, c = g["sum"].to_numpy(), g["count"].to_numpy()
    m = s.sum() / c.sum()
    k = len(g)
    if k < 2:
        return m, np.nan, k
    se = np.sqrt(k / (k - 1) * ((s - m * c) ** 2).sum()) / c.sum()
    return m, se, k


def boot_cluster(x, day, rng, B=2000):
    g = pd.DataFrame({"x": np.asarray(x, float), "d": day}).groupby("d").x.agg(["sum", "count"])
    s, c = g["sum"].to_numpy(), g["count"].to_numpy()
    k = len(g)
    idx = rng.integers(0, k, (B, k))
    mm = s[idx].sum(1) / c[idx].sum(1)
    return np.percentile(mm, [2.5, 97.5]), (np.sum(mm <= 0) + 1) / (B + 1)


def ex_best5(x, day):
    g = pd.DataFrame({"x": np.asarray(x, float), "d": day}).groupby("d").x.sum().sort_values(ascending=False)
    keep = ~pd.Series(day).isin(g.index[:5]).to_numpy()
    return float(np.asarray(x, float)[keep].mean()) if keep.any() else np.nan


def bh(ps):
    ps = np.asarray(ps, float)
    o = np.argsort(ps)
    m = len(ps)
    q = np.empty(m)
    prev = 1.0
    for rank, i in zip(range(m, 0, -1), o[::-1]):
        prev = min(prev, ps[i] * m / rank)
        q[i] = prev
    return q


def cell_mask(df, phase, layer, bucket, direction="ok"):
    m = (df.ph == phase) & (df[f"b{layer}"] == bucket)
    return m & df.ok if direction == "ok" else m & ~df.ok


def select(out=None):
    """Step B on DEV only. Returns frozen cell dict."""
    TR, _, lab, meta = load(dev_only=True)
    TR = TR[TR.sig]
    assert TR.day.max() < S.SPLIT_DAY, "VAL leaked into selection"
    ldev = lab[lab.index < S.SPLIT_DAY]
    share = ldev.phase_id.value_counts(normalize=True)
    eligible_ph = {int(p) for p, v in share.items() if v >= 0.05}
    kept, table = {}, []
    for var in S.VARIANTS:
        T = TR[TR.variant == var]
        rows = []
        for ph in range(1, 7):
            for L in range(1, 9):
                for b in (0, 1, 2):
                    sub = T[cell_mask(T, ph, L, b)]
                    n = len(sub)
                    if n == 0:
                        continue
                    m, se, k = cluster(sub.net.to_numpy(), sub.day.to_numpy())
                    score = m - Z90 * se if se == se else np.nan
                    rows.append(dict(variant=var, phase=ph, layer=L, bucket=b, n=n, days=k, mean=m, se=se, score=score,
                                     eligible=bool(n >= MIN_N and k >= MIN_DAYS and ph in eligible_ph)))
        R = pd.DataFrame(rows)
        table.append(R)
        cand = R[R.eligible & (R.score > 0)].sort_values("score", ascending=False)
        chosen, used = [], set()
        for _, r in cand.iterrows():
            if r.layer in used:
                continue
            chosen.append({k: (int(r[k]) if k in ("phase", "layer", "bucket", "n", "days") else float(r[k])) for k in ("phase", "layer", "bucket", "n", "days", "mean", "se", "score")})
            used.add(r.layer)
            if len(chosen) == TOPK:
                break
        kept[var] = chosen
    pd.concat(table).to_csv(os.path.join(HERE, "dev_cells_all.csv"), index=False)
    sha = subprocess.run(["git", "-C", HERE, "rev-parse", "HEAD"], capture_output=True, text=True).stdout.strip()
    frozen = dict(code_commit=sha, split="2024-01-01", dev_phase_share={PH.PHASES[int(p)]: round(float(v), 4) for p, v in share.items()},
                  eligible_phases=sorted(eligible_ph), kept=kept)
    json.dump(frozen, open(out or os.path.join(HERE, "cells_frozen.json"), "w"), indent=1)
    return frozen


def stats_block(sub, rng):
    m, se, k = cluster(sub.net.to_numpy(), sub.day.to_numpy())
    (lo, hi), p = boot_cluster(sub.net.to_numpy(), sub.day.to_numpy(), rng)
    return dict(n=len(sub), days=k, net=m, ci_lo=lo, ci_hi=hi, p=p, gross=sub.gross.mean(), costR=sub.costR.mean(),
                ex5=ex_best5(sub.net.to_numpy(), sub.day.to_numpy()), win=(sub.net > 0).mean())


def pool_net(var, TR, PL, ph, L, b):
    """net-R matrix (N x K) of random-entry candidates in the same cell on VAL: same variant, phase, bucket, phase-appropriate side.
    NK1: pool rows with 10 candidate entry bars (b3..b12); NK5: every VAL anchor (signal or not), K=1. Entry hour = the fixed session anchor."""
    if var.startswith("NK1"):
        P = PL[(PL.variant == var) & PL.val & (PL.ph == ph) & (PL[f"b{L}"] == b) & PL.ok]
        if not len(P):
            return None
        return (np.stack(P.pr.to_numpy()) - FEE_T - np.stack(P.pf.to_numpy())) / np.stack(P.pR.to_numpy())
    P = TR[(TR.variant == var) & TR.val & (TR.ph == ph) & (TR[f"b{L}"] == b) & TR.ok]
    return P.net.to_numpy()[:, None] if len(P) else None


def placebo_draws(NET, n, rng, draws=1000):
    if NET is None:
        return None
    N, K = NET.shape
    i = rng.integers(0, N, (draws, n))
    kk = rng.integers(0, K, (draws, n))
    return NET[i, kk].mean(1)


def phase_table(TR, var):
    """Step A: per phase, appropriate vs opposite direction; DEV and VAL; no pooled headline."""
    rows = []
    T = TR[(TR.variant == var) & TR.sig]
    for ph in range(1, 7):
        r = dict(variant=var, phase=PH.PHASES[ph])
        for per, msk in (("DEV", ~T.val), ("VAL", T.val)):
            a = T[msk & (T.ph == ph) & T.ok]
            o = T[msk & (T.ph == ph) & ~T.ok]
            ma, sa, ka = cluster(a.net.to_numpy(), a.day.to_numpy())
            mo, so, ko = cluster(o.net.to_numpy(), o.day.to_numpy())
            r.update({f"{per}_n_app": len(a), f"{per}_days_app": ka, f"{per}_gross_app": a.gross.mean() if len(a) else np.nan,
                      f"{per}_cost_app": a.costR.mean() if len(a) else np.nan, f"{per}_net_app": ma,
                      f"{per}_n_opp": len(o), f"{per}_net_opp": mo,
                      f"{per}_diff": ma - mo, f"{per}_diff_se": np.sqrt(sa ** 2 + so ** 2) if sa == sa and so == so else np.nan})
        rows.append(r)
    return pd.DataFrame(rows)


def val(frozen):
    TR, PL, lab, meta = load()
    Tg = TR[TR.sig]
    rng = np.random.default_rng(1114)
    out = dict(code_commit_at_freeze=frozen["code_commit"])
    # Step A
    A = pd.concat([phase_table(TR, v) for v in S.VARIANTS])
    A.to_csv(os.path.join(HERE, "stepA_phase_table.csv"), index=False)
    # coverage of context layers
    cov = []
    for v in S.VARIANTS:
        T = Tg[Tg.variant == v]
        for L in range(1, 9):
            cov.append(dict(variant=v, layer=f"C{L}", dev_with_data=int(((T.val == False) & (T[f"b{L}"] >= 0)).sum()),
                            val_with_data=int(((T.val) & (T[f"b{L}"] >= 0)).sum()), signals=len(T)))
    pd.DataFrame(cov).to_csv(os.path.join(HERE, "layer_coverage.csv"), index=False)
    # VAL on frozen cells, once
    rows = []
    for v, cells in frozen["kept"].items():
        Tv = Tg[(Tg.variant == v) & Tg.val]
        Td = Tg[(Tg.variant == v) & ~Tg.val]
        for c in cells:
            ph, L, b = c["phase"], c["layer"], c["bucket"]
            sub = Tv[cell_mask(Tv, ph, L, b)]
            r = dict(variant=v, phase=PH.PHASES[ph], layer=f"C{L}", bucket=CX.LABELS[f"C{L}"][b], dev_n=c["n"], dev_net=c["mean"], dev_score=c["score"])
            if len(sub) >= 2:
                st = stats_block(sub, rng)
                draws = placebo_draws(pool_net(v, TR, PL, ph, L, b), len(sub), rng)
                pp = float((draws >= sub.net.mean()).mean()) if draws is not None else np.nan
                pl_mean = float(draws.mean()) if draws is not None else np.nan
                m6 = sub[sub.net_m.notna()]
                r.update(st)
                r.update(placebo_p=pp, placebo_mean=pl_mean, shrink=st["net"] - c["mean"],
                         n_maker=len(m6), net_maker6=m6.net_m.mean() if len(m6) else np.nan)
                # control rows
                opp = Tv[cell_mask(Tv, ph, L, b, "opp")]
                oth = Tv[(Tv.ph != ph) & (Tv[f"b{L}"] == b) & Tv.ok]
                unc = Tv[Tv.ok]
                r.update(ctl_opp_n=len(opp), ctl_opp_net=opp.net.mean() if len(opp) else np.nan,
                         ctl_otherph_n=len(oth), ctl_otherph_net=oth.net.mean() if len(oth) else np.nan,
                         ctl_uncond_n=len(unc), ctl_uncond_net=unc.net.mean() if len(unc) else np.nan)
            else:
                r.update(n=len(sub))
            rows.append(r)
    V = pd.DataFrame(rows)
    if len(V) and "p" in V:
        pv = V.p.fillna(1.0).to_numpy()
        V["bh_q"] = bh(pv)
        def verdict(r):
            if r.get("n", 0) < MIN_N:
                return "UNDERPOWERED"
            ok = (r.net > 0 and r.ci_lo > 0 and r.ex5 > 0 and r.placebo_p < 0.05 and r.bh_q < 0.10)
            return "PASS" if ok else "FAIL"
        V["verdict"] = V.apply(verdict, axis=1)
    V.to_csv(os.path.join(HERE, "val_kept_cells.csv"), index=False)
    # regime mix and sanity windows
    ld = lab[lab.phase_id.notna()]
    mix = {}
    for name, m in (("DEV", ld.index < S.SPLIT_DAY), ("VAL", ld.index >= S.SPLIT_DAY)):
        m = np.asarray(m)
        mix[name] = {PH.PHASES[int(k)]: round(float(x), 3) for k, x in ld[m].phase_id.value_counts(normalize=True).items()}
        mix[name + "_M"] = {k: round(float(x), 3) for k, x in ld[m].M.value_counts(normalize=True).items()}
        mix[name + "_days"] = int(m.sum())
    out["mix"] = mix
    # lab.index is day number: convert for windows
    lab2 = PH.phase_daily()
    win = {}
    for nm, (a, b2, exp) in {"CAP 2020-03-12..15": ("2020-03-12", "2020-03-15", 1), "CAP 2022-06-13..18": ("2022-06-13", "2022-06-18", 1),
                             "MARKDOWN 2022-01..10": ("2022-01-01", "2022-10-31", 2), "MARKDOWN 2025-11..2026-02": ("2025-11-01", "2026-02-28", 2),
                             "MARKUP 2020-11..2021-03": ("2020-11-01", "2021-03-31", 5), "MARKUP 2023-10..2024-03": ("2023-10-01", "2024-03-31", 5)}.items():
        w = lab2.loc[a:b2].phase_id
        win[nm] = dict(expected=PH.PHASES[exp], share_expected=round(float((w == exp).mean()), 3),
                       mix={PH.PHASES[int(k)]: round(float(x), 3) for k, x in w.value_counts(normalize=True).items()})
    out["sanity_windows"] = win
    ha = lab2.groupby("phase").halving_age_d.median().dropna().round(0).to_dict()
    out["halving_age_median_by_phase"] = ha
    out["now"] = lab2.iloc[-1][["phase", "phase_id", "pos40", "M", "rsi", "dd", "r10", "s50"]].astype(str).to_dict()
    out["now_date"] = str(lab2.index[-1].date())
    # trades by phase share
    out["trade_phase_share"] = {v: {PH.PHASES[int(k)]: int(x) for k, x in Tg[Tg.variant == v].ph.value_counts().items()} for v in S.VARIANTS}
    out["fund_missing_coins"] = [s for s, m in meta.items() if not m["funding"]]
    out["ctx_first_avail"] = {s: {k: (pd.to_datetime(x, unit="ms").strftime("%Y-%m-%d") if x else None) for k, x in m["first"].items()} for s, m in meta.items()}
    json.dump(out, open(os.path.join(HERE, "summary.json"), "w"), indent=1, default=str)
    return A, V, out


def main():
    mode = sys.argv[2] if len(sys.argv) > 2 else (sys.argv[1] if len(sys.argv) > 1 else "")
    if mode == "select":
        f = select()
        print(json.dumps(f["kept"], indent=1))
    elif mode == "val":
        fr = json.load(open(os.path.join(HERE, "cells_frozen.json")))
        A, V, out = val(fr)
        pd.set_option("display.width", 250, "display.max_columns", 50)
        print(A.round(3).to_string())
        print(V.round(3).to_string())
        print(json.dumps(out, indent=1, default=str)[:3000])


if __name__ == "__main__":
    main()
