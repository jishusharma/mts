"""mts_doctor.py - the MTS doctor: one repeatable, read-only health check (MyTradingSys/system/MTS_DOCTOR.md).

  python scripts/dev/mts_doctor.py [--hours 72] [--memory DIR] [--out DIR] [--no-process]

Part 1 (AI health): dead references, duplicated guidance, memory index drift, task-card lint warnings, twin cards, bad skills, boot cost.
Part 2 (process health): health_audit.py (commit mix, gate bookkeeping, B4 adoption, red CI, stale claims).
Writes ONE file, <out>/REPORT_<utc date>.md (default MyTradingSys/research/mts_doctor/). Reports only: it never edits rules,
memory, cards or the live tree. Part 1 is deterministic for a given repo state; Part 2 reads trunk and CI at run time.
"""
import argparse
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
    lines = [f"# MTS doctor report {day}", "", f"Part 1: AI health ({len(docs)} guidance files checked). Reports only; nothing was edited.", "",
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
    print(f"{p}: {len(f)} findings")
