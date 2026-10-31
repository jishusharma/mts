"""F4 runner (see PRE_REG.md). HOLDOUT 2025-07+ is dropped at load.
Usage: python run_f4.py <klines_dir_with_BTCUSDT-1h-YYYY-MM.csv> [out_md]
"""
import glob
import os
import sys

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "..", "phase_tag"))
sys.path.insert(0, os.path.join(HERE, "..", "f2"))
import f4lib as L  # noqa: E402
import harness  # noqa: E402

END_TS = int(pd.Timestamp("2025-07-01", tz="UTC").timestamp())
DRAWS = 2000
SEED = 41
H_SPLIT = 6


def load_1h(folder):
    fs = sorted(glob.glob(os.path.join(folder, "BTCUSDT-1h-*.csv")))
    fs = [f for f in fs if os.path.basename(f)[12:19] <= "2025-06"]
    d = pd.concat([pd.read_csv(f, header=None, usecols=[0, 1, 2, 3, 4, 5, 9]) for f in fs], ignore_index=True)
    d.columns = ["t", "o", "h", "l", "c", "v", "tbv"]
    t = d.t.to_numpy(np.int64)
    d["t"] = np.where(t > 10 ** 14, t // 10 ** 6, t // 1000)
    d = d[d.t < END_TS].drop_duplicates("t").sort_values("t").reset_index(drop=True)
    assert d.t.max() < END_TS
    return d


def strata_of(vol30, edges):
    return np.clip(np.searchsorted(edges, vol30, side="right") - 1, 0, 4)


def describe(name, h, R, pct, idx, months, base1, base2, p1):
    n = len(R)
    out = {"name": name, "h": h, "n": n}
    if n == 0:
        return out
    ci = L.month_bootstrap(R, months) if n > 1 else (np.nan, np.nan)
    half = n // 2
    out.update(mean=float(R.mean()), pct=float(pct.mean()), hit=float((R > 0).mean()), lo=ci[0], hi=ci[1],
               a=float(R[:half].mean()) if half else np.nan, b=float(R[half:].mean()),
               b1=float(base1.mean()), b2=float(base2.mean()), p1=p1, p2=L.p_greater(R.mean(), base2),
               sd=float(R.std()), need=harness.power_n(float(R.std()), 0.10) if R.std() > 0 else 0)
    return out


def main():
    folder = sys.argv[1]
    outp = sys.argv[2] if len(sys.argv) > 2 else os.path.join(HERE, "output.md")
    h1 = load_1h(folder)
    b = L.build_8h(h1)
    F = L.features(b)
    P = L.path_matrix(b)
    tab, valid = L.trade_tables(b, h1)
    bt = b.t.to_numpy()
    n8 = len(b)
    lines = [f"# F4 output (BTCUSDT spot 8h from 1h; {pd.Timestamp(int(bt[0]), unit='s')} .. {pd.Timestamp(int(bt[-1]), unit='s')}; {n8} bars, {int(valid.sum())} valid)", ""]
    vol = F.vol30.to_numpy()
    okv = valid & np.isfinite(vol)
    edges = np.quantile(vol[okv], [0, 0.2, 0.4, 0.6, 0.8])
    strata = np.where(np.isfinite(vol), strata_of(np.nan_to_num(vol), edges), 0)
    gate = valid & (F.pctb.to_numpy() < 0)
    ent_time = bt + L.BAR
    months = pd.to_datetime(ent_time, unit="s", utc=True).strftime("%Y-%m").to_numpy()

    rule_idx = np.flatnonzero(L.rule_events(F) & valid)
    q_idx = np.flatnonzero(gate & np.isfinite(F[list(L.SCAL_COLS)].to_numpy(float)).all(axis=1) & np.isfinite(P).all(axis=1))
    nb_cache = {int(s): L.analog_neighbours(F, P, valid, int(s)) for s in q_idx}
    lines.append(f"RULE raw events {len(rule_idx)}; ANALOG queries {len(q_idx)} (answered {sum(len(v) == L.K for v in nb_cache.values())})")
    lines.append("")

    sets = {}   # (name, h) -> dict(idx, side, R, pct)
    for h in L.HORIZONS:
        for nm, key, side in (("RULE-cont", "c", -1), ("RULE-fade", "f", 1)):
            r_all, p_all = tab[(key + "r", h)], tab[(key + "p", h)]
            ix = rule_idx[np.isfinite(r_all[rule_idx])]
            keep = L.non_overlap(ix, h)
            ix = ix[keep]
            sets[(nm, h)] = dict(idx=ix, side=np.full(len(ix), side), R=r_all[ix], pct=p_all[ix])
        ix_l, sd_l, R_l, P_l = [], [], [], []
        for s in q_idx:
            nb = nb_cache[int(s)]
            if len(nb) < L.K:
                continue
            mc = np.nanmean(tab[("cr", h)][nb])
            mf = np.nanmean(tab[("fr", h)][nb])
            if not np.isfinite(mc) and not np.isfinite(mf):
                continue
            mc, mf = (-np.inf if not np.isfinite(mc) else mc), (-np.inf if not np.isfinite(mf) else mf)
            if max(mc, mf) <= 0:
                continue
            k = "c" if mc >= mf else "f"
            r = tab[(k + "r", h)][s]
            if not np.isfinite(r):
                continue
            ix_l.append(int(s)); sd_l.append(-1 if k == "c" else 1); R_l.append(r); P_l.append(tab[(k + "p", h)][s])
        ix = np.array(ix_l, dtype=int)
        keep = L.non_overlap(ix, h)
        sets[("ANALOG", h)] = dict(idx=ix[keep], side=np.array(sd_l, dtype=int)[keep], R=np.array(R_l)[keep], pct=np.array(P_l)[keep])

    res = {}
    pct_p = {}
    p1_list, keys = [], []
    for (nm, h), S in sets.items():
        ix, R = S["idx"], S["R"]
        cnt = np.bincount(strata[ix], minlength=5) if len(ix) else np.zeros(5, dtype=int)
        draws = {}
        for tag, mask in (("b1", okv), ("b2", okv & gate)):
            if nm == "ANALOG":
                ns = np.bincount(strata[ix[S["side"] < 0]], minlength=5)
                nl = np.bincount(strata[ix[S["side"] > 0]], minlength=5)
                ds = L.draw_means(np.where(mask, tab[("cr", h)], np.nan), strata, ns, DRAWS, SEED) * ns.sum()
                dl = L.draw_means(np.where(mask, tab[("fr", h)], np.nan), strata, nl, DRAWS, SEED + 1) * nl.sum()
                draws[tag] = (ds + dl) / max(ns.sum() + nl.sum(), 1)
            else:
                key = "cr" if nm == "RULE-cont" else "fr"
                draws[tag] = L.draw_means(np.where(mask, tab[(key, h)], np.nan), strata, cnt, DRAWS, SEED)
        p1 = L.p_greater(R.mean(), draws["b1"]) if len(R) else 1.0
        if nm == "ANALOG":
            dsp = L.draw_means(np.where(okv, tab[("cp", h)], np.nan), strata, ns, DRAWS, SEED) * ns.sum()
            dlp = L.draw_means(np.where(okv, tab[("fp", h)], np.nan), strata, nl, DRAWS, SEED + 1) * nl.sum()
            dpct = (dsp + dlp) / max(ns.sum() + nl.sum(), 1)
        else:
            dpct = L.draw_means(np.where(okv, tab[(("cp" if nm == "RULE-cont" else "fp"), h)], np.nan), strata, cnt, DRAWS, SEED)
        pct_p[(nm, h)] = (float(dpct.mean()), L.p_greater(S["pct"].mean(), dpct) if len(R) else 1.0)
        res[(nm, h)] = (draws["b1"], draws["b2"], p1)
        keys.append((nm, h)); p1_list.append(p1)
    adj = L.holm(p1_list)
    lines.append("| set | h (bars) | n | hit | net R/trade | net %/trade | month-boot 95% CI | half A / B | B1 mean (p, Holm p) | B2 mean (p) | sd R | n for 0.10 R | POST-HOC net-% control mean (p) | verdict |")
    lines.append("|---|---|---|---|---|---|---|---|---|---|---|---|---|---|")
    ev_rows = ["set,h,entry_time,side,net_r,net_pct"]
    for i, (nm, h) in enumerate(keys):
        S = sets[(nm, h)]
        d = describe(nm, h, S["R"], S["pct"], S["idx"], months[S["idx"]], res[(nm, h)][0], res[(nm, h)][1], res[(nm, h)][2])
        if d["n"] == 0:
            lines.append(f"| {nm} | {h} | 0 | | | | | | | | | | NOT_DECIDABLE |")
            continue
        if d["n"] < 30:
            v = "NOT_DECIDABLE"
        elif d["mean"] > 0 and adj[i] < 0.05 and d["lo"] > 0 and d["a"] > 0 and d["b"] > 0:
            v = "PASS"
        elif d["hi"] < 0:
            v = "FAIL"
        else:
            v = "INCONCLUSIVE"
        d["v"] = v
        lines.append(f"| {nm} | {h} | {d['n']} | {d['hit']:.3f} | {d['mean']:+.3f} | {d['pct']:+.3f} | [{d['lo']:+.3f}, {d['hi']:+.3f}] | {d['a']:+.3f} / {d['b']:+.3f} | {d['b1']:+.3f} ({d['p1']:.3f}, {adj[i]:.3f}) | {d['b2']:+.3f} ({d['p2']:.3f}) | {d['sd']:.2f} | {d['need']} | {pct_p[(nm, h)][0]:+.3f} ({pct_p[(nm, h)][1]:.3f}) | {v} |")
        for j, s in enumerate(S["idx"]):
            ts = pd.Timestamp(int(ent_time[s]), unit="s", tz="UTC").strftime("%Y-%m-%dT%H:%M:%SZ")
            ev_rows.append(f"{nm},{h},{ts},{'long' if S['side'][j] > 0 else 'short'},{S['R'][j]:.6f},{S['pct'][j]:.6f}")
    with open(os.path.join(HERE, "events.csv"), "w", newline="\n") as f:
        f.write("\n".join(ev_rows) + "\n")

    # ---- splits (h = 6) ----
    tags = pd.read_csv(os.path.join(HERE, "..", "phase_tag", "tags.csv"))
    tags["date"] = pd.to_datetime(tags["date"]).dt.strftime("%Y-%m-%d")
    tags = tags.set_index("date")
    tags["cs"] = tags.cowen_side.astype(str) + "|" + tags.sma200_side.astype(str)
    lines += ["", "## Phase splits (h = 6, descriptive)", ""]
    rng = np.random.default_rng(SEED)
    rsidiv = pd.read_csv(os.path.join(HERE, "..", "p1b_rsi_feenet", "events_feenet.csv"), usecols=["time"])
    rd_t = np.sort(((pd.to_datetime(rsidiv.time, utc=True) - pd.Timestamp("1970-01-01", tz="UTC")) // pd.Timedelta(seconds=1)).to_numpy().astype(np.int64))
    h1b = h1[h1.t >= int(pd.Timestamp("2021-09-01", tz="UTC").timestamp())].reset_index(drop=True)
    import hseries
    hser = hseries.h_from_closes(h1b.t.to_numpy(np.int64), h1b.c.to_numpy(float))
    hmap = dict(zip(h1b.t.to_numpy(np.int64), hser))
    for nm in ("RULE-cont", "RULE-fade", "ANALOG"):
        S = sets[(nm, H_SPLIT)]
        ix, R = S["idx"], S["R"]
        if len(ix) < 10:
            lines.append(f"{nm}: n {len(ix)} < 10, no split")
            continue
        dates = pd.to_datetime(ent_time[ix], unit="s", utc=True).strftime("%Y-%m-%d")
        lines.append(f"### {nm} (n {len(ix)}, mean {R.mean():+.3f} R)")
        lines.append("")
        lines.append("| labelling | cell | n | mean net R | gap vs pooled |")
        lines.append("|---|---|---|---|---|")
        for lab_name, col in (("cowen|sma200", "cs"), ("wsma10_phase", "wsma10_phase"), ("dd_bin", "dd_bin"), ("cycle_year", "cycle_year")):
            lab = np.array([str(tags[col].get(d, "nan")) for d in dates])
            cells = sorted(set(lab) - {"nan"})
            for c in cells:
                m = lab == c
                lines.append(f"| {lab_name} | {c} | {int(m.sum())} | {R[m].mean():+.3f} | {R[m].mean() - R.mean():+.3f} |")
            if lab_name != "cycle_year":
                big = [c for c in cells if (lab == c).sum() >= 10]
                m = np.isin(lab, big)
                if len(big) >= 2 and m.sum() >= 20:
                    code = {c: i for i, c in enumerate(big)}
                    li = np.array([code[x] for x in lab[m]])
                    t = harness.shift_null_test(R[m], li, n_shifts=1000, rng=rng)
                    names = [big[j] for j in t["flagged"]]
                    lines.append(f"| {lab_name} | FAMILY-WISE | {int(m.sum())} | max gap {t['max_gap']:.3f} vs thr {t['threshold']:.3f}, p {t['p_global']:.3f} | flagged {names or 'none'} |")
        # layer splits, 2022+ only
        m22 = ent_time[ix] >= int(pd.Timestamp("2022-01-01", tz="UTC").timestamp())
        if m22.sum() >= 10:
            lines.append(f"| (layers, entries 2022+ only, n {int(m22.sum())}) | | | | |")
            ct = ent_time[ix]
            fired = np.array([bool(((rd_t > c - 86400) & (rd_t <= c)).any()) for c in ct])
            for nme, mm in (("RSI-DIV-MTF fired", fired), ("RSI-DIV-MTF not fired", ~fired)):
                k = mm & m22
                if k.any():
                    lines.append(f"| layer | {nme} | {int(k.sum())} | {R[k].mean():+.3f} | {R[k].mean() - R[m22].mean():+.3f} |")
            hv = np.array([hmap.get(int(c) - 3600, np.nan) for c in ct])
            for nme, mm in (("Hurst H<0.45", hv < 0.45), ("Hurst 0.45-0.55", (hv >= 0.45) & (hv <= 0.55)), ("Hurst H>0.55", hv > 0.55), ("Hurst NaN", ~np.isfinite(hv))):
                k = mm & m22
                if k.any():
                    lines.append(f"| layer | {nme} | {int(k.sum())} | {R[k].mean():+.3f} | {R[k].mean() - R[m22].mean():+.3f} |")
        lines.append("")
    with open(outp, "w", newline="\n") as f:
        f.write("\n".join(lines) + "\n")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
