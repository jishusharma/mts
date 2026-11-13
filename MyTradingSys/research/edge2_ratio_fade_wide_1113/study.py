"""Wave-2 ratio-fade confirmation (see PRE_REG.md). Writes results.csv, prints tables."""
import json, os, sys
import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(__file__))
import crowd as C  # noqa: E402

DATA = os.path.join(os.path.dirname(__file__), "..", "..", "..", "runtime_data", "edge2-ratio-fade-wide-1113")
HOLDS = [7, 3]
SPL = dict(C.SPLITS)
SPL["VAL+RECENT"] = ("2024-07-01", "2100-01-01")


def load():
    coins = {}
    for f in sorted(os.listdir(DATA)):
        if f.endswith("USDT.json"):
            d = json.load(open(os.path.join(DATA, f)))
            d["oi"] = [{"timestamp": "0", "openInterest": "1"}]  # OI unused by the ratio rule
            cd = C.build_coin(d)
            if cd is not None:
                coins[f[:-5]] = cd
    return coins


def stats(parts, tf="1d"):
    """parts: list of (cd, ents, sides, gross, fund, valid) already filtered. Returns dict."""
    v = np.concatenate([C.net(s, g[e], f[e]) for cd, e, s, g, f, va in parts]) if parts else np.array([])
    if len(v) == 0:
        return dict(n=0)
    w = np.concatenate([cd["t"][e] // (7 * C.DAY) for cd, e, s, g, f, va in parts])
    mean, lo, hi, p = C.cluster_boot(v, w)
    plc, pn = None, 0
    for cd, e, s, g, f, va in parts:
        pl = C.placebo_sums(cd, e, s, g, f, va, tf)
        if pl is not None:
            plc = pl[0] if plc is None else plc + pl[0]
            pn += pl[1]
    pm = plc / pn if pn else np.array([np.nan])
    return dict(n=len(v), mean_bp=mean * 1e4, lo_bp=lo * 1e4, hi_bp=hi * 1e4, p=p, win=float((v > 0).mean()),
                placebo_bp=float(np.mean(pm)) * 1e4, placebo_p95_bp=float(np.quantile(pm, 0.95)) * 1e4,
                beats_placebo=bool(mean > np.quantile(pm, 0.95)))


def main():
    coins = load()
    print("coins:", {k: (pd.to_datetime(v["t"][0], unit="ms").date().isoformat()) for k, v in coins.items()})
    print("n coins", len(coins))
    for sp, (a, b) in C.SPLITS.items():
        u = np.concatenate([(cd["ret3"][(cd["t"] >= C.ms(a)) & (cd["t"] < C.ms(b)) & ~np.isnan(cd["ret3"])] > 0) for cd in coins.values()])
        print(f"regime {sp}: share of 3d windows up = {u.mean():.3f} (n={len(u)})")
    sel = {hd: {k: C.select_trades(cd, "b", "1d", hd) for k, cd in coins.items()} for hd in HOLDS}
    rows = []
    for hd in HOLDS:
        for sp, (a, b) in SPL.items():
            for side in ("both", "long", "short"):
                parts = []
                for k, cd in coins.items():
                    ents, sides, g, f, va = sel[hd][k]
                    if len(ents) == 0:
                        continue
                    m = (cd["t"][ents] >= C.ms(a)) & (cd["t"][ents] < C.ms(b))
                    if side == "long":
                        m &= sides > 0
                    if side == "short":
                        m &= sides < 0
                    if m.any():
                        parts.append((cd, ents[m], sides[m], g, f, va))
                rows.append(dict(hold=hd, split=sp, side=side, **stats(parts)))
        # per calendar year, both sides
        for y in range(2020, 2027):
            parts = []
            for k, cd in coins.items():
                ents, sides, g, f, va = sel[hd][k]
                if len(ents) == 0:
                    continue
                m = (cd["t"][ents] >= C.ms(f"{y}-01-01")) & (cd["t"][ents] < C.ms(f"{y+1}-01-01"))
                if m.any():
                    parts.append((cd, ents[m], sides[m], g, f, va))
            rows.append(dict(hold=hd, split=f"Y{y}", side="both", **stats(parts)))
    df = pd.DataFrame(rows)
    # BH over the two VALIDATION both-sides cells
    v = df[(df.split == "VALIDATION") & (df.side == "both")].copy()
    p = v["p"].fillna(1.0).values
    order = np.argsort(p); m = len(p)
    ok = p[order] <= 0.10 * np.arange(1, m + 1) / m
    k = np.max(np.nonzero(ok)[0]) + 1 if ok.any() else 0
    bh = np.zeros(m, bool); bh[order[:k]] = True
    v["bh10"] = bh
    df = df.merge(v[["hold", "split", "side", "bh10"]], on=["hold", "split", "side"], how="left")
    df["pass"] = ((df.split == "VALIDATION") & (df.side == "both") & (df.n >= 30) & (df.mean_bp > 0) & (df.lo_bp > 0)
                  & df.beats_placebo.fillna(False) & df.bh10.fillna(False))
    df.round(3).to_csv(os.path.join(os.path.dirname(__file__), "results.csv"), index=False)
    pd.set_option("display.width", 250, "display.max_rows", 500)
    print(df.round(2).to_string(index=False))
    print("PASS cells:", int(df["pass"].sum()))


if __name__ == "__main__":
    main()
