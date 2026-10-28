"""T07 step 1: verdict -> publishing commit -> later commits to the study script or any repo file it imports.
Read-only on the repo (git log / numstat + ast import walk). Writes out/provenance.csv and out/provenance_commits.csv.
Run from the worktree root: python MyTradingSys/research/dsa_backtest_audit_2026-10-16/scripts/T07/t07_provenance.py
"""
import ast
import csv
import re
import subprocess
import sys
from pathlib import Path

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
REPO = HERE.parents[4]
OUT = HERE / "out"
R = "MyTradingSys/research/"

# (brief 1b #, short name, result files (the verdict lives here), study scripts)
STUDIES = [
    (1, "gross_effect_screen", [R + "gross_effect_screen_2026-10-15/RESULT.md"], [R + "gross_effect_screen_2026-10-15/screen.py"]),
    (2, "opr_preopen_tops", [R + "opr_preopen_tops_2026-10-16/RESULT.md"], [R + "opr_preopen_tops_2026-10-16/study.py"]),
    (3, "mal_bb_mid_engulf", [R + "mal_bb_mid_engulf_2026-10-16/RESULT.md"], [R + "mal_bb_mid_engulf_2026-10-16/study.py"]),
    (4, "opr_bb_mtf_center", [R + "opr_bb_mtf_center_2026-10-16/RESULT.md"], [R + "opr_bb_mtf_center_2026-10-16/study.py"]),
    (5, "opr_weekly_low_round_sweep", [R + "opr_weekly_low_round_sweep_2026-10-16/RESULT.md"], [R + "opr_weekly_low_round_sweep_2026-10-16/study.py"]),
    (6, "wlow_bounce_bbrsi60", [R + "wlow_bounce_bbrsi60_2026-10-16/RESULT.md"], [R + "wlow_bounce_bbrsi60_2026-10-16/study.py"]),
    (7, "krown_malkan_g3", [R + "krown_malkan_g3_2026-10-16/EVENT_COUNTS.md"], [R + "krown_malkan_g3_2026-10-16/event_counts.py"]),
    (8, "qriptal_scorecard", [R + "qriptal_2026-10-10/SCORECARD.md"], [R + "qriptal_2026-10-10/score_calls.py"]),
    (9, "candle_close", [R + "layer_lab/candle_close_2026-10-14/REPORT.md", R + "layer_lab/candle_close_2026-10-14/results.json"], [R + "layer_lab/candle_close_2026-10-14/study.py"]),
    (10, "levels_sizing", [R + "levels_sizing_2026-10-14/REPORT.md", R + "levels_sizing_2026-10-14/results.json"], [R + "levels_sizing_2026-10-14/probe.py"]),
    (11, "levels_hold_lc1", [R + "levels_confluence_2026-10-14/levels_hold.md"], [R + "levels_confluence_2026-10-14/levels_hold.py", R + "levels_confluence_2026-10-14/levels.py"]),
    (12, "orderflow_views", [R + "orderflow_views_2026-10-14/RESULT.md"], [R + "orderflow_views_2026-10-14/study.py"]),
    (13, "eur_low_us_sweep", [R + "eur_low_us_sweep_2026-10-14/RESULT.md"], [R + "eur_low_us_sweep_2026-10-14/study.py"]),
    (14, "mfe_exit", [R + "mfe_exit_2026-10-13/REPORT.md"], [R + "mfe_exit_2026-10-13/mfe_exit_study.py"]),
    (15, "published_strats", [R + "published_strats_2026-10-13/RESULTS.md"], [R + "published_strats_2026-10-13/run_pub.py"]),
    (16, "tom_fabio_guidance_q33", [R + "tom_fabio_guidance_2026-10-12/MATRIX_REPORT.md"], [R + "tom_fabio_guidance_2026-10-12/matrix_q33.py"]),
]


def git(*a):
    r = subprocess.run(["git", "-C", str(REPO), *a], capture_output=True, text=True, encoding="utf-8")
    return r.stdout


def sibling_dirs(src):
    """Directories added to sys.path by name, e.g. sys.path.insert(0, str(HERE.parent / "chart_read_g5_2026-10-16"))."""
    d = (REPO / src).parent
    out = [d]
    for m in re.finditer(r'sys\.path\.(?:insert|append)\([^)]*?HERE\.parent\s*/\s*["\']([^"\']+)["\']', (REPO / src).read_text(encoding="utf-8", errors="replace")):
        out.append(d.parent / m.group(1))
    out += [REPO, REPO / "MyTradingSys" / "backtest"]
    return out


