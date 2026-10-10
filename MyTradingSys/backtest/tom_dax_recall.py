"""tom-dax-recall: does coded Tom fire where Tom traded his own DAX trades? (research/tom_transfer_2026-10-11/PROBE_PLAN.md H1)

Trades: read from the chart frames of his videos (F:/MTS/data/tom_videos/frames, taskbar clock + chart header + order
labels), not from the transcript (the transcript has e.g. "18,258" where the chart shows 24257). Tom trades FDAX;
the data is the Dukascopy cash-index CFD, so his futures prices are shifted by the fair-value basis
(DAX is a performance index: basis = price * r * days_to_expiry / 365, r = BASIS_R).

Rules declared before the run (2026-10-11):
- Entry instant: the minute within +-WIN_FIND min of his approximate chart time where the basis-adjusted CFD bar
  touches his entry (short: high >= E, long: low <= E), nearest to the approximate time; none -> NOT_IN_DATA.
- Snapshots: engine (archive mode, -Dmts.symbol=GER40) every minute from entry-30 to entry+5.
- ZONE HIT: some snapshot has a rank<=3 candidate on his side whose zone price is within TOL of his adjusted entry,
  TOL = max(his stop distance, 0.15 % of price). SIGNAL HIT: in addition the snapshot verdict is WATCH or
  SETUP_FORMING. Verdict twice: as coded (net_rr with the engine's BTC fee term) and DAX-fee (net_rr := gross_rr,
  FDAX fees are ~0.1 point per round turn).
- MISS-PROOF: zone hit but proof < 3 everywhere (order-flow proofs cannot fire on CFD data: data limit).
  MISS-RULE: no same-side candidate near his entry at any snapshot.
SENSITIVITY --anchor extreme (added AFTER the declared run, post-hoc, labelled as such in the report): the observed
  futures-CFD offset was ~200 points in Dec 2025/Jan 2026 (theory 100-120) while May/Jun matched theory, and the 06-02 spike
  sat outside +-60 min. Entry instant := minute of the CFD session extreme within +-90 min (short: max high, long: min low),
  entry := that extreme; Tom sells spike tops / buys the pullback low, so this anchors on the same bar shape.
  python MyTradingSys/backtest/tom_dax_recall.py [--raw F:/MTS/data/dax_archive] [--out <dir>] [--anchor extreme]
"""
import argparse
import datetime as dt
import json
import sys
from pathlib import Path
from zoneinfo import ZoneInfo

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import dax_engine  # noqa: E402
import verdict as V  # noqa: E402

BER = ZoneInfo("Europe/Berlin")
BASIS_R = 0.02
WIN_FIND = 60
TOL_PCT = 0.0015
EXPIRY = {"H6": dt.date(2026, 3, 20), "M6": dt.date(2026, 6, 19)}
FR = "F:/MTS/data/tom_videos/frames/"
# id, video, local date, approx local time, contract, side, entry, stop (None = not shown), target, evidence
TRADES = [
    ("T1", "n7ZSkjb7JXs", "2025-12-22", "07:25", "H6", "short", 24481, None, 24422, FR + "n7ZSkjb7JXs_0314.jpg (clock 22.12.2025 08:30; -3 @24481, TP 24422; SL already moved to 24485)"),
    ("T2", "k0zm5NYn0IQ", "2026-01-08", "08:35", "H6", "short", 25343, None, None, FR + "k0zm5NYn0IQ_0670.jpg (FDAXH6 5m, 08.01.2026 08:35, -1 @25343)"),
    ("T3", "ujedEcmvBMk", "2026-05-12", "10:05", "M6", "short", 24229, 24257, 24111, FR + "ujedEcmvBMk_0168.jpg (clock 12.05.2026; -2 @24229 SL 24257 TP 24111)"),
    ("T3b", "ujedEcmvBMk", "2026-05-12", "12:05", "M6", "short", 24216, 24236, 24111, FR + "ujedEcmvBMk_0330.jpg (re-entry -1 @24216 SL 24236 TP 24111)"),
    ("T4", "UOBgXV20yCM", "2026-05-18", "10:00", "M6", "long", 23887, 23857, 23962, FR + "UOBgXV20yCM_0300.jpg (FDAXM6 M5; clock 19.05.2026; 'yesterday ... Monday')"),
    ("T5", "T6hDJcHrVBM", "2026-05-19", "09:15", "M6", "short", 24690, 24753, 24184, FR + "T6hDJcHrVBM_0420.jpg (-3 @24690 SL 24753 TP2 24184; open spike on the 19th)"),
    ("T6", "zQTbdEweG3c", "2026-06-02", "11:30", "M6", "short", 25344, None, None, FR + "zQTbdEweG3c_0345.jpg + _0465 (FDAXM26 profiles 2026-06-02; -1 @25344)"),
]


def basis(price, day, contract):
    return price * BASIS_R * (EXPIRY[contract] - day).days / 365.0


def load_bars(raw, day):
    """1m CFD bars of the month file: {open_ms: (o, h, l, c)}."""
    f = Path(raw) / "klines" / f"GER40-1m-{day:%Y-%m}.csv"
    out = {}
    if f.exists():
        for ln in f.read_text(encoding="utf-8").splitlines():
            p = ln.split(",")
            out[int(p[0])] = tuple(float(x) for x in p[1:5])
    return out


