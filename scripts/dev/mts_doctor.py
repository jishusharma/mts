"""mts_doctor.py - the MTS doctor: one repeatable, read-only health check (MyTradingSys/system/MTS_DOCTOR.md).

  python scripts/dev/mts_doctor.py [--hours 72] [--memory DIR] [--out DIR] [--no-process]

Part 1 (AI health): dead references, duplicated guidance, memory index drift, task-card lint warnings, twin cards, bad skills, boot cost.
Part 2 (process health): health_audit.py (commit mix, gate bookkeeping, B4 adoption, red CI, stale claims).
Writes ONE file, <out>/REPORT_<utc date>.md (default MyTradingSys/research/mts_doctor/). Reports only: it never edits rules,
memory, cards or the live tree. Part 1 is deterministic for a given repo state; Part 2 reads trunk and CI at run time.
"""
import argparse
import json
import re
import subprocess
import sys
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
OUT_REL = "MyTradingSys/research/mts_doctor"
PATH_RE = re.compile(r"`((?:scripts|MyTradingSys)/[A-Za-z0-9_./-]+\.(?:py|ps1|md|json|csv|yml))`")
BARE_DOC_RE = re.compile(r"\b([A-Z][A-Z0-9_]{3,}\.md)\b")
DUP_MIN = 80          # a duplicated line shorter than this is usually a heading or a table row
KINDS = ("DEAD-REF", "DUPLICATE", "MEMORY", "CARD", "DUP-CARD", "SKILL", "HOOKS")
HOOK_FILES = (".claude/settings.json",)


def tracked(repo):
    out = subprocess.run(["git", "-C", str(repo), "ls-files"], capture_output=True, text=True).stdout.splitlines()
    return [p for p in out if p]


def ai_files(repo, files):
    """The files an AI session reads as guidance (not data, not archives)."""
    keep = []
    for p in files:
        low = p.lower()
        if "archive" in low or low.startswith("_archive/"):
            continue
        if p in ("CLAUDE.md", "AGENTS.md") or p.endswith("SKILL.md"):
            keep.append(p)
        elif p.startswith("MyTradingSys/system/") and p.endswith(".md") and p.count("/") == 2:
            keep.append(p)
        elif "relay_prompts/" in p and p.endswith(".md"):
            keep.append(p)
    return sorted(keep)


def read(repo, rel):
    try:
        return (Path(repo) / rel).read_text(encoding="utf-8", errors="ignore")
    except OSError:
        return ""


def dead_refs(repo, files, docs):
    have = set(files)
    names = {Path(p).name for p in files}
    out = []
    for rel in docs:
        for i, line in enumerate(read(repo, rel).splitlines(), 1):
            for m in PATH_RE.finditer(line):
                ref = m.group(1)
                if any(c in ref for c in "<>*") or "YYYY" in ref or re.search(r"/runtime/(sched|orderflow\w*|state)/", ref) or re.search(r"\d{4}-\d\d-\d\d", ref) or ref in have or (Path(repo) / ref).exists():
                    continue
                out.append(("DEAD-REF", f"{rel}:{i}", f"names {ref} which is not tracked", "fix the path or drop the line"))
            if rel == "CLAUDE.md":
                for m in BARE_DOC_RE.finditer(line):
                    if m.group(1) not in names and m.group(1) != "CLAUDE.md":
                        out.append(("DEAD-REF", f"{rel}:{i}", f"names {m.group(1)} which does not exist", "fix the name or drop the line"))
    return out


def duplicates(repo, docs):
    seen = defaultdict(set)
    for rel in docs:
        if rel.endswith(".SKILL.md"):
            continue  # each skill is installed alone, so shared rules repeat on purpose
        for line in read(repo, rel).splitlines():
            norm = re.sub(r"\s+", " ", line.strip().lstrip("-*0123456789.) ").lower())
            if len(norm) >= DUP_MIN and not norm.startswith(("|", "```", "#")):
                seen[norm].add(rel)
    return [("DUPLICATE", ", ".join(sorted(rels)), f"same line in {len(rels)} files: {norm[:70]}...",
             "keep one copy, point the others at it") for norm, rels in sorted(seen.items()) if len(rels) > 1]


def memory_drift(memory_dir):
    if not memory_dir or not Path(memory_dir).is_dir():
        return []
    d = Path(memory_dir)
    index = (d / "MEMORY.md").read_text(encoding="utf-8", errors="ignore") if (d / "MEMORY.md").exists() else ""
    listed = set(re.findall(r"\]\(([^)]+\.md)\)", index))
    files = {p.name for p in d.glob("*.md") if p.name != "MEMORY.md"}
    out = [("MEMORY", f"MEMORY.md", f"lists {n} which does not exist", "delete the index line or restore the file") for n in sorted(listed - files)]
    out += [("MEMORY", n, "is not in MEMORY.md (never recalled)", "add an index line or delete the memory") for n in sorted(files - listed)]
    return out


