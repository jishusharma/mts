"""NKN-06 driver: `python study.py run` computes every cell once and writes results.json and RESULT.md.
It refuses to run while any code file or PRE_REG.md of this folder has uncommitted changes (the code is committed before results exist).
All logic lives in nkn06_core.py (unit-tested on synthetic data); this file only loads data, assembles cells and writes the report."""
import sys, os, json, subprocess, datetime as dt, csv
from pathlib import Path
import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import nkn06_core as nc

REPO = nc.REPO
CACHE = Path(r"F:\MTS\data_cache")
SPOT = CACHE / "binance_spot"
BTC_DAILY_CSV = REPO / "MyTradingSys" / "research" / "btc_cycles_2026-11" / "btc_daily.csv"
PHASE_CSV = CACHE / "mts_brains" / "phase_daily.csv"
CODE_FILES = ["PRE_REG.md", "study.py", "nkn06_core.py", "test_study.py"]
COINS = "BTC ETH BNB XRP ADA DOGE SOL LTC LINK TRX DOT AVAX ATOM ETC BCH XLM UNI NEAR FIL ALGO".split()
RULE = "NKN-06"

# ---- the 15 cells (frozen design). src = which simulated set the cell reads
CELLS = [
    dict(id="P1", role="PRIMARY", side=1, trend=nc.UP, cyc=nc.MARKUP, var="V0", at="at level", tf="1h", src=("long", "cross", "1h", "normal"),
         phase="UP x MARKUP", ctx="R2 break leads to R3 (FzNDQm7wC_s 00:09:44) SOURCED idea; pivots, 1h, fresh cross, at-level <=1 ATR, 1.5R room, day-end exit OURS", layer="V0 rule alone", level="daily floor pivot R2 trigger, R3 target"),
    dict(id="P2", role="PRIMARY", side=-1, trend=nc.DOWN, cyc=nc.MARKDOWN, var="V0", at="at level", tf="1h", src=("short", "cross", "1h", "normal"),
         phase="DOWN x MARKDOWN", ctx="mirror of P1 (S2 to S3), mirror OURS", layer="V0 rule alone", level="daily floor pivot S2 trigger, S3 target"),
    dict(id="P3", role="PRIMARY", side=1, trend=nc.UP, cyc=nc.MARKUP, var="V0", at="at R3", tf="1d", src=("p3",),
         phase="UP x MARKUP (labels of the entry day)", ctx="three days sitting at R3 (a8RP5ftOfGo 00:13:56) SOURCED idea (count 3); 0.5% band, 5-day hold OURS", layer="V0 rule alone", level="daily floor pivot R3, three daily closes under it"),
    dict(id="C1", role="CONTROL", side=1, trend=nc.RANGE, cyc=nc.MARKUP, var="V0", at="at level", tf="1h", src=("long", "cross", "1h", "normal"), phase="RANGE x MARKUP", note="does the trend label add"),
    dict(id="C2", role="CONTROL", side=1, trend=nc.UP, cyc="not_markup", var="V0", at="at level", tf="1h", src=("long", "cross", "1h", "normal"), phase="UP x cycle not MARKUP", note="does the cycle label add"),
    dict(id="C3", role="CONTROL", side=1, trend=nc.DOWN, cyc=nc.MARKDOWN, var="V0", at="at level", tf="1h", src=("long", "cross", "1h", "normal"), phase="DOWN x MARKDOWN, long (mismatched side)", note="mismatch, descriptive"),
    dict(id="C4", role="CONTROL", side=1, trend=nc.UP, cyc=nc.MARKUP, var="V1", at="at level", tf="1h", src=("long", "cross", "1h", "normal"), phase="UP x MARKUP", note="Malkan BULL (daily)"),
    dict(id="C5", role="CONTROL", side=1, trend=nc.UP, cyc=nc.MARKUP, var="V1opp", at="at level", tf="1h", src=("long", "cross", "1h", "normal"), phase="UP x MARKUP", note="Malkan BEAR (layer adds?)"),
    dict(id="C6", role="CONTROL", side=1, trend=nc.UP, cyc=nc.MARKUP, var="V2", at="at level", tf="1h", src=("long", "cross", "1h", "normal"), phase="UP x MARKUP", note="Malkan BULL + 4h %B>=0.5"),
    dict(id="C7", role="CONTROL", side=1, trend=nc.UP, cyc=nc.MARKUP, var="V0", at="away from level", tf="1h", src=("long", "away", "1h", "normal"), phase="UP x MARKUP", note="level effect"),
    dict(id="C8", role="CONTROL", side=1, trend=nc.UP, cyc=nc.MARKUP, var="V0", at="at level", tf="15m", src=("long", "cross", "15m", "normal"), phase="UP x MARKUP", note="15m trigger"),
    dict(id="C9", role="CONTROL", side=1, trend=nc.UP, cyc=nc.MARKUP, var="V0", at="at level", tf="4h", src=("long", "cross", "4h", "normal"), phase="UP x MARKUP", note="4h trigger"),
    dict(id="C10", role="CONTROL", side=1, trend=nc.UP, cyc=nc.MARKUP, var="V0+BTC", at="at level", tf="1h", src=("long", "cross", "1h", "normal"), phase="UP x MARKUP", note="BTC daily close > SMA20 and SMA50"),
    dict(id="C11", role="CONTROL", side=1, trend=nc.UP, cyc=nc.MARKUP, var="V0", at="at level", tf="1h", src=("long", "cross", "1h", "close"), phase="UP x MARKUP", note="close-based exit: 1h close back under R2"),
]
TOTAL_CELLS = 15  # 3 primary + 11 controls + 1 placebo (C12)
PRIMARY = ["P1", "P2", "P3"]
SRC_KEYS = sorted({c["src"] for c in CELLS})


