"""Card tom-holdout-clean-split (N1, N2): DATES ONLY, no price or outcome is read.

  python -I scripts/dev/tom_holdout_split.py [archive_klines_dir]   # writes HOLDOUT_CLEAN.json

Holdout 2026-04-11..2026-10-09 (PRE_REG_DAX). Every ledger candidate date inside it is dropped, +-1 trading day
(trading day = UTC date with at least one 1m bar in the DAX archive; only the open_ms column is read).
Design/check split: NOT decided here. It is the frozen session split of TOM_LAYER_V2_SPEC.md section 7, copied below
(DESIGN = sessions whose transcript existed when the spec was written, CHECK otherwise). Contamination exclusions
(spec section 7): every candidate date of a ledger group is removed from dev and holdout; +-1 trading day covers the
spec's "and the trading day before each".
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


# TOM_LAYER_V2_SPEC.md section 7, frozen 2026-10-13 (grouped by session; no outcome read)
SPLIT = {
    "design": {"S1 n7ZSkjb7JXs": ["T1"], "S2 k0zm5NYn0IQ": ["T2", "T2b"], "S3 ujedEcmvBMk": ["T3", "T3b"],
               "S4 T6hDJcHrVBM": ["T5"], "S5 zQTbdEweG3c": ["T6"], "S6 l8RZrBfzvp4 (text only, ES)": ["T7"]},
    "check": {"S7 liEJMfE_PXg": ["T11"], "S8 ZZeET7ng1nk": ["T12"]},
    "family_c_in_neither_set": {"S9 UOBgXV20yCM": ["T4"]},
    "excluded": {"T8": "own row in S1 (spec: T1 (+T8, excluded))"},
}
DEV_START, DEV_END = "2024-11-04", "2026-04-10"


def flat(section):
    return sorted((g for v in SPLIT[section].values() for g in v), key=lambda g: int(re.sub(r"\D", "", g)))


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
    sess_groups = set(flat("design")) | set(flat("check")) | set(flat("family_c_in_neither_set")) | set(SPLIT["excluded"])
    missing = sorted(set(groups) - sess_groups)
    _, dev_dropped, _ = clean_holdout(cands, days, DEV_START, DEV_END)
    out = {
        "card": "tom-holdout-clean-split", "dates_only": True,
        "source": "TOM_LEDGER_CANONICAL_GROUPS.csv date_candidates_to_exclude (recording, inferred, legacy dates; none is a verified trade date)",
        "calendar": f"UTC dates with >=1 bar in the DAX archive klines ({len(days)} days, {days[0]}..{days[-1]})",
        "holdout_window": [H_START, H_END],
        "holdout_days_before": len(hold), "dropped_days": {d: dropped[d] for d in sorted(dropped)},
        "dropped_count": len(dropped), "remaining_holdout_days": remaining, "remaining_count": len(remaining),
        "dev_window": [DEV_START, DEV_END],
        "dev_dropped_days": {d: dev_dropped[d] for d in sorted(dev_dropped)}, "dev_dropped_count": len(dev_dropped),
        "forward_holdout": {"from": FWD_START, "read_once_at_trades_ge": 100,
                            "note": "DAX bars from 2026-10-10 on; no look before 100 trades; every recall iteration is a TRIAL_REGISTRY row"},
        "split_source": "TOM_LAYER_V2_SPEC.md section 7 (frozen; copied, not re-derived)",
        "split": SPLIT, "design_groups": flat("design"), "check_groups": flat("check"),
        "groups_not_covered_by_split": missing,
    }
    with open(OUT, "w", encoding="utf-8", newline="\n") as f:
        json.dump(out, f, indent=1)
        f.write("\n")
    print(f"holdout days {len(hold)}, dropped {len(dropped)}, remaining {len(remaining)}; dev dropped {len(dev_dropped)}; "
          f"design {flat('design')}; check {flat('check')}; uncovered {missing}")
    return 1 if missing else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