def resolve(mod, dirs):
    parts = mod.split(".")
    for base in dirs:
        for cand in (base.joinpath(*parts).with_suffix(".py"), base.joinpath(*parts, "__init__.py")):
            if cand.is_file():
                return cand
    return None


def imports_of(path, dirs):
    try:
        tree = ast.parse(path.read_text(encoding="utf-8", errors="replace"))
    except SyntaxError:
        return []
    mods = []
    for n in ast.walk(tree):
        if isinstance(n, ast.Import):
            mods += [a.name for a in n.names]
        elif isinstance(n, ast.ImportFrom) and n.module and n.level == 0:
            mods.append(n.module)
            mods += [n.module + "." + a.name for a in n.names]
    found = []
    for m in mods:
        if m.split(".")[0] in sys.stdlib_module_names or m.split(".")[0] in ("numpy", "pandas", "scipy"):
            continue
        p = resolve(m, dirs)
        if p:
            found.append(p)
    return found


def walk(script):
    """Transitive repo-local import closure (files, repo-relative posix)."""
    seen = {}
    todo = [REPO / script]
    while todo:
        p = todo.pop()
        rel = p.relative_to(REPO).as_posix()
        if rel in seen:
            continue
        seen[rel] = True
        # package __init__ chain counts as an input too
        for q in imports_of(p, sibling_dirs(rel)):
            todo.append(q)
            par = q.parent
            while par != REPO and (par / "__init__.py").is_file():
                todo.append(par / "__init__.py")
                par = par.parent
    return sorted(seen)


def later_commits(files, pub):
    rows = {}
    for f in files:
        txt = git("log", "--format=@@%h|%ad|%s", "--date=short", "--numstat", f"{pub}..HEAD", "--", f)
        cur = None
        for line in txt.splitlines():
            if line.startswith("@@"):
                h, d, s = line[2:].split("|", 2)
                cur = (h, d, s)
            elif line.strip() and cur:
                a, b, fn = line.split("\t")[:3]
                ch = (int(a) if a.isdigit() else 0) + (int(b) if b.isdigit() else 0)
                rows[(cur, fn)] = ch
    return rows


def main():
    OUT.mkdir(exist_ok=True)
    prov, com = [], []
    for num, name, results, scripts in STUDIES:
        pub = ""
        pub_info = ""
        for rf in results:
            h = git("log", "-1", "--format=%H|%h|%ad|%s", "--date=short", "--", rf).strip()
            if h and (not pub or h.split("|")[2] > pub_info.split("|")[2]):
                pub, pub_info = h.split("|")[0], h
        files = sorted({f for s in scripts for f in walk(s)})
        lc = later_commits(files, pub) if pub else {}
        # same walk against the FIRST commit that touched any result file (the verdict as first published)
        firsts = [git("log", "--reverse", "--format=%h|%ad", "--date=short", "--", rf).splitlines()[:1] for rf in results]
        firsts = sorted(x[0] for x in firsts if x)
        first_sha = firsts[0].split("|")[0] if firsts else ""
        lf = later_commits(files, first_sha) if first_sha else {}
        shas = sorted({k[0] for k in lc})
        changed = sum(lc.values())
        # a commit that only edits the result folder's own outputs is not an input change; keep files only
        stale = bool(lc)
        prov.append({
            "num": num, "study": name, "result_file": results[0], "pub_sha": pub_info.split("|")[1] if pub_info else "",
            "pub_date": pub_info.split("|")[2] if pub_info else "", "n_inputs": len(files), "n_later_commits": len(shas),
            "changed_lines": changed, "first_pub_sha": first_sha, "n_commits_since_first": len({k[0] for k in lf}),
            "lines_since_first": sum(lf.values()), "status": "STALE-CANDIDATE" if stale else "CURRENT",
            "latest_later_commit": (max(shas, key=lambda c: c[1]) if shas else ("", "", ""))[0],
        })
        for (c, fn), ch in sorted(lc.items(), key=lambda kv: (kv[0][0][1], kv[0][0][0])):
            com.append({"num": num, "study": name, "later_sha": c[0], "date": c[1], "subject": c[2][:90], "file": fn, "changed_lines": ch})
    with open(OUT / "provenance.csv", "w", newline="\n", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(prov[0]))
        w.writeheader()
        w.writerows(prov)
    with open(OUT / "provenance_commits.csv", "w", newline="\n", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=["num", "study", "later_sha", "date", "subject", "file", "changed_lines"])
        w.writeheader()
        w.writerows(com)
    for p in prov:
        print(p["num"], p["study"], p["pub_sha"], p["pub_date"], p["status"], p["n_later_commits"], p["changed_lines"])


if __name__ == "__main__":
    main()