def git(*a):
    return subprocess.run(["git", "-C", str(REPO), *a], capture_output=True, text=True).stdout.strip()


def code_dirty():
    rel = [str((HERE / f).relative_to(REPO)).replace("\\", "/") for f in CODE_FILES]
    return git("status", "--porcelain", "--", *rel)


def btc_cycle_and_filter(btc15):
    """BTC daily (btc_daily.csv through 2026-11-06, then complete UTC days from the cached Binance 15m) -> cycle label for day D (lag 1) and the BTC filter for day D (lag 1)."""
    d, h, l, c = [], [], [], []
    for r in csv.DictReader(open(BTC_DAILY_CSV)):
        d.append(dt.date.fromisoformat(r["date"]).toordinal() - 719163)
        h.append(float(r["high"])); l.append(float(r["low"])); c.append(float(r["close"]))
    d, h, l, c = map(np.array, (d, h, l, c))
    bd = nc.resample(btc15["t"], btc15["o"], btc15["h"], btc15["l"], btc15["c"], btc15["v"], 96)
    dn = bd["t"] // nc.DAY
    last_csv = int(d[-1])
    add = dn > last_csv
    d, h, l, c = (np.r_[d, dn[add]], np.r_[h, bd["h"][add]], np.r_[l, bd["l"][add]], np.r_[c, bd["c"][add]])
    cyc_days, cyc_lab = nc.cycle_labels_from_daily(d, h, l, c)
    # BTC filter from the cached-15m daily series (one source): close > SMA20 and SMA50 at the day's close, applies to the next day
    cb = bd["c"]
    cs = np.cumsum(np.r_[0, cb])
    s20, s50 = np.full(len(cb), np.nan), np.full(len(cb), np.nan)
    s20[19:] = (cs[20:] - cs[:-20]) / 20
    s50[49:] = (cs[50:] - cs[:-50]) / 50
    with np.errstate(invalid="ignore"):
        ok = ((cb > s20) & (cb > s50)).astype(np.int8)
    return cyc_days, cyc_lab, dn + 1, ok


def phase_csv_agreement(cyc_days, cyc_lab):
    """read-only informational: how many UTC days the shared phase_daily.csv (another builder) labels MARKUP/MARKDOWN differently from our own recomputation."""
    if not PHASE_CSV.exists():
        return None
    names = {"MARKDOWN": 2, "MARKUP": 5}
    other = {}
    with open(PHASE_CSV) as f:
        for r in csv.DictReader(f):
            if str(r.get("provisional", "False")).lower() == "true" or not r.get("label"):
                continue
            other[dt.date.fromisoformat(r["date"]).toordinal() - 719163] = r["label"]
    mine = dict(zip(cyc_days.tolist(), cyc_lab.tolist()))
    inv = {1: "CAPITULATION", 2: "MARKDOWN", 3: "RELIEF", 4: "ACCUM-RANGE", 5: "MARKUP", 6: "DISTRIBUTION"}
    both = [k for k in mine if k in other and mine[k] > 0]
    diff = sum(1 for k in both if inv[mine[k]] != other[k])
    return dict(days_compared=len(both), differing=diff)


