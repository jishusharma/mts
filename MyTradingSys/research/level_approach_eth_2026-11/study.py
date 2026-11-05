"""Level-approach replication (card ms-level-approach-eth-replicate): C15 on BTCUSDT, ETHUSDT and BTC+ETH pooled, DEV only.
PRE_REG.md is the spec; the C15 code (../level_approach_2026-10-30/level_approach.py) is reused by path, unchanged.

Run: python study.py --symbols BTCUSDT,ETHUSDT [--klines F:/MTS/data/tom_raw/klines]
Refuses to run unless PRE_REG.md ends with a FROZEN_UTC line; the loader refuses any end after 2024-07-01 and never opens a later
file. Output: sequences.csv, classes.csv, regime_mix_dev.txt, RESULT.md, sim_desk/results/ms-level-approach-eth-replicate.json
(aggregates only, no account data). Fee-free descriptive study: no cost is applied.
"""
import argparse
import importlib.util
import json
import subprocess
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
sys.path.insert(0, str(REPO))


def _load(name, rel):
    sp = importlib.util.spec_from_file_location(name, REPO / rel)
    m = importlib.util.module_from_spec(sp)
    sp.loader.exec_module(m)
    return m


la = _load("level_approach_c15", "MyTradingSys/research/level_approach_2026-10-30/level_approach.py")
CUTOFF_MS, MIN_N = la.CUTOFF_MS, la.MIN_N
DEV_START = "2022-01"                       # SOURCED project DEV start (C15 file set 2022-01..2024-06)
JUDGED = ("near_miss", "wick_back")         # OURS (C15): class known at the event bar
COMBO = ["rsi_ge50", "cvd12_pos", "above_dbb_mid"]
INVALIDATION = ("near_miss", "1m", 0, 0, 0)  # C15's named invalidation row
C15_EVENTS = 10822
SIM_ID = "level-approach-eth-replicate-2026-11-05"   # sim_desk ids end with the run date (card's ms-level-approach-eth-replicate)
SIM_JSON = REPO / "MyTradingSys/research/sim_desk/results" / (SIM_ID + ".json")


def agreement(cells, base, pooled_ci, pooled_base):
    """PRE_REG rule. cells: {(sym, half): (n, p)} for the 4 symbol x half cells; base: {sym: class x TF base rate};
    pooled_ci: (lo, hi) Wilson CI of the pooled row; pooled_base: pooled class x TF base rate."""
    if any(n < MIN_N for n, _ in cells.values()):
        return "UNDERPOWERED"
    signs = {np.sign(p - base[sym]) for (sym, _), (_, p) in cells.items()}
    if len(signs) != 1 or 0 in signs:
        return "DISAGREES"
    lo, hi = pooled_ci
    return "AGREES" if (pooled_base < lo or pooled_base > hi) else "DISAGREES"


def root_for(sym, base="F:/MTS/data/tom_raw/klines"):
    """ETH 1m files were moved to klines_eth on 2026-11-05 (duplicate open_time vs BTC); BTC stays in klines."""
    return Path(base + "_eth") if sym == "ETHUSDT" else Path(base)


def load_symbol(sym, root=None, end_ms=CUTOFF_MS):
    if end_ms > CUTOFF_MS:
        raise ValueError("end %d after DEV cutoff %d: VALIDATION/HOLDOUT not loadable here" % (end_ms, CUTOFF_MS))
    root = Path(root) if root is not None else root_for(sym)
    end_month = str(np.datetime64(int(end_ms), "ms").astype("datetime64[M]"))
    paths = []
    for p in sorted(root.glob(sym + "-1m-*.csv")):
        per = p.stem.split("-1m-")[1]
        if DEV_START <= per[:7] < end_month:
            paths.append(p)
    if not paths:
        raise SystemExit("no %s 1m files in %s for DEV" % (sym, root))
    return la.load_klines(paths, cutoff_ms=end_ms)


def features(ev):
    ev = ev[ev.above_bbmid >= 0]
    return ev.assign(rsi_ge50=(ev.rsi >= 50).astype(int), cvd12_pos=(ev.cvd12 > 0).astype(int), above_dbb_mid=ev.above_bbmid)


def stats(s):
    n = len(s)
    p = s.brk.mean() if n else np.nan
    lo, hi = la.wilson(p, n) if n else (np.nan, np.nan)
    a, b = s[s.half == "A"], s[s.half == "B"]
    return dict(n=n, p=p, ci_lo=lo, ci_hi=hi, nA=len(a), pA=a.brk.mean() if len(a) else np.nan, nB=len(b),
                pB=b.brk.mean() if len(b) else np.nan)


