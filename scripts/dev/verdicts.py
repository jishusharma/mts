#!/usr/bin/env python
"""Verdict registry: one row per tested arm, built from research/**/RESULT.md + PRE_REG.md.

  verdicts.py backfill                parse every study folder, rewrite VERDICTS.csv, list UNPARSED fields
  verdicts.py check "<family words>"  print prior rows; exit 1 if a matching row is one_run=yes or a FAIL
                                      whose kill_scope is not "none" (run BEFORE freezing a PRE_REG)
  verdicts.py count --split DEV [--ledger]  with --ledger also the count-only rows of TRIAL_LEDGER.csv (per study the larger
                                      of the two counts, no double count)
  verdicts.py count --split DEV       distinct (study, arm) variants already read on that split = m for Holm
  verdicts.py add key=value ...       append/replace one row by hand (after RESULT, for studies backfill cannot parse)

Parsing rules: a field that cannot be read from the files is written as UNPARSED, never guessed.
Study folders are those holding RESULT.md (or RESULTS.md) and/or PRE_REG.md under --root.
Sources of each field:
  family       title line of PRE_REG.md (else RESULT.md), prefix and "(frozen..)" / ", BTCUSDT" tail cut
  arm/n/mean/se  first table under a header "Verdict arms" or "Primary ..." (columns arm|group, n, mean*, SE*, verdict)
  verdict      BLOCKED = study folder with BLOCKED.md and no RESULT.md (count-only gate stop; check never treats it as a
               family-wide FAIL, its kill_scope sentence is read from BLOCKED.md too);
               the arm's verdict column; else the study word (first line, "Verdict:" line, "## Verdict"/"## Answer"
               first line). NEGATIVE / "no edge" / "nothing survives" read as FAIL. Control row "C" of a primary
               table without a verdict column: derived from the PRE_REG rule (n >= 200 and t_cost < 2 => FAIL),
               and marked "(derived)" in kill_scope.
  split_read   "DEV+VALIDATION+HOLDOUT" if the text reports all three side by side, "DEV" for "DEV only"/"on DEV"
  one_run      yes if PRE_REG says "one run" or "not changed after the first outcome"; no if the study has no
               PRE_REG; UNPARSED otherwise
  kill_scope   the sentence "FAIL means stop: ..." / "FAIL/INCONCLUSIVE: stop; ..." (PRE_REG or RESULT); "none"
               for PASS (and INCONCLUSIVE without such a sentence); UNPARSED for FAIL without one (check treats
               that as family-wide)
  commit/date  last git commit touching the result file (else the date in the folder name, else UNPARSED)
Counting is a lower bound: only table arms and study rows count, not secondary cells or variant grids.
"""
import argparse
import csv
import math
import re
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
RESEARCH = REPO / "MyTradingSys" / "research"
CSV_PATH = RESEARCH / "VERDICTS.csv"
OVERRIDES_PATH = RESEARCH / "VERDICTS_OVERRIDES.csv"
OVERRIDE_COLS = ["study_dir", "arm", "column", "value", "source"]
COLS = ["study_dir", "family", "arm", "split_read", "n", "gross_mean_pct", "se_pct", "cost_pct",
        "verdict", "kill_scope", "one_run", "commit", "date"]
UNP = "UNPARSED"
VERDICTS = ("PASS", "FAIL", "INCONCLUSIVE", "BLOCKED")
N_MIN = 200       # PRE_REG template section 4 (gross_effect_screen_2026-10-15)
STOP = {"the", "and", "with", "for", "from", "after", "then", "that", "this", "into", "than", "are", "not",
        "screen", "dev", "btc", "btcusdt", "study", "test", "rule", "work", "family"}
FLOAT = re.compile(r"^[-+]?\d+(?:\.\d+)?$")


def read(p):
    return Path(p).read_text(encoding="utf-8", errors="replace").replace("\r\n", "\n")


# ---------------------------------------------------------------- parsing helpers
def title_of(text):
    for ln in text.split("\n"):
        if ln.startswith("# "):
            return ln[2:].strip()
    return None


def clean_family(title):
    t = re.sub(r"^(RESULT|PRE-REGISTRATION|PRE_REG)\s*:\s*", "", title, flags=re.I)
    t = re.split(r"\s\((?:frozen|primary|BTCUSDT)|,\s*BTCUSDT|,\s*DEV (?:only|screen)|\sDEV screen|\son DEV\b", t)[0]
    return t.strip(" ,;") or None


