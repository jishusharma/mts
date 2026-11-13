"""NY prior-session POC target on new coins. See PRE_REG.md (committed before any outcome).
python -I study5.py <npz_dir> <out_dir>"""
import sys, json, datetime as dt
from pathlib import Path
import numpy as np
sys.path.insert(0, str(Path(__file__).resolve().parent))
import parent_study as ps  # parent code, unchanged

NEW = ["BNBUSDT", "XRPUSDT", "DOGEUSDT", "ADAUSDT", "AVAXUSDT", "LINKUSDT", "LTCUSDT", "DOTUSDT", "TRXUSDT", "BCHUSDT"]
SEEN = ["BTCUSDT", "ETHUSDT", "SOLUSDT"]
MIN_TGT = 3 * ps.COST_RT          # 36 bp (3 x round-trip cost)
EDGE_BUF = 0.001                  # 0.1% beyond the re-entered value edge (stop B)
FIRST_ENTRY_BAR = 3 * ps.BLOCK - 1  # earliest possible entry: second block of a pair starting at block 1
N_BOOT, N_PLC, ALPHA = 5000, 2000, 0.05 / 8
SPLIT = ps.SPLIT_MS


def tgt_ok(side, entry, poc):
    return side * (poc - entry) / entry >= MIN_TGT


def stop_for(stype, side, ev, k):
    if stype == "A":
        ext = float(ev["H"][:k + 1].max()) if side == -1 else float(ev["L"][:k + 1].min())
        return ext * (1 + ps.BUF_FRAC) if side == -1 else ext * (1 - ps.BUF_FRAC)
    return ev["vah"] * (1 + EDGE_BUF) if side == -1 else ev["val"] * (1 - EDGE_BUF)


def gross_net(side, entry, ex, stop):
    risk = abs(stop - entry) / entry
    g = side * (ex - entry) / entry / risk
    return g, g - ps.COST_RT / risk


def setups(ev):
    """(ei, skipped_flag): ei None if no setup; skipped when POC < 36 bp away in the trade direction."""
    b = ps.find_setup(ev["inside"], True)
    if b is None:
        return None, False
    ei = (b + 1) * ps.BLOCK - 1
    entry = float(ev["C"][ei])
    return ei, (not tgt_ok(ev["side"], entry, ev["poc"]))


def trade(ev, ei, stype):
    H, L, C, side, poc = ev["H"], ev["L"], ev["C"], ev["side"], ev["poc"]
    entry = float(C[ei])
    stop = stop_for(stype, side, ev, ei)
    if abs(stop - entry) / entry < ps.MIN_STOP:
        return None
    ex, kind, reach, _ = ps.sim_trade(side, ei, poc, stop, H, L, C)
    g, n = gross_net(side, entry, ex, stop)
    rec = dict(sym=ev["sym"], date=ev["date"], ms=ev["ms"], side=side, balanced=ev["balanced"], stype=stype,
               G=g, R=n, kind=kind, reach=reach, rr=abs(poc - entry) / abs(stop - entry))
    cand = []
    for k in range(FIRST_ENTRY_BAR, len(C) - 1):
        if not (ev["val"] <= C[k] <= ev["vah"]) or not tgt_ok(side, float(C[k]), poc):
            continue
        st = stop_for(stype, side, ev, k)
        if abs(st - C[k]) / C[k] < ps.MIN_STOP:
            continue
        e2, _, _, _ = ps.sim_trade(side, k, poc, st, H, L, C)
        cand.append(gross_net(side, float(C[k]), e2, st)[1])
    rec["cand"] = np.array(cand)
    return rec


def trade_boot(R, rng):
    n = len(R)
    if n == 0:
        return float("nan"), float("nan")
    idx = rng.integers(0, n, size=(N_BOOT, n))
    m = R[idx].mean(axis=1)
    return float(np.percentile(m, 2.5)), float(np.percentile(m, 97.5))


def cell_stats(tr, rng):
    R = np.array([r["R"] for r in tr]); G = np.array([r["G"] for r in tr]); d = np.array([r["date"] for r in tr])
    n = len(R)
    row = dict(n=n, days=len(set(d.tolist())))
    if n == 0:
        return row
    row.update(reach_poc=100 * float(np.mean([r["reach"] for r in tr])), reach_stop=100 * float(np.mean([r["kind"] == "stop" for r in tr])),
               rr_med=float(np.median([r["rr"] for r in tr])), gross=float(G.mean()), net=float(R.mean()))
    row["t_lo"], row["t_hi"] = trade_boot(R, rng)
    _, row["d_lo"], row["d_hi"], row["p"] = ps.boot_mean_ci(d, R, rng)
    vc = [r["cand"] for r in tr if len(r["cand"])]
    if vc:
        pm = np.stack([rng.choice(c, size=N_PLC) for c in vc]).mean(axis=0)
        row.update(plc_mean=float(pm.mean()), plc_p95=float(np.percentile(pm, 95)), plc_p=float((pm >= R.mean()).mean()))
    else:
        row.update(plc_mean=float("nan"), plc_p95=float("nan"), plc_p=1.0)
    late = [r["R"] for r in tr if r["ms"] >= SPLIT]
    row["n_2024"] = len(late); row["net_2024"] = float(np.mean(late)) if late else float("nan")
    dev = [r["R"] for r in tr if r["ms"] < SPLIT]
    row["n_dev"] = len(dev); row["net_dev"] = float(np.mean(dev)) if dev else float("nan")
    yrs = {}
    for r in tr:
        yrs.setdefault(dt.datetime.fromtimestamp(r["ms"] / 1000, dt.timezone.utc).year, []).append(r["R"])
    row["years"] = {str(y): [len(v), float(np.mean(v))] for y, v in sorted(yrs.items())}
    byday = {}
    for r in tr:
        byday[r["date"]] = byday.get(r["date"], 0.0) + r["R"]
    tot = sum(byday.values()); top = sum(sorted(byday.values(), reverse=True)[:10])
    row["top10_share"] = top / tot if tot != 0 else float("nan")
    row["top10_sum"], row["total_sum"] = top, tot
    ok = dict(mean=row["net"] > 0, trade_ci=row["t_lo"] > 0, day_ci=row["d_lo"] > 0, size=(n >= 100 and row["days"] >= 60),
              placebo=bool(row["net"] > row["plc_p95"] and row["plc_p"] < ALPHA), bonf=row["p"] < ALPHA,
              slice2024=bool(row["net_2024"] > 0))
    row["checks"] = {k: bool(v) for k, v in ok.items()}
    row["verdict"] = "PASS" if all(ok.values()) else ("UNDERPOWERED" if (not ok["size"] and ok["mean"]) else "FAIL")
    return row