def scopes(ev_by_sym):
    import pandas as pd
    out = {s: features(e) for s, e in ev_by_sym.items()}
    out["POOL"] = pd.concat(list(out.values()), ignore_index=True)
    return out


def class_table(sc):
    rows = []
    for scope, ev in sc.items():
        for (cls, tf), g in ev.groupby(["cls", "tf"]):
            rows.append(dict(scope=scope, cls=cls, tf=tf, **stats(g)))
    return rows


def sequence_table(sc, syms):
    rows = []
    base = {s: {k: g.brk.mean() for k, g in e.groupby(["cls", "tf"])} for s, e in sc.items()}
    groups = {s: dict(iter(e.groupby(["cls", "tf"] + COMBO))) for s, e in sc.items()}
    keys = sorted(set().union(*[g.keys() for g in groups.values()]), key=lambda k: (k[0], k[1], k[2:]))
    for key in keys:
        cls, tf = key[0], key[1]
        row = dict(cls=cls, tf=tf, **dict(zip(COMBO, (int(x) for x in key[2:]))))
        for s in list(syms) + ["POOL"]:
            g = groups[s].get(key)
            st = stats(g) if g is not None else stats(sc[s].iloc[0:0])
            row.update({"%s_%s" % (s, k): v for k, v in st.items()})
            row["%s_base" % s] = base[s].get((cls, tf), np.nan)
        if cls in JUDGED:
            cells = {(s, h): (row["%s_n%s" % (s, h)], row["%s_p%s" % (s, h)]) for s in syms for h in "AB"}
            row["agreement"] = agreement(cells, {s: row["%s_base" % s] for s in syms},
                                         (row["POOL_ci_lo"], row["POOL_ci_hi"]), row["POOL_base"])
        else:
            row["agreement"] = "NOT_JUDGED"
        rows.append(row)
    return rows


def verdict(seq_rows):
    judged = [r for r in seq_rows if r["agreement"] != "NOT_JUDGED"]
    if any(r["agreement"] == "AGREES" for r in judged):
        return "REPLICATES"
    if any(r["agreement"] == "DISAGREES" for r in judged):
        return "DOES-NOT-REPLICATE"
    return "UNDERPOWERED"


def reproduction(ev_btc):
    """BTC futures here must equal C15 exactly (same folder and code): event count and n per kind x class x TF."""
    import pandas as pd
    base, _ = la.tables(ev_btc)
    shipped = pd.read_csv(REPO / "MyTradingSys/research/level_approach_2026-10-30/tables.csv")
    m = shipped.merge(base, on=["kind", "cls", "tf"], suffixes=("_c15", "_now"), how="outer")
    mism = int((m.n_c15 != m.n_now).sum())
    return dict(events=len(ev_btc), c15_events=C15_EVENTS, cells=len(m), n_mismatch=mism)


def regime_mix(syms):
    """Weekly regime mix of DEV per symbol and pooled, as bb_range_retest_eth_pool (research_kit.regime_tag on spot 1d)."""
    pool = _load("bb_pool_src", "MyTradingSys/research/bb_range_retest_eth_pool_2026-11/study.py")
    prev, rk = pool.prev, pool.rk
    per, allw = {}, []
    for s in syms:
        regime_at = prev.make_regime_at(*pool.spot_context(s, pool.DEV_END_MS))
        per[s] = [regime_at(t) for t in prev.week_starts(pool.DEV_START_MS, pool.DEV_END_MS)]
        allw += per[s]
    return [s + " " + rk.regime_mix_line(per[s]) for s in syms] + ["POOL " + rk.regime_mix_line(allw)]


def f3(x):
    return "-" if x != x else "%.3f" % x


