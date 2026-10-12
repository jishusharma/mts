"""Card tom-holdout-clean-split (N1, N2): DATES ONLY, no price or outcome is read.

  python -I scripts/dev/tom_holdout_split.py [archive_klines_dir]   # writes HOLDOUT_CLEAN.json

Holdout 2026-04-11..2026-10-09 (PRE_REG_DAX). Every ledger candidate date inside it is dropped, +-1 trading day
(trading day = UTC date with at least one 1m bar in the DAX archive; only the open_ms column is read).
Design/check split, rule fixed before any encode: ledger groups are joined into date clusters (groups that share a
candidate date, e.g. T4/T5 on 05-19), clusters ordered by earliest candidate date (ties: first member id), and every
third cluster starting at the second (0-based index % 3 == 1) is the CHECK set; the rest is DESIGN.
"""
import bisect
import csv
import datetime as dt
import json
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
DIR = REPO / "MyTradingSys/research/tom_transfer_2026-10-11"
GROUPS = DIR / "TOM_LEDGER_CANONICAL_GROUPS.csv"
OUT = DIR / "HOLDOUT_CLEAN.json"
ARCHIVE = Path("F:/MTS/data/dax_archive/klines")
H_START, H_END = "2026-04-11", "2026-10-09"
FWD_START = "2026-10-10"
ISO = re.compile(r"\d{4}-\d{2}-\d{2}")


def trading_days(klines_dir):
    days = set()
    for f in sorted(Path(klines_dir).glob("GER40-1m-*.csv")):
        with open(f, encoding="utf-8") as fh:
            last = None
            for line in fh:
                ms = line.split(",", 1)[0]
                if not ms.isdigit():
                    continue
                d = dt.datetime.fromtimestamp(int(ms) / 1000, dt.timezone.utc).date().isoformat()
                if d != last:
                    days.add(d)
                    last = d
    return sorted(days)


def clean_holdout(candidates, days, start=H_START, end=H_END):
    """Return (holdout_days, dropped {day: [candidate dates]}, remaining_days).

    +-1 trading day is taken on weekdays only; a Sunday (evening session bars) is dropped with the Monday it
    belongs to, so a dropped Monday also takes the Sunday and the previous Friday.
    """
    wk = [d for d in days if dt.date.fromisoformat(d).weekday() < 5]
    hold = [d for d in days if start <= d <= end]
    dropped = {}
    for c in sorted(set(candidates)):
        if not (start <= c <= end):
            continue
        i = bisect.bisect_left(wk, c)
        if i < len(wk) and wk[i] == c:
            idx = (i - 1, i, i + 1)          # trading day: itself and both neighbours
        else:
            idx = (i - 1, i)                 # weekend date: the adjacent trading days
        for j in idx:
            if 0 <= j < len(wk):
                dropped.setdefault(wk[j], []).append(c)
    for d in list(dropped):                  # Sunday bars belong to the Monday session
        sun = (dt.date.fromisoformat(d) - dt.timedelta(days=1)).isoformat()
        if dt.date.fromisoformat(d).weekday() == 0 and sun in days:
            dropped.setdefault(sun, []).extend(dropped[d])
    for c in set(candidates):                # a weekend candidate itself is dropped when it has bars
        if c in days and any(c in v for v in dropped.values()):
            dropped.setdefault(c, []).append(c)
    dropped = {d: sorted(set(v)) for d, v in dropped.items() if start <= d <= end}
    remaining = [d for d in hold if d not in dropped]
    return hold, dropped, remaining


def _key(gid):
    m = re.match(r"T(\d+)(.*)", gid)
    return (int(m.group(1)), m.group(2)) if m else (10**6, gid)


def clusters(groups):
    """groups {id: set(dates)} -> [(sorted ids, sorted dates)] ordered by earliest date then first id."""
    parent = {g: g for g in groups}

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x
    owner = {}
    for g, ds in groups.items():
        for d in ds:
            if d in owner:
                parent[find(g)] = find(owner[d])
            owner.setdefault(d, g)
    out = {}
    for g in groups:
        out.setdefault(find(g), []).append(g)
    res = []
    for ids in out.values():
        ids = sorted(ids, key=_key)
        res.append((ids, sorted(set().union(*(groups[i] for i in ids)))))
    res.sort(key=lambda c: (c[1][0], _key(c[0][0])))
    return res


def split(groups):
    """-> (clusters, design ids, check ids, undated ids)"""
    cl = clusters({g: ds for g, ds in groups.items() if ds})
    design, check = [], []
    for i, (ids, _) in enumerate(cl):
        (check if i % 3 == 1 else design).extend(ids)
    undated = sorted((g for g, ds in groups.items() if not ds), key=_key)
    return cl, sorted(design, key=_key), sorted(check, key=_key), undated


def main(argv):
    kd = Path(argv[1]) if len(argv) > 1 else ARCHIVE
    groups, cands = {}, set()
    with open(GROUPS, encoding="utf-8", newline="") as f:
        for r in csv.DictReader(f):
            ds = set(ISO.findall(r["date_candidates_to_exclude"]))
            groups[r["canonical_id"]] = ds
            cands |= ds
    days = trading_days(kd)
    hold, dropped, remaining = clean_holdout(cands, days)
    cl, design, check, undated = split(groups)
    out = {
        "card": "tom-holdout-clean-split", "dates_only": True,
        "source": "TOM_LEDGER_CANONICAL_GROUPS.csv date_candidates_to_exclude (recording, inferred, legacy dates; none is a verified trade date)",
        "calendar": f"UTC dates with >=1 bar in the DAX archive klines ({len(days)} days, {days[0]}..{days[-1]})",
        "holdout_window": [H_START, H_END],
        "holdout_days_before": len(hold), "dropped_days": {d: dropped[d] for d in sorted(dropped)},
        "dropped_count": len(dropped), "remaining_holdout_days": remaining, "remaining_count": len(remaining),
        "forward_holdout": {"from": FWD_START, "read_once_at_trades_ge": 100,
                            "note": "DAX bars from 2026-10-10 on; no look before 100 trades; every recall iteration is a TRIAL_REGISTRY row"},
        "split_rule": "date clusters (groups sharing a candidate date) ordered by earliest candidate date; 0-based index % 3 == 1 -> check, else design; fixed before any encode",
        "clusters": [{"groups": ids, "dates": ds, "set": "check" if i % 3 == 1 else "design"} for i, (ids, ds) in enumerate(cl)],
        "design_groups": design, "check_groups": check, "undated_groups": undated,
    }
    with open(OUT, "w", encoding="utf-8", newline="\n") as f:
        json.dump(out, f, indent=1)
        f.write("\n")
    print(f"holdout days {len(hold)}, dropped {len(dropped)}, remaining {len(remaining)}; design {design}; check {check}; undated {undated}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