def cell_mask(cell, R):
    """R: dict of arrays for the rows of the cell's src (all statuses). Phase cell x variant filter. Control-phase rows never match a primary cell (in_cell is exact)."""
    m = nc.in_cell(R["trend"], R["cycle"], cell["trend"], cell["cyc"])
    v = cell["var"]
    if v == "V1":
        m &= R["malk"] == nc.BULL
    elif v == "V1opp":
        m &= R["malk"] == nc.BEAR
    elif v == "V2":
        with np.errstate(invalid="ignore"):
            m &= (R["malk"] == nc.BULL) & (R["pb"] >= nc.PB_MIN)
    elif v == "V0+BTC":
        m &= R["btcf"] == 1
    return m


def to_arrays(rows):
    keys = ["coin", "t", "trend", "cycle", "malk", "pb", "btcf", "hour", "dist"]
    out = {k: np.array([r[k] for r in rows]) for k in keys}
    out["status"] = np.array([r["status"] for r in rows])
    ok = out["status"] == "ok"
    for k in ("g", "e", "x", "R"):
        out[k] = np.array([r[k] if r["status"] == "ok" else np.nan for r in rows], float)
    out["hit"] = np.array([bool(r.get("hit", False)) for r in rows])
    out["stacked"] = np.array([bool(r.get("stacked", False)) for r in rows])
    out["kind"] = np.array([r.get("kind", "") for r in rows])
    return out