def word_verdict(s):
    """Map the lead of a verdict text to PASS/FAIL/INCONCLUSIVE or None."""
    s = s.strip().strip("*# ").upper()
    s = re.sub(r"^(VERDICT|STUDY WORD)\s*[:=]\s*", "", s).strip("* ")
    for w in VERDICTS:
        if re.match(w + r"\b", s):
            return w
    if re.match(r"(EXPLORATORY )?NEGATIVE\b|NO EDGE\b|NOTHING SURVIVES\b", s):
        return "FAIL"
    return None


def study_verdict(text):
    lines = text.split("\n")
    first = next((l for l in lines if l.strip()), "")
    v = word_verdict(first)
    if v and (len(first.split()) <= 3 or re.match(r"\s*\**\s*verdict", first, re.I)):
        return v
    for i, l in enumerate(lines):
        m = re.match(r"\s*\**(?:verdict|study word)\**\s*[:=]\s*(.*)", l, re.I)
        if m and word_verdict(m.group(1)):
            return word_verdict(m.group(1))
        if re.match(r"##\s*(verdict|answer)\b", l, re.I):
            nxt = next((x for x in lines[i + 1:] if x.strip()), "")
            if word_verdict(nxt):
                return word_verdict(nxt)
    return None


def first_table(text, header_re):
    """Rows (list of dict header->cell) of the first table after a '##' header matching header_re."""
    lines = text.split("\n")
    for i, l in enumerate(lines):
        if l.startswith("##") and re.search(header_re, l, re.I):
            tbl = []
            for x in lines[i + 1:]:
                if x.startswith("|"):
                    tbl.append([c.strip() for c in x.strip().strip("|").split("|")])
                elif tbl:
                    break
                elif x.startswith("##"):
                    break
            if len(tbl) >= 3:
                head = [h.lower() for h in tbl[0]]
                return head, [dict(zip(head, r)) for r in tbl[2:]]
    return None


def num(cell):
    if cell is None:
        return UNP
    c = cell.strip().replace("%", "").strip()
    return c if FLOAT.match(c) else UNP


def col(row, pred):
    for k, v in row.items():
        if pred(k):
            return v
    return None


def split_of(*texts):
    t = "\n".join(texts)
    if re.search(r"DEV[ -]only|\bon DEV\b|VAL(?:IDATION)?\s+and\s+HOLD(?:OUT)?\s+(?:were\s+)?(?:never opened|not read)", t):
        return "DEV"
    if re.search(r"DEV[^\n]{0,60}VAL[^\n]{0,60}HOLD", t):
        return "DEV+VALIDATION+HOLDOUT"
    return UNP


def cost_of(*texts):
    for t in texts:
        for pat in (r"\bC\s*=\s*([\d.]+)\s*%", r"cost[^0-9\n]{0,25}([\d.]+)\s*%", r"net of ([\d.]+)\s*%"):
            m = re.search(pat, t)
            if m:
                return m.group(1)
    return UNP


def one_run_of(pre):
    if pre is None:
        return "no"
    if re.search(r"one[ -]run\b|not changed after the first outcome|changed after the first outcome", pre, re.I):
        return "yes"
    return UNP


def kill_scope_of(*texts):
    for t in texts:
        if not t:
            continue
        for ln in t.split("\n"):
            m = re.search(r"(FAIL means stop[^\n]*|FAIL/INCONCLUSIVE:\s*stop[^\n]*)", ln)
            if m:
                return re.sub(r"\s+", " ", m.group(1)).strip().replace("**", "")[:400]
    return None


def git_info(path):
    try:
        out = subprocess.run(["git", "-C", str(path.parent), "log", "-1", "--format=%h|%cd", "--date=short", "--", path.name],
                             capture_output=True, text=True, timeout=30).stdout.strip()
    except Exception:
        out = ""
    if "|" in out:
        return out.split("|", 1)
    m = re.search(r"(\d{4}-\d{2}-\d{2})", path.parent.name)
    return UNP, (m.group(1) if m else UNP)


