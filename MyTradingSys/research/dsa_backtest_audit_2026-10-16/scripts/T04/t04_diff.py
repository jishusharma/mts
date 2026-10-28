"""T04 steps 3-5: diff the twin variants against the shipped studies, classify, measure verdicts.
Run locally (needs F:/MTS/data, pandas and the shipped study.py, which is read only at this step).
Outputs out/diff_mal_bb_A1.csv, out/diff_wlow_pooled.csv, out/diff_wlow_RL.csv, out/t04_results.json."""
import sys
sys.dont_write_bytecode = True
import csv
import datetime as dt
import json
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
R = HERE.parents[2]
OUT = HERE / "out"
sys.path.insert(0, str(HERE))
import twin_common as TC
import twin_mal_bb as M
import twin_wlow as W

TOL = 0.001
T0 = TC.T0_MS
CLASSES = ("twin_bug", "spec_ambiguity", "shipped_bug", "residual")


def iso(ms):
    return dt.datetime.fromtimestamp(ms / 1000, dt.timezone.utc).strftime("%Y-%m-%d %H:%M")


def variant(name):
    """v0 = twin as first written (cumsum SMA, cooldown >= 60 min); v1 = + exact SMA; v2 = + cooldown > 60 min."""
    TC.SMA_EXACT = name != "v0"
    M.ROUND_TIES = name == "v3"
    return name in ("v2", "v3")


def compare(twin, ship):
    st = {}
    for k in set(twin) | set(ship):
        if k in twin and k not in ship:
            st[k] = "twin_only"
        elif k in ship and k not in twin:
            st[k] = "shipped_only"
        else:
            a, b = twin[k], ship[k]
            st[k] = "return_differs" if (a is not None and b is not None and abs(a - b) > TOL) else "matched"
    return st


def counts(st):
    c = {"matched": 0, "return_differs": 0, "twin_only": 0, "shipped_only": 0}
    for v in st.values():
        c[v] += 1
    return c


def classify(st0, st1, st2, why_sma, why_cd):
    cls = {}
    for k, s in st0.items():
        if s == "matched":
            continue
        if st1.get(k, "matched") == "matched":
            cls[k] = ("twin_bug", why_sma)
        elif st2.get(k, "matched") == "matched":
            cls[k] = ("spec_ambiguity", why_cd)
        else:
            cls[k] = ("residual", "unexplained")
    return cls


