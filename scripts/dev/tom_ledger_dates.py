"""Mechanical check (and one-shot repair) for the Tom ledger `date` column.

Rule (RV01 D4, card rv-fix-tom-ledger-date-column): `date` is the OBSERVED trade date or empty.
Recording, inferred and chart-title dates live in their own columns, never in `date`.

  python scripts/dev/tom_ledger_dates.py check   # prints violations, exit 1 if any
  python scripts/dev/tom_ledger_dates.py fix     # idempotent repair of the CSV + groups CSV
"""
import csv
import re
import sys
from pathlib import Path

DIR = Path(__file__).resolve().parents[2] / "MyTradingSys/research/tom_transfer_2026-10-11"
LEDGER = DIR / "TOM_TRADE_LEDGER.csv"
GROUPS = DIR / "TOM_LEDGER_CANONICAL_GROUPS.csv"
ISO = re.compile(r"^\d{4}-\d{2}-\d{2}$")
ISO_ANY = re.compile(r"\d{4}-\d{2}-\d{2}")
NEW_COLS = ["date_legacy_unverified"]


def read(path):
    with open(path, encoding="utf-8", newline="") as f:
        rd = csv.DictReader(f)
        return list(rd), rd.fieldnames


def write(path, rows, fields):
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        w = csv.DictWriter(f, fieldnames=fields, lineterminator="\n")
        w.writeheader()
        w.writerows(rows)


def violations(rows, groups=None):
    out = []
    by_group = {}
    for r in rows:
        rid, d = r["id"], r.get("date", "")
        inf = r.get("trade_date_inferred", "")
        st = r.get("trade_date_status", "")
        if d and not ISO.match(d):
            out.append(f"{rid}: date is not ISO: {d!r}")
        if d and not st.startswith("OBSERVED"):
            out.append(f"{rid}: date {d!r} set while trade_date_status is {st[:40]!r}")
        if inf and not ISO.match(inf):
            out.append(f"{rid}: trade_date_inferred is not ISO: {inf!r}")
        for v in (d, inf):
            if v:
                by_group.setdefault(r.get("canonical_id") or rid, set()).add(v)
    for g, vals in sorted(by_group.items()):
        if len(vals) > 1:
            out.append(f"group {g}: {len(vals)} different dates {sorted(vals)}")
    for g in groups or []:
        for col in ("trade_date_observed", "trade_date_inferred"):
            v = g.get(col, "")
            if v and not ISO.match(v):
                out.append(f"groups {g['canonical_id']}: {col} not ISO: {v!r}")
    return out


def fix_rows(rows):
    for r in rows:
        old = r.get("date", "")
        st = r.get("trade_date_status", "")
        if old and not (ISO.match(old) and st.startswith("OBSERVED")):
            m = ISO_ANY.search(old)
            r["date_legacy_unverified"] = r.get("date_legacy_unverified") or (m.group(0) if m else "")
            if st.startswith("ASSUMED") and not r.get("trade_date_inferred"):
                r["trade_date_inferred"] = r["date_legacy_unverified"]
            r["date"] = ""
        r.setdefault("date_legacy_unverified", "")
        inf = r.get("trade_date_inferred", "")
        m = ISO_ANY.search(inf)
        if inf and m and not ISO.match(inf):
            r["trade_date_inferred"] = m.group(0)  # prose qualifier stays in trade_date_status
    return rows


def fix_groups(groups, rows):
    members = {}
    for r in rows:
        members.setdefault(r.get("canonical_id") or r["id"], []).append(r)
    for g in groups:
        ms = members.get(g["canonical_id"], [])
        inferred = {r["trade_date_inferred"] for r in ms if r.get("trade_date_inferred")}
        observed = {r["date"] for r in ms if r.get("date")}
        cands = set()
        for r in ms:
            for c in ("recording_date_observed", "trade_date_inferred", "date_legacy_unverified", "date"):
                m = ISO_ANY.search(r.get(c, ""))
                if m:
                    cands.add(m.group(0))
        g["trade_date_observed"] = ";".join(sorted(observed))
        g["trade_date_inferred"] = ";".join(sorted(inferred))
        g["date_candidates_to_exclude"] = ";".join(sorted(cands))
    return groups


def main(argv):
    mode = argv[1] if len(argv) > 1 else "check"
    rows, fields = read(LEDGER)
    groups, gfields = read(GROUPS)
    if mode == "fix":
        rows = fix_rows(rows)
        fields = fields + [c for c in NEW_COLS if c not in fields]
        groups = fix_groups(groups, rows)
        gfields = gfields + [c for c in ("trade_date_observed", "trade_date_inferred",
                                         "date_candidates_to_exclude") if c not in gfields]
        write(LEDGER, rows, fields)
        write(GROUPS, groups, gfields)
    v = violations(rows, groups)
    for line in v:
        print(line)
    print(f"{len(v)} violations over {len(rows)} rows, {len(groups)} groups")
    return 1 if v else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