def run():
    allow_dirty = "--allow-dirty" in sys.argv
    dirty = code_dirty()
    if dirty and not allow_dirty:
        sys.exit("REFUSED: uncommitted changes in the study folder:\n" + dirty)
    head, prereg_commit = git("rev-parse", "HEAD"), git("log", "-1", "--format=%H", "--", str((HERE / "PRE_REG.md").relative_to(REPO)).replace("\\", "/"))
    prov = {}
    data = {}
    for coin in COINS:
        p = SPOT / f"{coin}USDT_15m.npz"
        data[coin], prov[coin] = nc.load_15m(p)
        pv = prov[coin]
        print(f"{coin}: key={pv['key']} first={dt.datetime.fromtimestamp(pv['first'] / 1000, dt.timezone.utc):%Y-%m-%d %H:%M} last={dt.datetime.fromtimestamp(pv['last'] / 1000, dt.timezone.utc):%Y-%m-%d %H:%M} n={pv['n']} gaps={pv['gaps']}", flush=True)
        assert pv["first"] < nc.SPLIT - 400 * nc.DAY and pv["last"] > nc.SPLIT + 400 * nc.DAY, f"{coin}: no history on both sides of 2024-01-01"
    cyc_days, cyc_lab, btc_days, btc_ok = btc_cycle_and_filter(data["BTC"])
    agree = phase_csv_agreement(cyc_days, cyc_lab)
    sets = {k: [] for k in SRC_KEYS}
    ev = {"long": [], "short": [], "p3": []}  # event study: same signals before the 1.5R room skip
    plc = {"P1": {"real": [], "cands": [], "hour": [], "dist": []}, "P2": {"real": [], "cands": []}, "P3": {"cands": []}}
    mix = {"DEV": dict(UP=0, DOWN=0, RANGE=0, P1cell=0, P2cell=0, known=0), "VAL": dict(UP=0, DOWN=0, RANGE=0, P1cell=0, P2cell=0, known=0)}
    for ci, coin in enumerate(COINS):
        d = data[coin]
        CB = nc.build_coin(d["t"], d["o"], d["h"], d["l"], d["c"], d["v"], cyc_days, cyc_lab, btc_days, btc_ok)
        # regime mix over coin-days (labels only)
        D = CB["dn"] + 1
        tr = CB["trend_close"]
        cy = nc.lookup(cyc_days, cyc_lab, D, 0)
        for nm, m in (("DEV", D * nc.DAY < nc.SPLIT), ("VAL", D * nc.DAY >= nc.SPLIT)):
            k = m & (tr != nc.UNK)
            mix[nm]["UP"] += int((k & (tr == nc.UP)).sum()); mix[nm]["DOWN"] += int((k & (tr == nc.DOWN)).sum()); mix[nm]["RANGE"] += int((k & (tr == nc.RANGE)).sum())
            mix[nm]["known"] += int(k.sum())
            mix[nm]["P1cell"] += int((k & (tr == nc.UP) & (cy == nc.MARKUP)).sum()); mix[nm]["P2cell"] += int((k & (tr == nc.DOWN) & (cy == nc.MARKDOWN)).sum())
        ctx = {}
        for tf in ("15m", "1h", "4h"):
            ctx[tf] = nc.tf_ctx(CB, tf)
        for key in SRC_KEYS:
            if key == ("p3",):
                rows = nc.p3_rows(CB)
            else:
                side, mode, tf, ex = key
                rows = nc.sim_signals(ctx[tf], 1 if side == "long" else -1, mode, True, ex)
            for r in rows:
                r["coin"] = ci
            sets[key].extend(rows)
        for name, d_ in (("long", 1), ("short", -1)):
            rows = nc.sim_signals(ctx["1h"], d_, "cross", False, "normal")
            for r in rows:
                r["coin"] = ci
            ev[name].extend(rows)
        rows = nc.p3_rows(CB, skip_room=False)
        for r in rows:
            r["coin"] = ci
        ev["p3"].extend(rows)
        # placebo candidate lists for the REAL validation trades of this coin (1h, same cell, side, hour, +-0.3 ATR distance)
        for cid, side, key, tr_, cyc_ in (("P1", 1, ("long", "cross", "1h", "normal"), nc.UP, nc.MARKUP), ("P2", -1, ("short", "cross", "1h", "normal"), nc.DOWN, nc.MARKDOWN)):
            rng = np.random.default_rng(1000 + 10 * ci + (1 if side > 0 else 2))
            for r in sets[key]:
                if r["coin"] == ci and r["status"] == "ok" and r["t"] >= nc.SPLIT and r["trend"] == tr_ and r["cycle"] == cyc_:
                    plc[cid]["real"].append(r["g"] - float(nc.fee_r(r["e"], r["x"], r["R"], 12.0)))
                    plc[cid]["cands"].append(nc.placebo_candidates(ctx["1h"], side, tr_, cyc_, r["hour"], r["dist"], rng))
        # P3 placebo: random daily entries, same coin, same cell (entry-day labels), VAL signal days, same exit and room rule (no distance match)
        rng = np.random.default_rng(5000 + ci)
        p3c = p3_candidates(CB, rng)
        plc["P3"]["cands"].append((ci, p3c))
        print(f"done {coin}", flush=True)
        del ctx
    res = analyse(sets, ev, plc, mix, prov, agree, head, prereg_commit)
    (HERE / "results.json").write_text(json.dumps(res, indent=1, default=float), encoding="utf-8")
    (HERE / "RESULT.md").write_text(make_result(res), encoding="utf-8")
    print("verdict", res["verdict"], flush=True)


def p3_candidates(CB, rng, kmax=60):
    """net R at 12 bp of random daily entries in the cell UP x MARKUP (entry-day labels), VAL signal days, same stop / target (that day's R3) / 5-day exit / room rule. A real P3 needs no distance match
    because the level is part of the signal; here the matching is the cell, the coin and the same exit logic only (stated in PRE_REG)."""
    Bd = CB["B"]["1d"]
    dn, o, h, l, c = CB["dn"], Bd["o"], Bd["h"], Bd["l"], Bd["c"]
    n = len(dn)
    out = []
    cand = []
    for j in range(2, n - nc.P3_HOLD - 1):
        if Bd["t"][j] < nc.SPLIT or dn[j] - dn[j - 1] != 1 or np.isnan(CB["atr_d"][j]):
            continue
        cyc = int(nc.lookup(CB["cyc_days"], CB["cyc_lab"], np.array([dn[j] + 1]), 0)[0])
        if CB["trend_close"][j] == nc.UP and cyc == nc.MARKUP:
            cand.append(j)
    if len(cand) > kmax:
        cand = list(rng.choice(cand, kmax, replace=False))
    for j in cand:
        pr = j - 1
        R3 = h[pr] + 2 * ((h[pr] + l[pr] + c[pr]) / 3.0 - l[pr])
        k0, k1 = j + 1, j + nc.P3_HOLD
        if dn[k0] != dn[j] + 1 or dn[k1] - dn[k0] != nc.P3_HOLD - 1:
            continue
        e = o[k0]
        R = max(nc.MIN_PCT * e, nc.MIN_ATR * CB["atr_d"][j])
        if (R3 - e) < nc.ROOM_MULT * R:
            continue
        x, xi, kind = nc.walk(o, h, l, c, k0, k1, 1, e - R, R3)
        out.append(float((x - e) / R - nc.fee_r(e, x, R, 12.0)))
    return out