def card_warnings(repo):
    r = subprocess.run([sys.executable, str(Path(repo) / "scripts" / "dev" / "tasks.py"), "lint"], capture_output=True, text=True, cwd=repo)
    lines = [ln for ln in (r.stdout or "").splitlines() if ln.strip() and not ln.startswith("tasks lint:")]
    return [("CARD", ln.split(" ")[1] if ln.startswith("WARN") else ln.split(" ")[0], ln[:140], "tasks.py tag <id> --refresh, or fix the card")
            for ln in lines[:20]]


def dup_cards(repo):
    """Likely twin cards (`tasks.py twins`): two open cards for one job, e.g. made by two sessions."""
    r = subprocess.run([sys.executable, str(Path(repo) / "scripts" / "dev" / "tasks.py"), "twins"], capture_output=True, text=True, cwd=repo)
    out = []
    for ln in (r.stdout or "").splitlines():
        m = re.match(r"TWIN (\S+) (\S+) \((.*)\)$", ln)
        if m:
            out.append(("DUP-CARD", f"{m.group(1)} + {m.group(2)}", f"likely the same job ({m.group(3)})",
                        "drop one, or add the other id to not_twin_of"))
    return out[:20]


def skills(repo, files):
    out = []
    for rel in files:
        if rel.endswith("SKILL.md"):
            head = read(repo, rel)[:600]
            if not (head.startswith("---") and re.search(r"^name:\s*\S", head, re.M) and re.search(r"^description:\s*\S", head, re.M)):
                out.append(("SKILL", rel, "no frontmatter name/description (never auto-selected)", "add the two fields"))
    return out


def hook_drift(repo, ref="origin/fast-track"):
    """Claude Code loads hooks and env from the main checkout, not the worktree (seen 2026-10-21: a main checkout 1858 commits
    behind ran the old turn_meter.py). Each HOOK_FILES file there that differs from trunk is a finding; no trunk ref, no finding."""
    common = subprocess.run(["git", "-C", str(repo), "rev-parse", "--git-common-dir"],      # no --path-format: git < 2.31 echoes it
                            capture_output=True, text=True).stdout.strip()
    if not common:
        return []
    main = (Path(repo) / common).resolve().parent       # relative to repo; an absolute common dir wins
    out = []
    for rel in HOOK_FILES:
        trunk = subprocess.run(["git", "-C", str(repo), "show", f"{ref}:{rel}"], capture_output=True)
        if trunk.returncode:
            continue
        try:
            here = (main / rel).read_bytes()
        except OSError:
            here = b""
        if here.replace(b"\r\n", b"\n") != trunk.stdout.replace(b"\r\n", b"\n"):
            out.append(("HOOKS", str(main / rel), f"differs from {ref}: every session runs this copy",
                        "operator or coordinator: git -C <main checkout> pull --ff-only"))
    return out


def boot_cost(repo, docs):
    sizes = sorted(((len(read(repo, p).encode()), p) for p in docs), reverse=True)
    claude = len(read(repo, "CLAUDE.md").encode())
    top = ", ".join(f"{p.rsplit('/', 1)[-1]} {n}" for n, p in sizes[:5])
    return f"Boot cost: CLAUDE.md {claude} B loaded every turn; largest guidance files: {top}. Trim only if the cap test fails (the cache makes the prefix cheap)."


# ---- checklist (operator 2026-10-25): each fix of 10-23..10-25 leaves one check. Status OK / WARN / unavailable; never fails, never edits.
HEADROOM_MIN_PCT = 3        # OURS
CI_FIX_MIN = 10             # OURS: CLAUDE.md "ships in 10 min"
SHIP_MAX_MIN = 15           # OURS
HOOKS_BEHIND_MAX = 50       # OURS
DISK_MIN_GB = 15            # OURS
HOOK_NAMES = ("role_loader", "ci_watch")
CHECK_NAMES = ("SIZE-HEADROOM", "CI-REVERT", "SHIP-TIME", "HOOK-REG", "DISK", "CONTEXT-GAP")