# ---------------------------------------------------------------- one study
def parse_study(d):
    res_file = next((d / n for n in ("RESULT.md", "RESULTS.md") if n in {x.name for x in d.iterdir()}), None)
    pre_file = d / "PRE_REG.md" if "PRE_REG.md" in {x.name for x in d.iterdir()} else None
    blk = read(d / "BLOCKED.md") if "BLOCKED.md" in {x.name for x in d.iterdir()} else None
    res = read(res_file) if res_file else None
    pre = read(pre_file) if pre_file else None
    base = {c: UNP for c in COLS}
    base["study_dir"] = d.name
    t = (pre and title_of(pre)) or (res and title_of(res))
    base["family"] = (clean_family(t) if t else None) or UNP
    base["split_read"] = split_of(*(x for x in (res, pre) if x))
    base["cost_pct"] = cost_of(*(x for x in (res, pre) if x))
    base["one_run"] = one_run_of(pre)
    scope = kill_scope_of(pre, res, blk)
    if res_file:
        base["commit"], base["date"] = git_info(res_file)
    else:
        base["commit"], base["date"] = git_info(pre_file or d / "BLOCKED.md")
    sv = study_verdict(res) if res else None
    if sv is None and res is None and blk is not None:
        sv = "BLOCKED"   # count-only study stopped by a gate: never a FAIL, never family-wide (GATE_AUDIT Q4)
    base["arm"] = "(study)"
    rows = []
    tbl = first_table(res, r"verdict arms|primary") if res else None
    if tbl:
        head, trs = tbl
        has_v = "verdict" in head
        for i, r in enumerate(trs):
            first = list(r.values())[0]
            row = dict(base)
            row["arm"] = first
            row["n"] = num(col(r, lambda k: k == "n"))
            row["gross_mean_pct"] = num(col(r, lambda k: k.startswith("mean")))
            row["se_pct"] = num(col(r, lambda k: k.startswith("se")))
            if has_v:
                v = (r.get("verdict") or "").strip().upper()
                row["verdict"] = v if v in VERDICTS else UNP
            elif i == 0:
                row["verdict"] = sv or UNP
            elif first.strip() == "C" and sv in ("INCONCLUSIVE", "FAIL"):
                # PRE_REG s4: PASS_CONTROL did not hold (study word is not a PASS); n >= N_MIN and t_cost < 2 => FAIL
                tc = col(r, lambda k: k.startswith("t_cost"))
                if FLOAT.match(str(tc or "")) and row["n"] != UNP and float(row["n"]) >= N_MIN and float(tc) < 2.0:
                    row["verdict"] = "FAIL"
                    row["_derived"] = True
            else:
                continue
            rows.append(row)
    if not rows:
        row = dict(base)
        row["verdict"] = sv or UNP
        rows.append(row)
    for row in rows:
        v = row["verdict"]
        s = scope
        if v == "PASS":
            s = "none"
        elif s is None:
            s = "none" if v in ("INCONCLUSIVE", "BLOCKED") else UNP
        if row.pop("_derived", False):
            s = (s + " (derived)") if s not in (UNP, "none") else "derived from PRE_REG s4 rule"
        row["kill_scope"] = s
    return rows


def study_dirs(root):
    seen = set()
    for pat in ("RESULT.md", "RESULTS.md", "PRE_REG.md"):
        for f in Path(root).rglob(pat):
            if pat in {x.name for x in f.parent.iterdir()}:   # Windows globbing ignores case; phase2/results.md is not a study result
                seen.add(f.parent)
    return sorted(seen)