def analyse(sets, ev, plc, mix, prov, agree, head, prereg_commit):
    A = {k: to_arrays(v) if v else None for k, v in sets.items()}
    cells, prim_p = [], {}
    for cell in CELLS:
        R = A[cell["src"]]
        row = dict(id=cell["id"], role=cell["role"], phase=cell["phase"], layer=cell.get("layer", cell["var"]), level=cell.get("level", ""), tf=cell["tf"],
                   side="long" if cell["side"] > 0 else "short", at=cell["at"], note=cell.get("note", ""), ctx=cell.get("ctx", ""))
        if R is None:
            cells.append(dict(row, dev=dict(n=0), val=dict(n=0), skipped={})); continue
        m = cell_mask(cell, R)
        okm = m & (R["status"] == "ok")
        sd = {}
        for nm, isv in (("DEV", False), ("VAL", True)):
            sm = m & (nc.split_is_val(R["t"]) == isv)
            sd[nm] = {s: int((sm & (R["status"] == s)).sum()) for s in ("room", "no_entry", "busy")}
        dev = nc.cell_stats(R["g"][okm], R["e"][okm], R["x"][okm], R["R"][okm], R["t"][okm], "DEV", full=False)
        val = nc.cell_stats(R["g"][okm], R["e"][okm], R["x"][okm], R["R"][okm], R["t"][okm], "VAL")
        vm = okm & nc.split_is_val(R["t"])
        val["hit_rate"] = float(R["hit"][vm].mean()) if vm.any() else float("nan")
        val["time_share"] = float((R["kind"][vm] == "time").mean()) if vm.any() else float("nan")
        row.update(dev=dev, val=val, skipped=sd)
        if cell["id"] == "P1":
            st = R["stacked"][vm]
            nets = (R["g"] - nc.fee_r(R["e"], R["x"], R["R"], 12.0))[vm] if vm.any() else np.array([])
            row["descr_stacked"] = dict(stacked_n=int(st.sum()), stacked_net12=float(nets[st].mean()) if st.any() else None, clear_n=int((~st).sum()), clear_net12=float(nets[~st].mean()) if (~st).any() else None)
            hrs = R["hour"][vm]
            row["descr_hours"] = {int(h_): int((hrs == h_).sum()) for h_ in np.unique(hrs)} if vm.any() else {}
        cells.append(row)
    # placebo and BH for primaries
    byid = {c["id"]: c for c in cells}
    for pid in ("P1", "P2"):
        pl = nc.placebo_test(plc[pid]["real"], plc[pid]["cands"]) if plc[pid]["real"] else dict(matched=0, real_mean_matched=float("nan"), placebo_mean=float("nan"), p=1.0)
        byid[pid]["placebo"] = pl
    p3c = [v for _, v in plc["P3"]["cands"]]
    n3 = byid["P3"]["val"]["n"]
    # P3 placebo: pool the per-coin candidate nets; every real trade draws from the pool of its own coin
    R3 = A[("p3",)]
    if n3 >= 20 and R3 is not None:
        m3 = cell_mask(CELLS[2], R3) & (R3["status"] == "ok") & nc.split_is_val(R3["t"])
        cl = [plc["P3"]["cands"][int(ci)][1] for ci in R3["coin"][m3]]
        net = (R3["g"] - nc.fee_r(R3["e"], R3["x"], R3["R"], 12.0))[m3]
        byid["P3"]["placebo"] = nc.placebo_test(net, cl)
    else:
        byid["P3"]["placebo"] = dict(matched=0, real_mean_matched=float("nan"), placebo_mean=float("nan"), p=1.0, note="not run: n VAL < 20")
    ps = [byid[p]["val"].get("p_day", 1.0) if byid[p]["val"]["n"] >= 2 else 1.0 for p in PRIMARY]
    qs = nc.bh_q(np.array(ps))
    for p, pv, q in zip(PRIMARY, ps, qs):
        c = byid[p]
        c["p_day"], c["bh_q"] = float(pv), float(q)
        c["verdict"] = nc.cell_verdict(c["val"], c["placebo"]["p"], float(q)) if c["val"]["n"] > 0 else "UNDERPOWERED"
    # C12 placebo row (for P1) reported as its own cell
    cells.append(dict(id="C12", role="PLACEBO", phase="UP x MARKUP", layer="random entries, hour + R2-distance matched", level="same", tf="1h", side="long", at="-", note="gate, not an edge cell", dev=dict(n=0), val=dict(n=byid["P1"]["placebo"]["matched"]), placebo=byid["P1"]["placebo"], skipped={}))
    # event study (same signals, no 1.5R room skip), only the primary phase cells, descriptive
    evs = {}
    for name, key, tr_, cy_ in (("P1_event", "long", nc.UP, nc.MARKUP), ("P2_event", "short", nc.DOWN, nc.MARKDOWN), ("P3_event", "p3", nc.UP, nc.MARKUP)):
        if not ev[key]:
            evs[name] = None; continue
        E = to_arrays(ev[key])
        m = nc.in_cell(E["trend"], E["cycle"], tr_, cy_) & (E["status"] == "ok")
        evs[name] = dict(dev=nc.cell_stats(E["g"][m], E["e"][m], E["x"][m], E["R"][m], E["t"][m], "DEV", full=False), val=nc.cell_stats(E["g"][m], E["e"][m], E["x"][m], E["R"][m], E["t"][m], "VAL", full=False))
    prim_v = [byid[p]["verdict"] for p in PRIMARY]
    verdict = nc.overall_verdict(prim_v)
    k = lambda s: {kk: (round(v / s["known"], 4) if kk != "known" else v) for kk, v in s.items()}
    return dict(rule=RULE, verdict=verdict, primary_verdicts=dict(zip(PRIMARY, prim_v)), cells=cells, event_study=evs, regime_mix=dict(DEV=k(mix["DEV"]), VAL=k(mix["VAL"])),
                provenance={c: dict(v) for c, v in prov.items()}, phase_csv_check=agree, code_commit=head, prereg_commit=prereg_commit, total_cells=TOTAL_CELLS, primary_cells=3,
                universe=COINS)