def write_result(sha, syms, rep, cls_rows, seq_rows, mix, v):
    judged = [r for r in seq_rows if r["agreement"] != "NOT_JUDGED"]
    cnt = {k: sum(r["agreement"] == k for r in judged) for k in ("AGREES", "DISAGREES", "UNDERPOWERED")}
    hdr = "|cls|tf|rsi|cvd|bbmid|" + "|".join("%s n|p|A|B" % s[:3] for s in syms) + "|POOL n|p|ci|base|agreement|"
    sep = "|" + "---|" * (5 + 4 * len(syms) + 5)

    def line(r):
        cells = "|".join("%d|%s|%s|%s" % (r["%s_n" % s], f3(r["%s_p" % s]), f3(r["%s_pA" % s]), f3(r["%s_pB" % s])) for s in syms)
        return "|%s|%s|%d|%d|%d|%s|%d|%s|%s-%s|%s|%s|" % (r["cls"], r["tf"], r["rsi_ge50"], r["cvd12_pos"], r["above_dbb_mid"], cells,
                                                         r["POOL_n"], f3(r["POOL_p"]), f3(r["POOL_ci_lo"]), f3(r["POOL_ci_hi"]),
                                                         f3(r["POOL_base"]), r["agreement"])
    agree = [r for r in judged if r["agreement"] == "AGREES"]
    powered = [r for r in judged if r["agreement"] != "UNDERPOWERED"]
    inv = next((r for r in judged if (r["cls"], r["tf"], r["rsi_ge50"], r["cvd12_pos"], r["above_dbb_mid"]) == INVALIDATION), None)
    ctab = ["|scope|cls|tf|n|p|ci|nA|pA|nB|pB|", "|---|---|---|---|---|---|---|---|---|---|"]
    for r in sorted(cls_rows, key=lambda r: (r["cls"], r["tf"], r["scope"])):
        if r["cls"] in JUDGED:
            ctab.append("|%s|%s|%s|%d|%s|%s-%s|%d|%s|%d|%s|" % (r["scope"], r["cls"], r["tf"], r["n"], f3(r["p"]), f3(r["ci_lo"]),
                                                              f3(r["ci_hi"]), r["nA"], f3(r["pA"]), r["nB"], f3(r["pB"])))
    txt = [
        "# RESULT: level approach (C15) replicated on ETHUSDT and BTC+ETH pooled, DEV only, descriptive, fee-free", "",
        "Pre-reg `PRE_REG.md` sha256 %s. Data: %s USD-M futures 1m 2022-01..2024-06; VALIDATION and HOLDOUT not read. "
        "Card ms-level-approach-eth-replicate." % (sha, " + ".join(syms)), "",
        "**Verdict: %s.** %d near_miss / wick_back sequence rows judged: %d AGREE, %d DISAGREE, %d UNDERPOWERED (a cell under n 30). "
        "No edge claim; an agreeing row is a hypothesis for a fresh-window test." % (v, len(judged), cnt["AGREES"], cnt["DISAGREES"],
                                                                                   cnt["UNDERPOWERED"]), "",
        "Regime mix: " + mix[-1] + " (" + "; ".join(mix[:-1]) + ")", "",
        "## Reproduction check (BTC row first)",
        "BTC futures through the unchanged C15 code: %d events (C15 shipped %d); %d kind x class x TF cells compared with the shipped "
        "tables.csv, %d n mismatches." % (rep["events"], rep["c15_events"], rep["cells"], rep["n_mismatch"]), "",
        "## C15 invalidation row (named in advance)",
        "near_miss 1m, RSI<50, CVD12<=0, below daily BB mid: " + (
            "BTC n %d p %s (A %s / B %s); ETH n %d p %s (A %s / B %s); pooled n %d p %s vs pooled base %s; %s." % (
                inv["BTCUSDT_n"], f3(inv["BTCUSDT_p"]), f3(inv["BTCUSDT_pA"]), f3(inv["BTCUSDT_pB"]), inv["ETHUSDT_n"], f3(inv["ETHUSDT_p"]),
                f3(inv["ETHUSDT_pA"]), f3(inv["ETHUSDT_pB"]), inv["POOL_n"], f3(inv["POOL_p"]), f3(inv["POOL_base"]), inv["agreement"])
            if inv else "row absent"), "",
        "## Agreeing rows (all four symbol x half cells n >= 30, same sign vs each symbol's class base, pooled CI excludes pooled base)",
        hdr, sep] + ([line(r) for r in agree] or ["|none|"]) + [
        "", "## Powered rows that disagree", hdr, sep] + ([line(r) for r in powered if r["agreement"] == "DISAGREES"] or ["|none|"]) + [
        "", "## Class base rates (near_miss, wick_back; both level kinds pooled, features known)"] + ctab + [
        "", "## Read this first",
        "- Wilson CIs treat events as independent; 1m events cluster within days, so true CIs are wider.",
        "- 64 rows looked at, no multiplicity correction; p_above_level for the through classes is partly built in and is not judged.",
        "- Full per class x TF x sequence table for BTC, ETH and pooled (n, p, Wilson CI, halves A/B, base, agreement): `sequences.csv`; "
        "class tables: `classes.csv`.", ""]
    (HERE / "RESULT.md").write_text("\n".join(txt), encoding="utf-8", newline="\n")
    return cnt, agree, inv