def find_entry(bars, approx_utc, side, e_adj):
    best = None
    for k in range(-WIN_FIND, WIN_FIND + 1):
        t = approx_utc + dt.timedelta(minutes=k)
        b = bars.get(int(t.timestamp() * 1000))
        if not b:
            continue
        touch = b[1] >= e_adj if side == "short" else b[2] <= e_adj
        if touch and (best is None or abs(k) < abs(best[0])):
            best = (k, t)
    return best[1] if best else None


def find_extreme(bars, approx_utc, side, win=90):
    best = None
    for k in range(-win, win + 1):
        t = approx_utc + dt.timedelta(minutes=k)
        b = bars.get(int(t.timestamp() * 1000))
        if not b:
            continue
        v = b[1] if side == "short" else b[2]
        if best is None or (v > best[0] if side == "short" else v < best[0]):
            best = (v, t)
    return best


def verdicts(s):
    a = V.compute_verdict(s, V.proof_dir_of(s, fail_closed=True))["verdict"]
    s2 = json.loads(json.dumps(s))
    for c in s2.get("setup_candidates") or []:
        m = c.get("math") or {}
        m["net_rr"] = m.get("gross_rr", 0.0)
    b = V.compute_verdict(s2, V.proof_dir_of(s2, fail_closed=True))["verdict"]
    return a, b


def classify(snaps, side, e_adj, tol):
    zone, sig_coded, sig_dax, best = False, False, False, None
    for s in snaps:
        va, vb = verdicts(s)
        for c in (s.get("setup_candidates") or []):
            if int(c.get("rank") or 999) > 3 or str(c.get("direction")).lower() != side:
                continue
            zp = float((c.get("zone") or {}).get("price") or 0)
            if abs(zp - e_adj) <= tol:
                zone = True
                top = (s.get("setup_candidates") or [None])[0]
                is_top = top is c
                sig_coded |= is_top and va in ("WATCH", "SETUP_FORMING")
                sig_dax |= is_top and vb in ("WATCH", "SETUP_FORMING")
                pc = int((c.get("score") or {}).get("proof_count") or 0)
                if best is None or pc > best["proof"]:
                    best = dict(ts=s.get("timestamp_utc"), zone=(c.get("zone") or {}).get("name"), zone_price=zp,
                                proof=pc, rank=c.get("rank"), gross_rr=(c.get("math") or {}).get("gross_rr"),
                                net_rr=(c.get("math") or {}).get("net_rr"), verdict_coded=va, verdict_daxfee=vb)
    if not zone:
        cls = "MISS-RULE"
    elif sig_dax or sig_coded:
        cls = "HIT"
    else:
        cls = "MISS-PROOF" if best and best["proof"] < 3 else "MISS-GATE"
    return cls, zone, sig_coded, sig_dax, best


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--raw", default="F:/MTS/data/dax_archive")
    ap.add_argument("--out", default="F:/MTS/data/dax_recall")
    ap.add_argument("--anchor", choices=("declared", "extreme"), default="declared")
    x = ap.parse_args(argv)
    out = Path(x.out); out.mkdir(parents=True, exist_ok=True)
    plan, rows = [], []
    for tid, vid, d, hm, ctr, side, e, stop, tgt, ev in TRADES:
        day = dt.date.fromisoformat(d)
        approx = dt.datetime.combine(day, dt.time.fromisoformat(hm), BER).astimezone(dt.timezone.utc)
        e_adj = e - basis(e, day, ctr)
        tol = max(abs(e - stop) if stop else 0.0, TOL_PCT * e)
        if x.anchor == "extreme":
            ex = find_extreme(load_bars(x.raw, day), approx, side)
            t0, e_adj = (ex[1], ex[0]) if ex else (None, e_adj)
        else:
            t0 = find_entry(load_bars(x.raw, day), approx, side, e_adj)
        plan.append(dict(id=tid, video=vid, side=side, entry=e, entry_adj=round(e_adj, 1), tol=round(tol, 1),
                         approx_utc=approx.isoformat(), entry_utc=t0.isoformat() if t0 else None, evidence=ev,
                         stop=stop, target=tgt))
    inst = sorted({(dt.datetime.fromisoformat(p["entry_utc"]) + dt.timedelta(minutes=k)).strftime("%Y-%m-%dT%H:%M:%SZ")
                   for p in plan if p["entry_utc"] for k in range(-30, 6)})
    snapf = out / "snaps.jsonl"
    if inst:
        dax_engine.main(["snap", "--raw", x.raw, "--out", str(snapf), "--at", *inst])
    by_ts = {}
    if snapf.exists():
        for ln in snapf.read_text(encoding="utf-8").splitlines():
            s = json.loads(ln)
            by_ts[str(s.get("timestamp_utc"))[:16]] = s
    for p in plan:
        if not p["entry_utc"]:
            rows.append(dict(p, cls="NOT_IN_DATA")); continue
        t0 = dt.datetime.fromisoformat(p["entry_utc"])
        snaps = [by_ts[k] for k in ((t0 + dt.timedelta(minutes=m)).strftime("%Y-%m-%dT%H:%M") for m in range(-30, 6)) if k in by_ts]
        cls, zone, sc, sd, best = classify(snaps, p["side"], p["entry_adj"], p["tol"])
        rows.append(dict(p, cls=cls, n_snaps=len(snaps), zone_hit=zone, signal_coded=sc, signal_daxfee=sd, best=best))
    (out / "recall.json").write_text(json.dumps(rows, indent=1), encoding="utf-8", newline="\n")
    for r in rows:
        print(r["id"], r["side"], r.get("entry_utc"), r["cls"], r.get("n_snaps"), json.dumps(r.get("best"))[:220])


if __name__ == "__main__":
    main()