def run_set(syms, npz_dir):
    cover, trades = {}, []
    for sym in syms:
        ev, n_sess, bars, sess = ps.day_events(sym, npz_dir)
        t = bars[0]
        sk = su = 0
        for e in ev:
            ei, skipped = setups(e)
            if ei is None:
                continue
            su += 1
            if skipped:
                sk += 1
                continue
            for st in ("A", "B"):
                r = trade(e, ei, st)
                if r:
                    trades.append(r)
        cover[sym] = dict(first=dt.datetime.fromtimestamp(t[0] / 1000, dt.timezone.utc).date().isoformat(),
                          last=dt.datetime.fromtimestamp(t[-1] / 1000, dt.timezone.utc).date().isoformat(), bars=int(len(t)),
                          sessions_used=len(sess), sessions_with_prior=n_sess, open_outside=len(ev), setups=su, skipped_lt36bp=sk)
        print(sym, cover[sym], flush=True)
    return trades, cover


def cells_for(trades, rng):
    rows = []
    for st in ("A", "B"):
        for side in (1, -1):
            for reg in ("all", "balanced"):
                tr = [r for r in trades if r["stype"] == st and r["side"] == side and (reg == "all" or r["balanced"])]
                row = cell_stats(tr, rng)
                row.update(stop="extreme" if st == "A" else "edge", side="long" if side == 1 else "short", reg=reg)
                rows.append(row)
    return rows


def regime(npz_dir, trades):
    t, o, h, l, c, v = ps.load(npz_dir, "BTCUSDT")
    day = t // 86_400_000
    ud, first = np.unique(day, return_index=True)
    last = np.r_[first[1:], len(t)] - 1
    dcl = c[last]
    regs = {}
    for i in range(200, len(ud)):
        sma = dcl[i - 200:i].mean()
        regs[int(ud[i])] = "bull" if dcl[i - 1] > sma * 1.05 else ("bear" if dcl[i - 1] < sma * 0.95 else "range")

    def mix(lo_ms, hi_ms):
        labs = [lab for d_, lab in regs.items() if lo_ms <= d_ * 86_400_000 < hi_ms]
        n = max(len(labs), 1)
        return {k: round(100 * labs.count(k) / n, 1) for k in ("bull", "bear", "range")}
    out = dict(days=dict(DEV=mix(0, SPLIT), S2024=mix(SPLIT, 10 ** 15)), setups={})
    for nm, sel in (("DEV", lambda r: r["ms"] < SPLIT), ("S2024", lambda r: r["ms"] >= SPLIT)):
        tt = [r for r in trades if r["stype"] == "A" and sel(r)]
        labs = [regs.get(r["ms"] // 86_400_000, "n/a") for r in tt]
        n = max(len(labs), 1)
        m = {k: round(100 * labs.count(k) / n, 1) for k in ("bull", "bear", "range", "n/a")}
        m["balanced_share"] = round(100 * float(np.mean([r["balanced"] for r in tt])), 1) if tt else 0
        m["n"] = len(tt)
        out["setups"][nm] = m
    return out


def main(npz_dir, out_dir):
    rng = np.random.default_rng(20261113)
    out = Path(out_dir); out.mkdir(parents=True, exist_ok=True)
    res = {}
    for name, syms in (("new", NEW), ("seen", SEEN)):
        trades, cover = run_set([s for s in syms if (Path(npz_dir) / f"{s}_1m.npz").exists()], npz_dir)
        rows = cells_for(trades, rng)
        res[name] = dict(cover=cover, rows=rows, n_trades=len(trades))
        for r in rows:
            print(name, {k: v for k, v in r.items() if k not in ("years", "checks")}, flush=True)
        if name == "new":
            res["regime"] = regime(npz_dir, trades)
            res["per_coin_stopA"] = {}
            for s in NEW:
                tt = [r for r in trades if r["sym"] == s and r["stype"] == "A"]
                res["per_coin_stopA"][s] = dict(n=len(tt), reach=100 * float(np.mean([r["reach"] for r in tt])) if tt else None,
                                                net=float(np.mean([r["R"] for r in tt])) if tt else None)
    res["cost"] = dict(side=ps.COST_SIDE, rt=ps.COST_RT, min_tgt=MIN_TGT)
    (out / "results.json").write_text(json.dumps(res, indent=1, default=float), encoding="utf-8")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