def _load(path, name):
    import importlib.util
    spec = importlib.util.spec_from_file_location(name, str(path))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def size_headroom(repo):
    """CLAUDE.md etc. vs SIZE_CAPS (tests/docs/test_integrity.py, LF bytes) and roles/*.md vs BUDGET (tests/test_role_budget.py, CRLF
    bytes via its own crlf_size). Caps are imported from the tests, never copied."""
    repo = Path(repo)
    cap_file = repo / "MyTradingSys" / "tests" / "docs" / "test_integrity.py"
    bud_file = repo / "MyTradingSys" / "tests" / "test_role_budget.py"
    rows, warns = [], []
    try:
        rows += [(rel, len((repo / rel).read_bytes().replace(b"\r\n", b"\n")), cap, f"{cap_file.relative_to(repo).as_posix()} SIZE_CAPS")
                 for rel, cap in sorted(_load(cap_file, "_doc_caps").SIZE_CAPS.items())]
    except Exception as e:
        return "unavailable", f"caps not readable ({type(e).__name__}: {str(e)[:60]})"
    try:
        b = _load(bud_file, "_role_budget")
        rows += [(f"MyTradingSys/system/roles/{n}", b.crlf_size((repo / "MyTradingSys" / "system" / "roles" / n).read_bytes()), cap,
                  f"{bud_file.relative_to(repo).as_posix()} BUDGET") for n, cap in sorted(b.BUDGET.items())]
    except Exception as e:
        return "unavailable", f"role budgets not readable ({type(e).__name__}: {str(e)[:60]})"
    for rel, size, cap, src in rows:
        head = (cap - size) * 100.0 / cap
        if head < HEADROOM_MIN_PCT:
            warns.append(f"{rel} {size}/{cap} B ({head:.1f}% headroom, {src})")
    if warns:
        return "WARN", "; ".join(warns) + "; fix: move detail to a system/ doc, never raise the cap"
    tight = min(rows, key=lambda r: (r[2] - r[1]) / r[2])
    return "OK", f"{len(rows)} files, tightest {tight[0]} {tight[1]}/{tight[2]} B"


def ci_revert(runs, now=None, hours=72):
    """runs: GitHub workflow runs of fast-track (any order). Minutes from each first red to the next green; WARN when > CI_FIX_MIN or red now."""
    now = now or datetime.now(timezone.utc)

    def ts(s):
        return datetime.fromisoformat(s.replace("Z", "+00:00"))
    done = sorted((r for r in runs if r.get("conclusion") in ("success", "failure")), key=lambda r: r["created_at"])
    if not done:
        return "unavailable", "no completed runs returned"
    gaps, red_since, warns = [], None, []
    for r in done:
        t = ts(r["created_at"])
        if r["conclusion"] == "failure":
            red_since = red_since or (t, r["head_sha"][:8])
        elif red_since:
            if (now - red_since[0]).total_seconds() <= hours * 3600:
                gaps.append((red_since[1], (t - red_since[0]).total_seconds() / 60))
            red_since = None
    for sha, m in gaps:
        if m > CI_FIX_MIN:
            warns.append(f"red {sha} took {m:.0f} min to green (limit {CI_FIX_MIN})")
    if red_since:
        warns.append(f"trunk is red now since {red_since[1]} ({(now - red_since[0]).total_seconds() / 60:.0f} min): git revert the breaking commit")
    if warns:
        return "WARN", "; ".join(warns)
    return "OK", f"{len(gaps)} red streak(s) in {hours} h" + (f", slowest {max(m for _, m in gaps):.0f} min" if gaps else "") + ", trunk green"


def ci_fetch():
    import health_audit
    d = health_audit.fetch_json(f"{health_audit.API}/runs?branch=fast-track&per_page=100")
    return d["workflow_runs"] if "workflow_runs" in d else d.get("_error", "no data")


