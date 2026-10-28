"""Card tom-v2-recall-fire-rate: DESIGN recall + fire rate of the frozen family A fade encoding, then CHECK once.

Rules: tom_dax_recall.py docstring (V2 section) and TOM_LAYER_V2_SPEC.md sections 7, 14. No trade outcome is computed.
  python MyTradingSys/backtest/tom_v2_recall.py design [--raw F:/MTS/data/dax_archive] [--out F:/MTS/data/tom_v2_recall] [--shards 8]
  python MyTradingSys/backtest/tom_v2_recall.py check  [same]     # reads k* frozen in design_result.json, runs once
The replay is dax_engine.py `fade` (SpikeFadeDetector on a 40-calendar-day 1m series per minute, the series a flag-on
as-of snapshot hands the fade call). design writes design_result.json beside RECALL_DAX_V2.md and refuses to run
check before it exists; check refuses to run twice.
"""
import argparse
import datetime as dt
import json
import statistics
import sys
from collections import defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import dax_engine  # noqa: E402
import tom_dax_recall as R  # noqa: E402

DESIGN_IDS = ("T1", "T2", "T2b", "T3", "T3b", "T5", "T6")
CHECK_IDS = ("T11", "T12")
DEV_START, DEV_END = dt.date(2024, 11, 4), dt.date(2026, 4, 10)
RANK_GATES = (0.0, 0.8, 0.9)   # spec 13: fire rate also at impulse_rank 0.8 and 0.9, never chosen by outcome
N5_FLOOR = 0.88                # spec 11.3: Tom's narrowest stop in N5 units


def load_fires(path):
    by_date = defaultdict(list)
    for ln in Path(path).read_text(encoding="utf-8").splitlines():
        if ln.strip():
            r = json.loads(ln)
            by_date[dt.date.fromisoformat(r["date"])].append(r)
    for v in by_date.values():
        v.sort(key=lambda r: r["t"])
    return by_date


def run_replay(raw, days, out, shards):
    dates_file = Path(str(out) + ".dates.txt")
    dates_file.write_text("\n".join(sorted(d.isoformat() for d in set(days))) + "\n", encoding="utf-8", newline="\n")
    dax_engine.main(["fade", "--raw", str(raw), "--dates", str(dates_file), "--out", str(out), "--shards", str(shards)])


def recall_table(groups, fires, bars):
    """{k: {'groups': {gid: bool}, 'sessions': [..], 'n': {gid: candidate minutes}}} plus per-group detail."""
    table = {}
    for k in R.V2_PROOF_COUNTS:
        ghit, gn = {}, {}
        for g in groups:
            hit, n = False, 0
            for d in g["dates"]:
                cands = [(r["t"], r["zone"]) for r in fires.get(d, []) if r["proof_count"] >= k]
                n += len(cands)
                hit |= R.v2_group_hit(cands, g["entry_adj"][d], g["width"], bars.get(d, []))
            ghit[g["id"]], gn[g["id"]] = hit, n
        sess = sorted({g["session"] for g in groups if ghit[g["id"]]})
        table[k] = dict(groups=ghit, n=gn, sessions=sess)
    return table


def random_share(groups, table, bars, k, draws):
    gd = [(g["id"], g["session"], [(g["entry_adj"][d], g["width"], d) for d in g["dates"]]) for g in groups]
    rec = R.v2_random_recall(gd, table[k]["n"], bars, draws=draws)
    obs = len(table[k]["sessions"])
    return sum(1 for x in rec if x >= obs) / len(rec), statistics.mean(rec), max(rec)


def fire_rate(dev_days, fires):
    """Per k and rank gate: share of dev days with a first-attempt candidate, mean candidate minutes/day, N5 census."""
    out = {}
    for gate in RANK_GATES:
        for k in R.V2_PROOF_COUNTS:
            first, minutes, n5 = 0, 0, []
            for d in dev_days:
                c = [r for r in fires.get(d, []) if r["proof_count"] >= k and r["impulse_rank"] >= gate]
                minutes += len(c)
                if c:
                    first += 1
                    n5.append(c[0]["stop_n5"])
            known = [x for x in n5 if x is not None]
            out[f"rank>={gate}|k>={k}"] = dict(
                days=len(dev_days), first_attempt_days=first, per_session_day=round(first / len(dev_days), 4),
                candidate_minutes_per_day=round(minutes / len(dev_days), 3),
                stop_n5_n=len(known), stop_n5_median=round(statistics.median(known), 3) if known else None,
                stop_n5_share_below_0_88=round(sum(1 for x in known if x < N5_FLOOR) / len(known), 4) if known else None,
                stop_rule_s1=None)
    return out


def stop_rule_census(dev_days, fires):
    c = defaultdict(int)
    for d in dev_days:
        for r in fires.get(d, [])[:1]:
            c[r["stop_rule"]] += 1
    return dict(c)


