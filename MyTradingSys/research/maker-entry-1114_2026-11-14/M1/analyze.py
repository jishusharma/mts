"""M1 analysis of raw_run.json -> results.json (gates per PRE_REG). No parameters tuned."""
import os, sys, json
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import study as S
import maker_fill as MF

raw = json.load(open(os.path.join(HERE, "raw_run.json")))
rows = raw["rows"]
FEE_M = 0.0006


def per(sel):
    z = [r for r in rows if sel(r)]
    out = {}
    n = len(z)
    # taker baseline (original: next-open entry, 12bp, all signals)
    tg = np.array([r["tkr_gross"] for r in z]); tdf = np.array([r["tkr_df"] for r in z])
    t12 = tg - 0.0012 / tdf
    days = np.array([int(r["entry_ms"] // 86400000) for r in z])
    rng = np.random.default_rng(7)
    out["taker"] = dict(n=n, gross=float(tg.mean()), net12=float(t12.mean()), net6=float((tg - FEE_M / tdf).mean()),
                        win=float((t12 > 0).mean()),
                        ci_trade=MF._boot_mean_ci(t12, 10000, rng),
                        mix=[float(np.mean([r["phase"] == p for r in z])) for p in (1, -1, 0)])
    res = [dict(filled=r["filled"], net_R=r["net_R"], gross_R=r["gross_R"], fee_R=r["fee_R"], fill_ms=r["fill_ms"],
                signal_close_ms=r["signal_close_ms"]) for r in z]
    sm = MF.summarize(res)
    f = np.array([r["filled"] for r in z])
    out["maker"] = dict(sm)
    out["maker"]["ci_trade"] = list(sm["ci_trade"]); out["maker"]["ci_day"] = list(sm["ci_day"])
    out["maker"]["orig_gross_filled"] = float(tg[f].mean()) if f.any() else None
    out["maker"]["orig_gross_all"] = float(tg.mean())
    out["maker"]["adverse_selection_R"] = float(tg[f].mean() - tg.mean()) if f.any() else None   # filled minus all (orig model)
    out["maker"]["orig_net12_filled"] = float(t12[f].mean()) if f.any() else None
    out["maker"]["orig_net12_all"] = float(t12.mean())
    out["maker"]["mix_filled_UP_DOWN_RANGE"] = [float(np.mean([r["phase"] == p for r, ff in zip(z, f) if ff])) if f.any() else None for p in (1, -1, 0)]
    ex = {}
    for r in z:
        if r["filled"]:
            k = r["exit_type"]; ex[k] = ex.get(k, 0) + 1
    out["maker"]["exit_types"] = ex
    ms = {}
    for r in z:
        if not r["filled"]:
            ms[r["miss"]] = ms.get(r["miss"], 0) + 1
    out["maker"]["miss_reasons"] = ms
    return out


DEV = per(lambda r: not r["val"])
VAL = per(lambda r: r["val"])
# placebo (VAL): per symbol counts of real filled VAL trades, draws from per-symbol bank of filled placebo trials
cnt = {}
for r in rows:
    if r["val"] and r["filled"]:
        cnt[r["sym"]] = cnt.get(r["sym"], 0) + 1
nf = sum(cnt.values())
obs = VAL["maker"]["mean_net_R_filled"]
rng = np.random.default_rng(7)
B = 1000
sums = np.zeros(B)
for s, c in cnt.items():
    bank = np.array(raw["pbank"][s])
    if len(bank) < 20:
        raise SystemExit(f"placebo bank too thin for {s}: {len(bank)}")
    sums += bank[rng.integers(0, len(bank), (B, c))].sum(1)
draws = sums / nf
p = float((1 + (draws >= obs).sum()) / (B + 1))
bh_rej, bh_adj = MF.benjamini_hochberg([p] + [1.0] * 5)   # provisional: other 5 rows unknown here -> worst case p=1
g = MF.gates(VAL["maker"] | dict(ci_trade=tuple(VAL["maker"]["ci_trade"]), ci_day=tuple(VAL["maker"]["ci_day"])), p, bh_rej[0])
bank_stats = {s: dict(filled=len(raw["pbank"][s]), of=raw["pbank_n"][s]) for s in raw["pbank"]}
tot = np.array(raw["ph_mix"]); mixall = [float(x) for x in tot / tot.sum()]
out = dict(id="M1", row="NK2 1h SHORT-P limit at pivot P", dev=DEV, val=VAL, placebo=dict(p=p, draw_mean=float(draws.mean()),
           draw_q95=float(np.percentile(draws, 95)), observed=obs, n_filled=nf, bh_adj_provisional=bh_adj[0],
           bank=bank_stats, offsets_q10_50_90=raw["offs_q"], offsets_n=raw["offs_n"]),
           gates=g, regime_all_coin_days_VAL_UP_DOWN_RANGE=mixall, ticks=raw["ticks"])
json.dump(out, open(os.path.join(HERE, "results.json"), "w"), indent=1, default=float)
print(json.dumps(dict(dev=DEV, val=VAL, placebo=out["placebo"] | dict(bank=None), gates=g, mix=mixall), indent=1, default=float))