def write_sim_json(v, cnt, agree, inv, rep, mix, syms):
    head = "%s: %d of %d judged rows agree across BTC, ETH and both halves; %d disagree, %d underpowered" % (
        v, cnt["AGREES"], sum(cnt.values()), cnt["DISAGREES"], cnt["UNDERPOWERED"])
    why = ["BTC futures reproduce C15: %d events, %d n mismatches over %d cells." % (rep["events"], rep["n_mismatch"], rep["cells"])]
    if inv:
        why.append("C15 invalidation row (near_miss 1m all false): BTC p %s, ETH p %s, pooled %s vs base %s, %s." % (
            f3(inv["BTCUSDT_p"]), f3(inv["ETHUSDT_p"]), f3(inv["POOL_p"]), f3(inv["POOL_base"]), inv["agreement"]))
    why += ["Agrees: %s %s rsi%d cvd%d bb%d pooled n %d p %s vs base %s." % (
        r["cls"], r["tf"], r["rsi_ge50"], r["cvd12_pos"], r["above_dbb_mid"], r["POOL_n"], f3(r["POOL_p"]), f3(r["POOL_base"]))
        for r in agree[:4]]
    doc = {
        "id": SIM_ID, "kind": "backtest", "family": "Level approach",
        "title": "Replication: level approach (C15) on BTCUSDT + ETHUSDT USD-M futures, near_miss / wick_back sequences",
        "provenance": "builder-export", "date": "2026-11-05",
        "what": [
            {"name": "Levels", "value_plain": "prior-day high and last lower high (10-day lower-low lookback)", "label": "SOURCED"},
            {"name": "Classes", "value_plain": "near_miss / wick_back judged; arm 0.1 %, 3 confirm closes, 12-bar forward (C15)",
             "label": "OURS"},
            {"name": "Agreement", "value_plain": "n >= 30 in BTC-A, BTC-B, ETH-A, ETH-B, same sign vs class base, pooled CI excludes base",
             "label": "OURS"},
            {"name": "Regime mix", "value_plain": mix[-1], "label": "SOURCED"}],
        "how": "C15 code reused unchanged per symbol; sequences pooled over level kinds; fee-free descriptive.",
        "window": "DEV 2022-01-01..2024-06-30 %s futures 1m; VALIDATION and HOLDOUT not read" % " + ".join(syms),
        "verdict": {"label": head, "tone": "good" if v == "REPLICATES" else "warn"},
        "why": why,
        "kpis": [{"label": "rows judged", "value": str(sum(cnt.values()))}, {"label": "agree", "value": str(cnt["AGREES"])},
                 {"label": "BTC events", "value": str(rep["events"])}],
        "examples": [{"kind": "none", "title": "Examples", "caption": "no trades: descriptive event tables (sequences.csv)"}],
        "parity": None,
        "source_files": ["MyTradingSys/research/level_approach_eth_2026-11/" + f for f in
                         ("RESULT.md", "sequences.csv", "classes.csv", "PRE_REG.md")],
        "commit": subprocess.run(["git", "-C", str(REPO), "rev-parse", "--short=9", "HEAD"], capture_output=True, text=True).stdout.strip(),
        "banner": {"state": "UNCLEAR", "tone": "", "verdict": head, "n": None, "net_r": None, "try_no": None, "breakeven_x": None,
                   "text": "NO TRADE COUNT · verdict as written: %s · n=? · net R after fees n/a · try n/a · fee break-even n/a" % head}}
    SIM_JSON.write_text(json.dumps(doc, indent=1) + "\n", encoding="utf-8", newline="\n")


def main():
    import pandas as pd
    ap = argparse.ArgumentParser()
    ap.add_argument("--symbols", default="BTCUSDT,ETHUSDT")
    ap.add_argument("--klines", default=None, help="override root for every symbol; default BTC klines, ETH klines_eth")
    a = ap.parse_args()
    sha = la.require_frozen(HERE / "PRE_REG.md")
    syms = a.symbols.split(",")
    ev = {}
    for s in syms:
        ev[s] = la.build_events(load_symbol(s, a.klines))
        print(s, "events", len(ev[s]), flush=True)
    rep = reproduction(ev["BTCUSDT"])
    if rep["events"] != C15_EVENTS or rep["n_mismatch"]:
        raise SystemExit("BTC reproduction failed: %r" % rep)
    sc = scopes(ev)
    cls_rows, seq_rows = class_table(sc), sequence_table(sc, syms)
    pd.DataFrame(seq_rows).to_csv(HERE / "sequences.csv", index=False, lineterminator="\n", float_format="%.4f")
    pd.DataFrame(cls_rows).to_csv(HERE / "classes.csv", index=False, lineterminator="\n", float_format="%.4f")
    mix = regime_mix(syms)
    (HERE / "regime_mix_dev.txt").write_text("\n".join(mix) + "\n", encoding="utf-8", newline="\n")
    v = verdict(seq_rows)
    cnt, agree, inv = write_result(sha, syms, rep, cls_rows, seq_rows, mix, v)
    write_sim_json(v, cnt, agree, inv, rep, mix, syms)
    print("pre_reg_sha256", sha, "\nverdict", v, cnt)


if __name__ == "__main__":
    main()