def write_diff(path, st0, cls, twinG, shipG):
    rows = []
    for k in sorted(st0):
        c, why = cls.get(k, ("", ""))
        rows.append(dict(key_ts_ms=k, key_utc=iso(k), status=st0[k], diff_class=c, cause=why,
                         twin_G="" if twinG.get(k) is None else "%.5f" % twinG[k],
                         shipped_G="" if shipG.get(k) is None else "%.5f" % shipG[k]))
    with open(path, "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0].keys()), lineterminator="\n")
        w.writeheader()
        w.writerows(rows)


def clean(r):
    return {k: (float(v) if isinstance(v, (int, float, np.floating, np.integer)) else v) for k, v in r.items()}


def main():
    res = {}
    sys.path.insert(0, str(R / "mal_bb_mid_engulf_2026-10-16"))
    import study as SM
    A = SM.K.load()
    st_m = SM.build(A)
    S = SM.sets(st_m)
    mdd_bh = SM.K.S.bh_mdd(A)
    with open(R / "mal_bb_mid_engulf_2026-10-16" / "ledger.csv") as fh:
        led = list(csv.DictReader(fh))
    ship_m = {int(r["engulf_bar_open_utc_ms"]): float(r["G_short_h60"]) for r in led}
    res["mal_ledger_rows"] = len(led)

    def sh_arm(idx):
        t = SM.tdec(idx)
        G = SM.K.net_cells(A, t, np.full(len(t), -1), (60,))[60]
        return t, G, (t + 1 + SM.K.DELAY) // SM.K.DAYMIN
    t1, G1, d1 = sh_arm(S["e1"])
    tc, Gc, dc = sh_arm(S["ctrl1"])
    res["mal_shipped"] = clean(SM.K.verdict_arm(G1, d1, Gc, dc, t1, mdd_bh))

    outs = {}
    for v in ("v0", "v1", "v2", "v3"):
        strict = variant(v)
        d, a1, ct, c = M.run(strict_cd=strict)
        outs[v] = dict(tw={r["sig_ts"] - 300000: r["G"] for r in a1}, counts=c, line=clean(M.summarise(a1, ct, d)))
    sts = {v: compare(outs[v]["tw"], ship_m) for v in outs}
    cls = classify(sts["v0"], sts["v1"], sts["v2"],
                   "cumulative-sum SMA drifts about 1e-9 over 2.6M bars and flips a mid < mid[-10] comparison (twin bug T1)",
                   "cooldown boundary: an event exactly 60 min after the kept one is kept by the twin (>=) and dropped by the shipped code (<=)")
    write_diff(OUT / "diff_mal_bb_A1.csv", sts["v0"], cls, outs["v0"]["tw"], ship_m)
    res["mal"] = {v: dict(counts=counts(sts[v]), pre_counts=outs[v]["counts"], line=outs[v]["line"]) for v in outs}
    res["mal"]["classes"] = {c: sum(1 for x in cls.values() if x[0] == c) for c in CLASSES}
    variant("v3")
    d, b5, f = M.build()
    sd = {}
    for nm, mine, theirs in (("falling", f["falling"], st_m["fall"]), ("touch", f["touch"], st_m["bounce"][0.0]),
                             ("htf", f["htf"], st_m["htf_on"]), ("engulf_a", f["eng"], st_m["eng"]["a"])):
        bad = np.nonzero(mine[40:] != theirs[40:])[0] + 40
        sd[nm] = dict(twin=int(mine.sum()), shipped=int(theirs.sum()), disagree_after_warmup=len(bad), bars=[int(x) for x in bad[:10]])
    res["mal_state"] = sd

    sys.path.remove(str(R / "mal_bb_mid_engulf_2026-10-16"))
    sys.path.insert(0, str(R / "opr_weekly_low_round_sweep_2026-10-16"))
    del sys.modules["study"]
    import study as SW
    Lw = SW.week_low_prior(A["L"])
    j, lvl, fam = SW.pooled(A, 0.001, Lw)
    Cw = SW.win(A["C"], j, SW.WINDOW + 1)
    r = SW.first_above(Cw, lvl)
    okw = ~np.isnan(Cw).any(1)
    rl = (r <= 5) & okw
    rlc = (r > 5) & okw

    def sh_arm2(mask, tt):
        t = np.asarray(tt[mask], np.int64)
        G = SW.K.net_cells(A, t, np.full(len(t), 1), (60,))[60]
        return t, G, (t + 1 + SW.K.DELAY) // SW.K.DAYMIN
    tr, Gr, dr = sh_arm2(rl, j + np.minimum(r, 5))
    tcc, Gcc, dcc = sh_arm2(rlc, j + 5)
    res["wl_shipped"] = clean(SW.K.verdict_arm(Gr, dr, Gcc, dcc, tr, mdd_bh))
    res["wl_shipped_arm_n"] = dict(rl=int(rl.sum()), ctrl=int(rlc.sum()), dropped_nan_window=int((~okw).sum()))
    brk_ts = T0 + j.astype(np.int64) * 60000
    idx_rl = np.nonzero(rl)[0]
    gg = SW.K.net_cells(A, (j + np.minimum(r, 5))[idx_rl], np.full(len(idx_rl), 1), (60,))[60]
    ship_rlG = {int(brk_ts[i]): float(g) for i, g in zip(idx_rl, gg)}
    with open(R / "opr_weekly_low_round_sweep_2026-10-16" / "ledger.csv") as fh:
        wled = list(csv.DictReader(fh))
    res["wl_ledger_rows"] = len(wled)
    ship_p = {int(x["first_break_bar_open_utc_ms"]): None for x in wled}
    wout = {}
    for v in ("v0", "v2"):
        strict = variant(v)
        dd, rls, ctls, c = W.run(strict_cd=strict)
        wout[v] = dict(rl=rls, ctl=ctls, counts=c, line=clean(W.summarise(rls, ctls, dd)))
    tw_p = {x["break_ts"]: None for x in wout["v0"]["rl"] + wout["v0"]["ctl"]}
    tw_p2 = {x["break_ts"]: None for x in wout["v2"]["rl"] + wout["v2"]["ctl"]}
    stp, stp2 = compare(tw_p, ship_p), compare(tw_p2, ship_p)
    why_cd = "cooldown boundary (>= vs > 60 min between kept events), same as MAL"
    clsp = {k: ("spec_ambiguity", why_cd) if stp2.get(k, "matched") == "matched" else ("residual", "unexplained")
            for k, s in stp.items() if s != "matched"}
    write_diff(OUT / "diff_wlow_pooled.csv", stp, clsp, tw_p, ship_p)
    lv_s = {int(brk_ts[i]): float(lvl[i]) for i in range(len(j))}
    lv_t = {x["break_ts"]: x["level"] for x in wout["v2"]["rl"] + wout["v2"]["ctl"]}
    res["wl_level_mismatch"] = [dict(ts=k, utc=iso(k), twin=lv_t[k], shipped=lv_s[k])
                                for k in lv_s if k in lv_t and abs(lv_s[k] - lv_t[k]) > 1e-6]
    res["wl"] = {}
    for v in ("v0", "v2"):
        tw_rl = {x["break_ts"]: x["G"] for x in wout[v]["rl"]}
        s_rl = compare(tw_rl, ship_rlG)
        cl = {}
        for k, s in s_rl.items():
            if s == "matched":
                continue
            if stp.get(k, "matched") != "matched":
                cl[k] = ("spec_ambiguity", why_cd + ": the break event exists in only one ledger")
            elif s == "return_differs":
                cl[k] = ("residual", "return differs")
            else:
                cl[k] = ("residual", "arm membership differs")
        if v == "v0":
            write_diff(OUT / "diff_wlow_RL.csv", s_rl, cl, tw_rl, ship_rlG)
        res["wl"][v] = dict(counts=counts(s_rl), pre_counts=wout[v]["counts"], line=wout[v]["line"],
                            classes={c: sum(1 for x in cl.values() if x[0] == c) for c in CLASSES}, ctrl_n=len(wout[v]["ctl"]))
    res["wl"]["pooled_counts_v0"] = counts(stp)
    res["wl"]["pooled_counts_v2"] = counts(stp2)
    res["wl"]["pooled_classes"] = {c: sum(1 for x in clsp.values() if x[0] == c) for c in CLASSES}
    json.dump(res, open(OUT / "t04_results.json", "w", newline="\n"), indent=1, default=float)
    print(json.dumps(res, indent=1, default=float))


if __name__ == "__main__":
    main()
