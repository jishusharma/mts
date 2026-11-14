"""Run the 24 pre-registered cells over DEV / VALIDATION / RECENT. Writes results.csv and prints a table."""
import json
import os
import sys

import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(__file__))
import crowd as C  # noqa: E402

DATA = os.path.join(os.path.dirname(__file__), "..", "..", "..", "runtime_data", "edge-crowding-reversal-1113")
SIGS = ["a", "b", "c", "d"]
TFS = ["4h", "1d"]
HOLDS = [1, 3, 7]


def bh(pvals, q=0.10):
    p = np.asarray(pvals, float)
    order = np.argsort(p)
    m = len(p)
    thr = q * (np.arange(1, m + 1) / m)
    ok = p[order] <= thr
    k = np.max(np.nonzero(ok)[0]) + 1 if ok.any() else 0
    out = np.zeros(m, bool)
    out[order[:k]] = True
    return out


def main():
    coins = {}
    for f in sorted(os.listdir(DATA)):
        if f.endswith("USDT.json"):
            cd = C.build_coin(json.load(open(os.path.join(DATA, f))))
            if cd is not None:
                coins[f[:-5]] = cd
    print("coins:", {k: (pd.to_datetime(v["t"][0], unit="ms").date().isoformat(), len(v["t"])) for k, v in coins.items()})
    # regime mix (price only): share of 3-day windows up, per split
    for sp, (a, b) in C.SPLITS.items():
        ups = []
        for cd in coins.values():
            m = (cd["t"] >= C.ms(a)) & (cd["t"] < C.ms(b)) & ~np.isnan(cd["ret3"])
            ups.append(cd["ret3"][m] > 0)
        u = np.concatenate(ups)
        print(f"regime {sp}: share of 3d windows up = {u.mean():.3f} (n={len(u)})")
    rows = []
    for sig in SIGS:
        for tf in TFS:
            for hd in HOLDS:
                per = {sp: dict(v=[], w=[], plc=None, pn=0) for sp in C.SPLITS}
                for name, cd in coins.items():
                    ents, sides, gross, fund, valid = C.select_trades(cd, sig, tf, hd)
                    if len(ents) == 0:
                        continue
                    for sp, (a, b) in C.SPLITS.items():
                        m = (cd["t"][ents] >= C.ms(a)) & (cd["t"][ents] < C.ms(b))
                        if not m.any():
                            continue
                        e, s = ents[m], sides[m]
                        per[sp]["v"].append(C.net(s, gross[e], fund[e]))
                        per[sp]["w"].append(cd["t"][e] // (7 * C.DAY))
                        pl = C.placebo_sums(cd, e, s, gross, fund, valid, tf)
                        if pl is not None:
                            per[sp]["plc"] = pl[0] if per[sp]["plc"] is None else per[sp]["plc"] + pl[0]
                            per[sp]["pn"] += pl[1]
                for sp in C.SPLITS:
                    d = per[sp]
                    v = np.concatenate(d["v"]) if d["v"] else np.array([])
                    w = np.concatenate(d["w"]) if d["w"] else np.array([])
                    if len(v) == 0:
                        rows.append(dict(sig=sig, tf=tf, hold=hd, split=sp, n=0))
                        continue
                    mean, lo, hi, p = C.cluster_boot(v, w)
                    pm = d["plc"] / d["pn"] if d["pn"] else np.array([np.nan])
                    rows.append(dict(sig=sig, tf=tf, hold=hd, split=sp, n=len(v), mean_bp=mean * 1e4, lo_bp=lo * 1e4,
                                     hi_bp=hi * 1e4, p=p, win=float((v > 0).mean()),
                                     placebo_bp=float(np.mean(pm)) * 1e4, placebo_p95_bp=float(np.quantile(pm, 0.95)) * 1e4,
                                     beats_placebo=bool(mean > np.quantile(pm, 0.95))))
    df = pd.DataFrame(rows)
    # BH over the VALIDATION cells (24, absent cells count with p=1)
    val = df[df.split == "VALIDATION"].copy()
    val["p"] = val["p"].fillna(1.0)
    val["bh10"] = bh(val["p"].values)
    df = df.merge(val[["sig", "tf", "hold", "bh10"]], on=["sig", "tf", "hold"], how="left")
    df["pass"] = ((df.split == "VALIDATION") & (df.n >= 30) & (df.mean_bp > 0) & (df.lo_bp > 0)
                  & df.beats_placebo.fillna(False) & df.bh10.fillna(False))
    out = os.path.join(os.path.dirname(__file__), "results.csv")
    df.round(3).to_csv(out, index=False)
    pd.set_option("display.width", 250, "display.max_rows", 500)
    print(df.round(2).to_string(index=False))
    print("PASS cells:", int(df["pass"].sum()))


if __name__ == "__main__":
    main()