def _median(v):
    v = sorted(v)
    n = len(v)
    return v[n // 2] if n % 2 else (v[n // 2 - 1] + v[n // 2]) / 2


def ship_time(log, now=None, hours=72):
    """gate_timing.jsonl (written by sync.record_ship_timing for ships, run_all_tests.record_timing for gate steps). Ship = one `ship`
    row's secs; gate = wall time of one run of step rows (same sha). WARN when the max of either is over SHIP_MAX_MIN."""
    log = Path(log)
    if not log.is_file():
        return "unavailable", f"{log.as_posix()} missing (written by sync.py record_ship_timing / run_all_tests.py record_timing on this machine)"
    now = now or datetime.now(timezone.utc)
    ships, gates, cur = [], [], {}      # cur: sha -> [steps seen, first start, last end]; a repeated step number is a new gate run
    for ln in log.read_text(encoding="utf-8", errors="ignore").splitlines():
        try:
            r = json.loads(ln)
            t = datetime.strptime(r["utc"], "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc).timestamp()
            secs = float(r["secs"])
        except (ValueError, KeyError, TypeError):
            continue
        if now.timestamp() - t > hours * 3600:
            continue
        if r.get("step") == "ship":
            ships.append(secs)
            continue
        c = cur.setdefault(r.get("sha", ""), [set(), t - secs, t])
        if r.get("step") in c[0]:
            gates.append(c[2] - c[1])
            c[:] = [set(), t - secs, t]
        c[0].add(r.get("step"))                      # steps run in parallel shards: wall time = first start to last end
        c[1], c[2] = min(c[1], t - secs), max(c[2], t)
    g = gates + [c[2] - c[1] for c in cur.values() if c[0]]
    if not ships and not g:
        return "unavailable", f"no rows in the last {hours} h of {log.as_posix()}"
    parts = []
    for label, v in (("ship", ships), ("gate", g)):
        parts.append(f"{label} n={len(v)} median {_median(v) / 60:.1f} max {max(v) / 60:.1f} min" if v else f"{label} no rows")
    over = [lab for lab, v in (("ship", ships), ("gate", g)) if v and max(v) / 60 > SHIP_MAX_MIN]
    if over:
        return "WARN", f"{'; '.join(parts)}; {'/'.join(over)} max over {SHIP_MAX_MIN} min: profile the slowest gate steps in {log.as_posix()}"
    return "OK", "; ".join(parts)


def hook_reg(repo, ref="origin/fast-track"):
    """Worktree sessions take hooks from the MAIN checkout: it must register HOOK_NAMES and not be far behind trunk."""
    common = subprocess.run(["git", "-C", str(repo), "rev-parse", "--git-common-dir"], capture_output=True, text=True).stdout.strip()
    if not common:
        return "unavailable", "not a git checkout"
    main = (Path(repo) / common).resolve().parent
    try:
        text = (main / ".claude" / "settings.json").read_text(encoding="utf-8", errors="ignore")
    except OSError:
        return "WARN", f"{main / '.claude' / 'settings.json'} missing: git -C {main} pull --ff-only"
    warns = [f"{n} not registered in {main / '.claude' / 'settings.json'}" for n in HOOK_NAMES if n not in text]
    r = subprocess.run(["git", "-C", str(main), "rev-list", "--count", f"HEAD..{ref}"], capture_output=True, text=True)
    behind = int(r.stdout.strip()) if r.returncode == 0 and r.stdout.strip().isdigit() else None
    if behind is not None and behind > HOOKS_BEHIND_MAX:
        warns.append(f"main checkout is {behind} commits behind {ref} (limit {HOOKS_BEHIND_MAX})")
    if warns:
        return "WARN", "; ".join(warns) + f"; fix: git -C {main} pull --ff-only"
    return "OK", f"{'+'.join(HOOK_NAMES)} registered in {main.name}, " + (f"{behind} behind {ref}" if behind is not None else f"behind-count unavailable (no {ref})")


def disk(repo, free_gb=None):
    import shutil
    try:
        gb = free_gb if free_gb is not None else shutil.disk_usage(str(repo)).free / 1e9
    except OSError as e:
        return "unavailable", str(e)[:80]
    if gb < DISK_MIN_GB:
        return "WARN", f"{gb:.1f} GB free on the repo drive (limit {DISK_MIN_GB}): scripts/dev/declutter_backups.py --apply, c_drive_guard"
    return "OK", f"{gb:.0f} GB free"


def context_gap(repo, runs=None):
    """WARN when the median unnamed_reads (files a session read that its prompt never named) rose against the previous row of context_gap_runs.jsonl."""
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    import context_gap as G
    rs = G.rows(str(runs or Path(repo) / "MyTradingSys/research/mts_doctor/context_gap_runs.jsonl"))
    if len(rs) < 2:
        return "OK", f"{len(rs)} row(s) in context_gap_runs.jsonl; python scripts/dev/context_gap.py measure adds one"
    a, b = rs[-1].get("unnamed_reads_median"), rs[-2].get("unnamed_reads_median")
    if a is not None and b is not None and a > b:
        return "WARN", f"median unnamed_reads rose {b} -> {a} ({rs[-1]['utc']}): sessions read more files than their start prompt named"
    return "OK", f"median unnamed_reads {a} (previous {b})"


def checklist(repo, process=True, now=None):
    """[(name, status, detail)] for CHECK_NAMES. A check that raises is reported unavailable, never fatal."""
    repo = Path(repo)

    def ci():
        if not process:
            return "unavailable", "skipped (--no-process, no network)"
        runs = ci_fetch()
        return ("unavailable", f"GitHub API: {runs}") if isinstance(runs, str) else ci_revert(runs, now)
    fns = (("SIZE-HEADROOM", lambda: size_headroom(repo)), ("CI-REVERT", ci),
           ("SHIP-TIME", lambda: ship_time(repo / "runtime_data" / "gate_timing.jsonl", now)),
           ("HOOK-REG", lambda: hook_reg(repo)), ("DISK", lambda: disk(repo)),
           ("CONTEXT-GAP", lambda: context_gap(repo)))
    out = []
    for name, fn in fns:
        try:
            out.append((name, *fn()))
        except Exception as e:
            out.append((name, "unavailable", f"{type(e).__name__}: {str(e)[:80]}"))
    return out


def health_line(results):
    bad = [n for n, s, _ in results if s == "WARN"]
    return "HEALTH: GREEN" if not bad else f"HEALTH: {len(bad)} WARN: {', '.join(bad)}"


def previous_metrics(out, day):
    """METRICS line of the newest report older than `day`, as a dict; {} when there is none."""
    older = sorted(p for p in Path(out).glob("REPORT_*.md") if p.stem[7:] < day)
    if not older:
        return {}
    m = re.search(r"^METRICS (.*)$", older[-1].read_text(encoding="utf-8", errors="ignore"), re.M)
    return dict(kv.split("=", 1) for kv in m.group(1).split()) if m else {}


def run(repo=REPO, out_dir=None, memory_dir=None, process=True, hours=72, now=None):
    repo = Path(repo)
    files = tracked(repo)
    docs = ai_files(repo, files)
    findings = (dead_refs(repo, files, docs) + duplicates(repo, docs) + memory_drift(memory_dir) + card_warnings(repo)
                + dup_cards(repo) + skills(repo, docs) + hook_drift(repo))
    day = (now or datetime.now(timezone.utc)).strftime("%Y-%m-%d")
    out = Path(out_dir) if out_dir else repo / OUT_REL
    checks = checklist(repo, process, now)
    lines = [health_line(checks), "", f"# MTS doctor report {day}", "", "Checklist (OK / WARN / unavailable)", ""]
    lines += [f"- [{s}] {n}: {d}" for n, s, d in checks]
    lines += ["", f"Part 1: AI health ({len(docs)} guidance files checked). Reports only; nothing was edited.", "",
             boot_cost(repo, docs), f"Memory: {memory_dir if memory_dir and Path(memory_dir).is_dir() else 'skipped (no memory dir on this machine)'}", ""]
    counts = {k: sum(1 for f in findings if f[0] == k) for k in KINDS}
    lines += ["Findings: " + ", ".join(f"{k} {v}" for k, v in counts.items()), ""]
    lines += [f"- [{k}] {where}: {msg} | fix: {fix}" for k, where, msg, fix in findings] or ["- none"]
    if process:
        sys.path.insert(0, str(Path(__file__).resolve().parent))
        import health_audit
        text = health_audit.build(hours)
        prev = previous_metrics(out, day)
        now_m = dict(kv.split("=", 1) for kv in re.search(r"^METRICS (.*)$", text, re.M).group(1).split()) if "METRICS " in text else {}
        delta = [f"{k} {prev[k]} -> {v}" for k, v in now_m.items() if k in prev and prev[k] != v]
        lines += ["", "Part 2: process health (trunk and CI at run time)", "",
                  "Since the previous report: " + (", ".join(delta) if delta else ("no change" if prev else "no earlier report")), "",
                  text.replace("# health audit", "## Process detail", 1)]
    out.mkdir(parents=True, exist_ok=True)
    path = out / f"REPORT_{day}.md"
    path.write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")
    return path, findings


def default_memory():
    base = Path.home() / ".claude" / "projects"
    slug = re.sub(r"[^A-Za-z0-9]", "-", str(REPO.parent / "BinanceDataFeed"))
    for cand in (base / slug / "memory",):
        if cand.is_dir():
            return cand
    return None


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--hours", type=int, default=72)
    ap.add_argument("--memory")
    ap.add_argument("--out")
    ap.add_argument("--no-process", action="store_true")
    a = ap.parse_args()
    sys.stdout.reconfigure(errors="replace")
    p, f = run(REPO, a.out, a.memory or default_memory(), not a.no_process, a.hours)
    print(p.read_text(encoding="utf-8").splitlines()[0])
    print(f"{p}: {len(f)} findings")