# ---------------------------------------------------------------- csv io
def load(path):
    if not Path(path).exists():
        return []
    with open(path, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def save(path, rows):
    with open(path, "w", newline="\n", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=COLS, lineterminator="\n")
        w.writeheader()
        for r in rows:
            w.writerow({c: r.get(c, UNP) for c in COLS})


def load_overrides(path):
    """Hand-sourced corrections that survive backfill. arm '*' = every arm of the study; source (file:line) required."""
    out = []
    for i, r in enumerate(load(path), start=2):
        if not (r.get("source") or "").strip():
            raise ValueError(f"{path} line {i}: override without a source")
        if r.get("column") not in COLS or r["column"] in ("study_dir", "arm"):
            raise ValueError(f"{path} line {i}: unknown or non-overridable column {r.get('column')!r}")
        if not (r.get("study_dir") or "").strip() or not (r.get("arm") or "").strip():
            raise ValueError(f"{path} line {i}: study_dir and arm are required")
        out.append(r)
    return out


def apply_overrides(rows, overrides):
    for o in overrides:
        hit = [r for r in rows if r["study_dir"] == o["study_dir"] and o["arm"] in ("*", r["arm"])]
        for r in hit:
            r[o["column"]] = o["value"]
            if o["column"] == "verdict" and r.get("kill_scope") == UNP and o["value"] == "INCONCLUSIVE":
                r["kill_scope"] = "none"        # same rule as parse_study
    return rows


def cmd_apply_overrides(a):
    """Patch only the overridden cells of the existing registry (no re-parse: backfill would rewrite curated rows)."""
    rows = load(a.csv)
    ov = load_overrides(a.overrides)
    missing = [o["study_dir"] for o in ov if not any(r["study_dir"] == o["study_dir"] for r in rows)]
    if missing:
        raise ValueError(f"override study not in {a.csv}: {sorted(set(missing))}")
    apply_overrides(rows, ov)
    save(a.csv, rows)
    print(f"{a.csv}: {len(ov)} override(s) applied to {len(rows)} rows")


def cmd_backfill(a):
    root = Path(a.root)
    new, studies = [], study_dirs(root)
    for d in studies:
        new.extend(parse_study(d))
    apply_overrides(new, load_overrides(getattr(a, "overrides", None) or OVERRIDES_PATH))
    names = {d.name for d in studies}
    kept = [r for r in load(a.csv) if r["study_dir"] not in names]
    save(a.csv, kept + new)
    rows = load(a.csv)                       # count only after re-reading what was written
    bad = {}
    for r in new:
        miss = [c for c in COLS if r.get(c) == UNP]
        if miss:
            bad.setdefault(r["study_dir"], set()).update(miss)
    cells = sum(1 for r in new for c in COLS if r.get(c) == UNP)
    print(f"{a.csv}: {len(rows)} rows ({len(kept)} kept, {len(new)} parsed) from {len(studies)} studies, "
          f"{len(bad)} studies with UNPARSED fields ({cells} UNPARSED cells)")
    for s in sorted(bad):
        print(f"  UNPARSED {s}: {', '.join(sorted(bad[s]))}")


# ---------------------------------------------------------------- check / count
def stems(s):
    return {w[:5] for w in re.findall(r"[a-z0-9]{3,}", s.lower()) if not w.isdigit() and w not in STOP}


def power_line(row):
    """Compute MDE80, net mean, LOW-POWER flag and trades-for-80%-power for a row.

    MDE80 = 2.8016 * se_pct (two-sided alpha 0.05, 80% power; SOURCED REPORT.md:211-212).
    Flagged LOW-POWER when |net mean| < MDE80.
    Trades for 80% power = round(n * (MDE80 / |net mean|)^2).
    """
    try:
        se_val = row.get("se_pct") if "se_pct" in row else row.get("se")
        se = float(se_val)
    except (ValueError, TypeError):
        return None
    if se < 0:
        return None
    mde80 = 2.8016 * se
    parts = [f"MDE80={round(mde80, 5)}"]

    try:
        gross_val = row.get("gross_mean_pct") if "gross_mean_pct" in row else row.get("gross")
        cost_val = row.get("cost_pct") if "cost_pct" in row else row.get("cost")
        gross = float(gross_val)
        cost = float(cost_val)
        net = gross - cost
        parts.append(f"net={round(net, 4)}")
        if abs(net) < mde80:
            parts.append("LOW-POWER")
        n_val = row.get("n")
        n = float(n_val)
        if n > 0 and abs(net) > 0:
            n80 = round(n * (mde80 / abs(net)) ** 2)
            parts.append(f"trades_for_80_power={n80}")
    except (ValueError, TypeError):
        pass

    return "power: " + " ".join(parts)


def cmd_check(a):
    q = stems(a.words)
    if not q:
        print("check: no usable words in query")
        return 2
    need = math.ceil(0.6 * len(q))
    hits, block = [], []
    for r in load(a.csv):
        hay = stems(" ".join([r["study_dir"], r["family"], r["arm"], r["kill_scope"]]))
        if len(q & hay) >= need:
            hits.append(r)
            if r["one_run"] == "yes" or (r["verdict"] == "FAIL" and r["kill_scope"] != "none"):
                block.append(r)
    if not hits:
        print(f"check '{a.words}': no prior row matches (need {need} of {sorted(q)}). Safe to pre-register; append your row after RESULT.")
        return 0
    print(f"check '{a.words}': {len(hits)} prior row(s) (match {need}+ of {sorted(q)})")
    for r in hits:
        flag = "BLOCK" if r in block else "     "
        print(f"  {flag} {r['study_dir']} | {r['arm']} | {r['split_read']} | n={r['n']} mean={r['gross_mean_pct']} "
              f"se={r['se_pct']} cost={r['cost_pct']} | {r['verdict']} | one_run={r['one_run']} | {r['commit']} {r['date']}")
        print(f"        kill_scope: {r['kill_scope']}")
        pl = power_line(r)
        if pl:
            print(f"        {pl}")

    if block:
        print("BLOCKED: a one_run PRE_REG may not be re-run and a FAIL kills its family. A new PRE_REG must say why it is "
              "a different hypothesis. (kill_scope UNPARSED = read the study's PRE_REG/RESULT for the scope.)")
        return 1
    return 0


def count_variants(csv_path, split):
    """({(study, arm)} read on `split`, rows skipped as split_read UNPARSED): the lower bound for Holm m."""
    seen, skipped = set(), 0
    for r in load(csv_path):
        if r["split_read"] == UNP:
            skipped += 1
        elif split.upper() in r["split_read"].upper().split("+"):
            seen.add((r["study_dir"], r["arm"]))
    return seen, skipped


def ledger_per_study(ledger_path, split):
    """{study: distinct variants} read on `split` in the hand-kept TRIAL_LEDGER.csv (study,variant,run_utc,split,...)."""
    out = {}
    for r in load(ledger_path):
        if split.upper() in (r.get("split") or "").upper().split("+"):
            out.setdefault(r["study"], set()).add(r["variant"])
    return out


def count_with_ledger(csv_path, ledger_path, split):
    """Holm m with count-only rows (GATE_AUDIT Q6): per study the larger of the VERDICTS arm count and the ledger variant
    count, so a study listed in both (names differ: arm W01 vs variant WT-A01_W01) is never counted twice."""
    seen, skipped = count_variants(csv_path, split)
    per = {}
    for s, _ in seen:
        per[s] = per.get(s, 0) + 1
    for s, v in ledger_per_study(ledger_path, split).items():
        per[s] = max(per.get(s, 0), len(v))
    return sum(per.values()), len(per), skipped


def cmd_count(a):
    if getattr(a, "ledger", False):
        total, studies, skipped = count_with_ledger(a.csv, a.ledger_csv, a.split)
        print(f"{total}")
        print(f"# distinct variants read on {a.split.upper()} = per study max(VERDICTS arms, TRIAL_LEDGER variants): {total} from "
              f"{studies} studies; {skipped} VERDICTS rows have split_read UNPARSED and are not counted (lower bound for Holm m).",
              file=sys.stderr)
        return 0
    seen, skipped = count_variants(a.csv, a.split)
    studies = len({s for s, _ in seen})
    print(f"{len(seen)}")
    print(f"# distinct variants (study, arm) read on {a.split.upper()}: {len(seen)} from {studies} studies; "
          f"{skipped} rows have split_read UNPARSED and are not counted; secondary cells and variant grids are not counted "
          f"(lower bound for Holm m).", file=sys.stderr)
    return 0


def cmd_add(a):
    row = {c: UNP for c in COLS}
    for kv in a.pairs:
        k, _, v = kv.partition("=")
        if k not in COLS:
            print(f"add: unknown column {k}")
            return 2
        row[k] = v
    rows = [r for r in load(a.csv) if (r["study_dir"], r["arm"]) != (row["study_dir"], row["arm"])]
    save(a.csv, rows + [row])
    print(f"added {row['study_dir']} | {row['arm']}; {len(rows) + 1} rows")
    return 0


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--root", default=str(RESEARCH))
    p.add_argument("--csv", default=str(CSV_PATH))
    p.add_argument("--overrides", default=str(OVERRIDES_PATH))
    sub = p.add_subparsers(dest="cmd", required=True)
    sub.add_parser("backfill")
    sub.add_parser("apply-overrides")
    c = sub.add_parser("check")
    c.add_argument("words")
    n = sub.add_parser("count")
    n.add_argument("--split", required=True)
    n.add_argument("--ledger", action="store_true", help="also count TRIAL_LEDGER.csv rows (count-only trials)")
    n.add_argument("--ledger-csv", default=str(RESEARCH / "TRIAL_LEDGER.csv"))
    ad = sub.add_parser("add")
    ad.add_argument("pairs", nargs="+")
    a = p.parse_args(argv)
    return {"backfill": cmd_backfill, "apply-overrides": cmd_apply_overrides, "check": cmd_check, "count": cmd_count, "add": cmd_add}[a.cmd](a) or 0


if __name__ == "__main__":
    sys.exit(main())