def group_detail(groups, fires, bars):
    rows = []
    for g in groups:
        for d in g["dates"]:
            fs = fires.get(d, [])
            e, w = g["entry_adj"][d], g["width"]
            brk = R.v2_break_ms(bars.get(d, []), e, w)
            rows.append(dict(group=g["id"], session=g["session"], date=d.isoformat(), entry=g["entry"],
                             entry_adj=round(e, 1), width=w,
                             window_high=max((b[2] for b in bars.get(d, [])), default=None),
                             window_low=min((b[3] for b in bars.get(d, [])), default=None),
                             break_utc=(dt.datetime.fromtimestamp(brk / 1000, dt.timezone.utc).strftime("%H:%M") if brk else None),
                             fire_minutes=len(fs),
                             first_fire_utc=(dt.datetime.fromtimestamp(fs[0]["t"] / 1000, dt.timezone.utc).strftime("%H:%M") if fs else None),
                             zone_min=min((r["zone"] for r in fs), default=None),
                             zone_max=max((r["zone"] for r in fs), default=None),
                             max_proofs=max((r["proof_count"] for r in fs), default=None)))
    return rows


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("mode", choices=("design", "check"))
    ap.add_argument("--raw", default="F:/MTS/data/dax_archive")
    ap.add_argument("--out", default="F:/MTS/data/tom_v2_recall")
    ap.add_argument("--shards", type=int, default=8)
    ap.add_argument("--draws", type=int, default=R.V2_DRAWS)
    ap.add_argument("--reuse-fires", action="store_true", help="design: score the existing design_fires.jsonl, no replay")
    ap.add_argument("--report-dir", default=str(R.V2_DIR))
    x = ap.parse_args(argv)
    out, rep = Path(x.out), Path(x.report_dir)
    out.mkdir(parents=True, exist_ok=True)
    res_path = rep / "design_result.json"
    chk_path = rep / "check_result.json"

    if x.mode == "design":
        groups = R.v2_groups(groups=DESIGN_IDS)
        hc = json.loads((R.V2_DIR / "HOLDOUT_CLEAN.json").read_text(encoding="utf-8"))
        dropped = {dt.date.fromisoformat(d) for d in hc["dev_dropped_days"]}
        all_days = R.v2_all_window_days(x.raw, DEV_START, DEV_END)
        dev_days = [d for d in all_days if d not in dropped]
        design_days = sorted({d for g in groups for d in g["dates"]})
        fires_path = out / "design_fires.jsonl"
        if not (x.reuse_fires and fires_path.exists()):
            run_replay(x.raw, set(dev_days) | set(design_days), fires_path, x.shards)
        fires = load_fires(fires_path)
        bars = R.v2_window_bars(x.raw, design_days)
        table = recall_table(groups, fires, bars)
        shares = {}
        for k in R.V2_PROOF_COUNTS:
            shares[k] = random_share(groups, table, bars, k, x.draws)
        recall_by_k = {k: len(table[k]["sessions"]) for k in R.V2_PROOF_COUNTS}
        kstar, verdict = R.v2_verdict_design(recall_by_k, {k: shares[k][0] for k in R.V2_PROOF_COUNTS})
        result = dict(
            card="tom-v2-recall-fire-rate", encoding="SpikeFadeDetector PRICE arm (cc613a2)", date=dt.date.today().isoformat(),
            draws=x.draws, seed=R.V2_SEED, design_sessions=sorted({g["session"] for g in groups}),
            recall={str(k): dict(sessions_hit=recall_by_k[k], sessions=table[k]["sessions"], groups=table[k]["groups"],
                                 candidate_minutes=table[k]["n"], random_share_ge=round(shares[k][0], 4),
                                 random_mean=round(shares[k][1], 3), random_max=shares[k][2])
                    for k in R.V2_PROOF_COUNTS},
            k_star=kstar, design_verdict=verdict, group_detail=group_detail(groups, fires, bars),
            dev=dict(window=[DEV_START.isoformat(), DEV_END.isoformat()], dropped=len(dropped), days=len(dev_days),
                     fire_rate=fire_rate(dev_days, fires), first_attempt_stop_rule=stop_rule_census(dev_days, fires)))
        res_path.write_text(json.dumps(result, indent=1), encoding="utf-8", newline="\n")
        print(json.dumps({k: v for k, v in result.items() if k in ("recall", "k_star", "design_verdict")}, indent=1)[:3000])
        return result

    # check: once, after k* is frozen in design_result.json
    if not res_path.exists():
        raise SystemExit("design_result.json missing: run design first (k* must be frozen before CHECK is read)")
    if chk_path.exists():
        raise SystemExit("check_result.json exists: CHECK is read once (spec 14); a re-read is a new TRIAL_REGISTRY row and a new card")
    des = json.loads(res_path.read_text(encoding="utf-8"))
    kstar = des["k_star"]
    if kstar is None:
        raise SystemExit("no k* (DESIGN FAIL): the chain stops, CHECK is not read")
    groups = R.v2_groups(groups=CHECK_IDS)
    days = sorted({d for g in groups for d in g["dates"]})
    fires_path = out / "check_fires.jsonl"
    run_replay(x.raw, days, fires_path, x.shards)
    fires = load_fires(fires_path)
    bars = R.v2_window_bars(x.raw, days)
    table = recall_table(groups, fires, bars)
    hits = len(table[kstar]["sessions"])
    result = dict(card="tom-v2-recall-fire-rate", read="once", date=dt.date.today().isoformat(), k_star=kstar,
                  sessions_hit=hits, sessions=table[kstar]["sessions"], groups=table[kstar]["groups"],
                  verdict=R.v2_verdict_check(hits), by_k={str(k): dict(groups=table[k]["groups"], n=table[k]["n"])
                                                          for k in R.V2_PROOF_COUNTS},
                  group_detail=group_detail(groups, fires, bars))
    chk_path.write_text(json.dumps(result, indent=1), encoding="utf-8", newline="\n")
    print(json.dumps({k: v for k, v in result.items() if k != "group_detail"}, indent=1))
    return result


if __name__ == "__main__":
    main()