def f(x, nd=3):
    return "n/a" if x is None or (isinstance(x, float) and np.isnan(x)) else f"{x:+.{nd}f}"


def make_result(res):
    byid = {c["id"]: c for c in res["cells"]}
    L = []
    prim = [byid[p] for p in PRIMARY]
    best = max((c for c in prim if c["val"]["n"] > 0), key=lambda c: c["val"]["net12"], default=None)
    head = f"**Verdict: {res['verdict']}. NKN-06 pivot R2/R3 (S2/S3), 3 primary cells, validation 2024-01-01 onward, fee-net at 12 bp taker. "
    head += "; ".join(f"{p} {byid[p]['verdict']} (n VAL {byid[p]['val']['n']}, net12 {f(byid[p]['val'].get('net12'))} R)" for p in PRIMARY) + ".**"
    L += [head, ""]
    mx = res["regime_mix"]
    L.append(f"Regime mix: coin-day trend phase DEV UP {mx['DEV']['UP']:.0%} / DOWN {mx['DEV']['DOWN']:.0%} / RANGE {mx['DEV']['RANGE']:.0%}; VAL UP {mx['VAL']['UP']:.0%} / DOWN {mx['VAL']['DOWN']:.0%} / RANGE {mx['VAL']['RANGE']:.0%}. "
             f"Primary phase cells as share of coin-days: P1 UP x MARKUP DEV {mx['DEV']['P1cell']:.1%}, VAL {mx['VAL']['P1cell']:.1%}; P2 DOWN x MARKDOWN DEV {mx['DEV']['P2cell']:.1%}, VAL {mx['VAL']['P2cell']:.1%} ({mx['DEV']['known']} DEV and {mx['VAL']['known']} VAL labelled coin-days, {len(res['universe'])} coins). "
             f"Flag: {'mixed (no single phase over 50%)' if max(mx['VAL']['UP'], mx['VAL']['DOWN'], mx['VAL']['RANGE']) <= 0.5 else 'one phase dominates VAL'}.")
    L += ["", f"Total cells tried: {res['total_cells']} (3 primary, 11 controls, 1 placebo C12). Primary cells: {res['primary_cells']}. Underpowered primary cells: {sum(1 for p in prim if p['verdict'] == 'UNDERPOWERED')}. "
          f"Code commit at run: `{res['code_commit']}`; PRE_REG last commit: `{res['prereg_commit']}`.", ""]
    L += ["## PRIMARY cells (validation, 12 bp taker is the verdict; 6 bp maker secondary)", ""]
    hdr = "| cell | phase tested | context conditions (SOURCED/OURS) | crypto translation | layer agreement | level type | timeframe | side | n DEV | n VAL | gross R | net R 12bp | net R 6bp | win % | trade CI low | day-cluster CI low | ex-best-5 | placebo p | BH q | verdict |"
    L += [hdr, "|" + "---|" * 20]
    crypto = "UTC 00:00 day pivots; no gap; closed bars only"
    for c in prim:
        v = c["val"]
        L.append(f"| {c['id']} | {c['phase']} | {c['ctx']} | {crypto} | {c['layer']} | {c['level']} | {c['tf']} | {c['side']} | {c['dev']['n']} | {v['n']} | {f(v.get('gross'))} | {f(v.get('net12'))} | {f(v.get('net6'))} | "
                 f"{('%.1f' % (100 * v['win'])) if v.get('win') == v.get('win') and 'win' in v else 'n/a'} | {f(v.get('trade_ci_low'))} | {f(v.get('day_ci_low'))} | {f(v.get('ex5'))} | {c['placebo']['p']:.3f} | {c['bh_q']:.3f} | {c['verdict']} |")
    L += ["", "Gates per primary cell (all needed for PASS): net12 > 0, trade CI low > 0, day-cluster CI low > 0, ex-best-5 days > 0, placebo p < 0.05, BH q <= 0.10 over the 3 primaries, n VAL >= 200 (100-199: numbers shown, cannot PASS; under 100: UNDERPOWERED).", ""]
    L += ["### Placebo and hit rate (primary cells)", "", "| cell | matched real trades | real mean net R (matched) | placebo mean net R | placebo p | R3/S3 hit rate | share time-exit | skipped by 1.5R room VAL | no entry in day VAL |", "|---|---|---|---|---|---|---|---|---|"]
    for c in prim:
        pl, v = c["placebo"], c["val"]
        L.append(f"| {c['id']} | {pl['matched']} | {f(pl['real_mean_matched'])} | {f(pl['placebo_mean'])} | {pl['p']:.3f} | {f(v.get('hit_rate'), 2) if v.get('hit_rate') is not None else 'n/a'} | {f(v.get('time_share'), 2) if v.get('time_share') is not None else 'n/a'} | {c['skipped']['VAL']['room']} | {c['skipped']['VAL']['no_entry']} |")
    L += ["", "'Beats placebo' and 'profitable' are separate: a cell can beat random entries (which lose about 0.2 R after fees) and still have net R below zero.", ""]
    L += ["## CONTROL cells (never pooled with primary; 15 cells in total beside any positive row)", ""]
    L += ["| cell | phase | layer / variant | at/away | tf | side | n DEV | n VAL | gross R | net R 12bp | net R 6bp | win % | trade CI low | day CI low | ex-best-5 | note |", "|" + "---|" * 16]
    for c in res["cells"]:
        if c["role"] != "CONTROL":
            continue
        v = c["val"]
        L.append(f"| {c['id']} | {c['phase']} | {c['layer']} | {c['at']} | {c['tf']} | {c['side']} | {c['dev']['n']} | {v['n']} | {f(v.get('gross'))} | {f(v.get('net12'))} | {f(v.get('net6'))} | {('%.1f' % (100 * v['win'])) if v['n'] else 'n/a'} | {f(v.get('trade_ci_low'))} | {f(v.get('day_ci_low'))} | {f(v.get('ex5'))} | {c['note']} |")
    c12 = byid["C12"]["placebo"]
    L += [f"| C12 | UP x MARKUP | placebo for P1 | - | 1h | long | - | {c12['matched']} matched | - | real {f(c12['real_mean_matched'])} vs placebo {f(c12['placebo_mean'])} | - | - | - | - | - | p {c12['p']:.3f} |", ""]
    pos = [c["id"] for c in res["cells"] if c["role"] == "CONTROL" and c["val"]["n"] > 0 and c["val"].get("net12", -1) > 0]
    L += [f"Controls with positive net R 12bp on VAL: {', '.join(pos) if pos else 'none'} (read against {res['total_cells']} cells tried; no control carries a verdict).", ""]
    L += ["## Event study (same signals before the 1.5R room skip; descriptive, cannot PASS)", "", "| set | n DEV | n VAL | gross R VAL | net R 12bp VAL |", "|---|---|---|---|---|"]
    for k, e in res["event_study"].items():
        if e:
            L.append(f"| {k} | {e['dev']['n']} | {e['val']['n']} | {f(e['val'].get('gross'))} | {f(e['val'].get('net12'))} |")
    p1 = byid["P1"]
    if "descr_stacked" in p1:
        ds = p1["descr_stacked"]
        L += ["", f"Descriptive P1 VAL columns (no filter): stacked overhead (weekly R1 or prior-week high between entry and R3) n {ds['stacked_n']} net12 {f(ds['stacked_net12']) if ds['stacked_net12'] is not None else 'n/a'}; clear n {ds['clear_n']} net12 {f(ds['clear_net12']) if ds['clear_net12'] is not None else 'n/a'}. Entry-hour counts: {p1['descr_hours']}."]
    L += ["", "## Skipped signals per cell (room rule, no entry in the day, busy)", "", "| cell | DEV room | DEV no entry | VAL room | VAL no entry | VAL busy |", "|---|---|---|---|---|---|"]
    for c in res["cells"]:
        if c.get("skipped"):
            s = c["skipped"]
            L.append(f"| {c['id']} | {s['DEV']['room']} | {s['DEV']['no_entry']} | {s['VAL']['room']} | {s['VAL']['no_entry']} | {s['VAL']['busy']} |")
    L += ["", "## Provenance (cache = F:/MTS/data_cache/binance_spot, 15m, read-only; all timeframes resampled from it)", "", "| coin | key | first bar (UTC) | last bar (UTC) | bars | gaps (steps > 15m) |", "|---|---|---|---|---|---|"]
    for coin, p in res["provenance"].items():
        fm = lambda ms: dt.datetime.fromtimestamp(ms / 1000, dt.timezone.utc).strftime("%Y-%m-%d %H:%M")
        L.append(f"| {coin} | {p['key']} | {fm(p['first'])} | {fm(p['last'])} | {p['n']} | {p['gaps']} |")
    L += ["", f"Loader asserts: key is `ts` or `t`, timestamps strictly increasing, every step a multiple of 15 minutes (gaps are counted, resampled bars are built from complete groups only, a bar group with a hole is dropped). BTC cycle labels recomputed from `btc_daily.csv` plus the cached 15m; informational comparison with the shared phase_daily.csv: {res['phase_csv_check']}.", ""]
    dev_file = HERE / "deviations.txt"
    L += ["## Deviations", "", dev_file.read_text(encoding="utf-8").strip() if dev_file.exists() else "None. The code ran once as committed.", ""]
    L += ["## Parameter labels", "", "SOURCED: R2 break leads to R3 (FzNDQm7wC_s 00:09:44), three days at R3 (a8RP5ftOfGo 00:13:56), zones not lines (FzNDQm7wC_s 00:04:44), close-based stop spirit (control C11 only), Malkan 40/60/20 (Malkan layer). "
          "OURS (one value each, no grid): classic floor pivots from the prior UTC day, 1h trigger, fresh cross first per day, 00:00 bar skipped, ATR14 simple mean, at-level cap 1.0 ATR, R floor max(0.5% of entry, 0.6 ATR14, entry minus level), room rule 1.5 R, day-end time exit, "
          "coin trend phase (SMA20 slope 5-day lag, ADX14 >= 20 with DI direction), cycle state thresholds (MTS_BRAINS_SPEC_1114), V1 daily Malkan timeframe, V2 %B 20/2 with threshold 0.50, P3 band 0.5% and 5-day hold, placebo +-0.3 ATR distance match. No parameter is NK's own.", ""]
    return "\n".join(L) + "\n"


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "run":
        run()
    else:
        print(__doc__)
