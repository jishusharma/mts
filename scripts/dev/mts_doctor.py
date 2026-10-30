"""mts_doctor.py - the MTS doctor: one repeatable, read-only health check (MyTradingSys/system/MTS_DOCTOR.md).

  python scripts/dev/mts_doctor.py [--hours 72] [--memory DIR] [--out DIR] [--no-process]
  python scripts/dev/mts_doctor.py --heal [--apply]   # run the safe HEAL rows only (HEAL_MAP.md); default is a dry run, --apply makes it real

Part 1 (AI health): dead references, duplicated guidance, memory index drift, task-card lint warnings, twin cards, bad skills, boot cost.
Part 2 (process health): health_audit.py (commit mix, gate bookkeeping, B4 adoption, red CI, stale claims).
Writes ONE file, <out>/REPORT_<utc date>.md (default MyTradingSys/research/mts_doctor/). Reports only: it never edits rules,
memory, cards or the live tree. Part 1 is deterministic for a given repo state; Part 2 reads trunk and CI at run time.
`--heal` is the one exception to "reports only": it runs the HEAL class of doctor finding (HEAL_MAP.md) - idempotent, reversible,
and touching no git history, live tree, runtime data or others' uncommitted files - and logs every action to <out>/heal_log.jsonl.
The main-checkout heal only prints one recovery command (the main checkout is shared session state); releases and broadcast
parks are dry-run by default and apply with `--apply`.
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


def _git(repo, *args):
    """One git call, as a result object (callers read .stdout / .returncode). Injected heals read through this so they stay
    testable: `git_fn` can be swapped, and it needs no network."""
    return subprocess.run(["git", "-C", str(repo), *args], capture_output=True, text=True)


# ---- self-heal (O1 2026-10-28, HEAL_MAP.md): the safe class of doctor finding that fixes itself instead of piling up as
# WARN lines. A HEAL row is idempotent, reversible, and touches no git history, live tree, runtime data or others' uncommitted
# files (it appends bookkeeping commits the way sync.py already does). Bigger fixes (auto-revert of a red commit, deciding a
# waiting question) are CARD rows, not heals. No timer: heals are only invoked by a doctor run (`mts_doctor.py --heal`) or
# `sync.py`, never scheduled (SCHEDULING_POLICY.md).
CARD_SHIPPED = ("done", "shipped", "released")   # wait_after's shipped states: the task's work cannot come back
HEAL_STALE_CLAIM_H = None    # resolved from sync.STALE_HOURS at call time (one source, test_mts_doctor dedupe rule)
HEAL_BROADCAST_H = 48        # OURS: a HIGH broadcast pending this long on a host with no session is parked (expired), not just WARNed


def _card_state(slug, git_fn, ref="origin/fast-track"):
    """The task card's state on trunk (git show, so no local state), or '' when there is no card (a free-form task claim)."""
    r = git_fn("show", f"{ref}:MyTradingSys/system/tasks/{slug}.json")
    if r.returncode != 0:
        return ""
    try:
        c = json.loads(r.stdout)
    except (ValueError, json.JSONDecodeError):
        return ""
    return str(c.get("status") or c.get("state") or "")


def _now_utc(now):
    return (now or datetime.now(timezone.utc)).strftime("%Y%m%dT%H%M%SZ")


def _shipped_reason(repo, slug, kv, git_fn, ref="origin/fast-track"):
    """Why a stale claim is safe to release: its card is in a shipped state, or the claim host's branch shows 0 commits ahead
    of trunk (git cherry). None when the work is not shipped - the claim stays with its owner."""
    st = _card_state(slug, git_fn, ref=ref)
    if st in CARD_SHIPPED:
        return f"card {slug} is {st} (shipped)"
    host = str(kv.get("host", "")).strip()
    if host:
        r = git_fn("rev-list", "--count", f"{ref}..origin/{host}/{slug}")
        if r.returncode == 0 and r.stdout.strip() == "0":
            return f"branch {host}/{slug} is fully on {ref} (git cherry: shipped)"
    return None


def heal_release_shipped_claims(repo, now=None, claims=None, release_fn=None, git_fn=None):
    """Release a stale claim only when its work is already shipped (card in CARD_SHIPPED, or the claim host's branch shows 0
    commits ahead of trunk). Returns [(slug, reason)]; calls release_fn(slug) for each when given. A fresh claim or an
    unshipped one stays with its owner (conservative default)."""
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    import sync as Y
    git_fn = git_fn or (lambda *a: _git(repo, *a))
    now = now or datetime.now(timezone.utc)
    stale_h = HEAL_STALE_CLAIM_H if HEAL_STALE_CLAIM_H is not None else Y.STALE_HOURS
    if claims is None:
        claims = Y.open_claims(Path(repo))
    out = []
    for slug, kv in claims:
        epoch = kv.get("epoch")
        if not epoch or (now.timestamp() - int(epoch)) / 3600 <= stale_h:
            continue                       # fresh: still being worked, not stale
        reason = _shipped_reason(repo, slug, kv, git_fn, ref=f"origin/{Y.TRUNK}")
        if reason:
            out.append((slug, reason))
            if release_fn:
                release_fn(slug)
    return out


def heal_expire_unackable_broadcasts(repo, rows=None, now=None, send_fn=None):
    """Park (`expired`) a HIGH broadcast that a host with no session has sat on past HEAL_BROADCAST_H - so mts_signal.pending
    stops listing it and the BROADCAST check drops to OK - with the reason in the ack note. Active or fresh hosts are left
    alone (a session may still ack). Returns [(host, id)] of the broadcasts parked."""
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    import mts_signal as S
    now = now or datetime.now(timezone.utc)
    if rows is None:
        h = S.ensure(repo)
        rows = S.load(h) if h else []
    active = S.hosts_active(rows, BROADCAST_SEEN_H, now)
    rows_f = [r for r in rows if r.get("aud") != "top"]
    b_by_id = {b["id"]: b for b in S.high_open(rows_f)}
    out = []
    for host in sorted(S.hosts_seen(rows_f)):
        if host in active:
            continue                       # a session ran there recently: it can still ack
        for p in S.pending(rows_f, host, now):
            if p["hours"] <= HEAL_BROADCAST_H:
                continue
            b = b_by_id.get(p["id"])
            if b and S.hosts.key(str(b.get("from", "")).split("/")[0]) == host:
                continue                 # the host that issued the HIGH broadcast does not owe it its own ack
            note = f"doctor heal: no session on {host}, HIGH pending {p['hours']:.0f} h (>{HEAL_BROADCAST_H} h)"
            extra = {"id": p["id"], "state": "expired", "host": host, "note": note}
            if send_fn:
                send_fn(note, extra)
            out.append((host, p["id"]))
    return out


def heal_main_checkout(main, git_fn=None, ref="origin/fast-track"):
    """The main checkout (where every session loads hooks from) may be behind or diverged from trunk. A heal never moves it -
    it is shared session state and may hold others' uncommitted work (O1: 'touches no ... others' uncommitted files') - so it
    prints ONE exact recovery command and names which hook copy is in use. Clean-behind gets the fast-forward command;
    diverged gets the merge command; a live tree or an in-sync checkout gets a skip / OK line. Returns the lines to report."""
    main = Path(main)
    git_fn = git_fn or (lambda *a: _git(main, *a))
    hook_copy = main / ".claude" / "settings.json"
    if (main / ".mts_live").exists():
        return [f"live tree {main}: main-checkout heal skipped (the live tree changes only by deploy)"]
    head = git_fn("rev-parse", "HEAD")
    if head.returncode != 0:
        return [f"no HEAD at {main}; nothing to heal"]
    ahead = git_fn("rev-list", "--count", f"{ref}..HEAD").stdout.strip()
    behind = git_fn("rev-list", "--count", f"HEAD..{ref}").stdout.strip()
    if ahead.isdigit() and int(ahead) > 0:
        return [f"{main} is {ahead} ahead, {behind} behind {ref} (diverged): run by hand  git -C {main} merge {ref}  "
                f"(hooks currently load from {hook_copy})"]
    if behind.isdigit() and int(behind) > 0:
        return [f"{main} is {behind} behind {ref}: run  git -C {main} merge --ff-only {ref}  "
                f"(hooks load from {hook_copy})"]
    return [f"{main} is in sync with {ref} (hooks load from {hook_copy})"]


def heal(repo, out_dir=None, now=None, dry_run=True, claims=None, rows=None, main_checkout=None, git_fn=None):
    """Run the HEAL rows only (HEAL_MAP.md) and log each action to <out_dir>/heal_log.jsonl (the audit trail is written even
    in a dry run). dry_run names the actions without executing the release or send. Returns the report lines. In apply mode
    every action is fail-soft: a lost push race (the claims branch is hot, other workers release concurrently) defers that
    one item - logged and retried next run, idempotent - rather than taking the whole heal down. A self-heal that dies on
    transient contention is not safe-by-construction."""
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    import sync as Y
    out_dir = out_dir or Path(REPO / OUT_REL)
    now = now or datetime.now(timezone.utc)
    if claims is None:
        claims = Y.open_claims(Path(repo))
    lines, log = [], []

    release_errs = {}
    def _apply_release(s):
        try:
            Y.release(repo, s)
        except Exception as e:            # lost race / transient: defer, don't crash the heal
            release_errs[s] = f"{type(e).__name__}: {str(e)[:100]}"
    released = heal_release_shipped_claims(repo, now=now, claims=claims,
                                           release_fn=None if dry_run else _apply_release, git_fn=git_fn)
    for slug, reason in released:
        err = None if dry_run else release_errs.get(slug)
        if dry_run:
            lines.append(f"would release stale claim {slug}: {reason}")
        elif err:
            lines.append(f"release of stale claim {slug} deferred ({err}); idempotent, retried next run")
        else:
            lines.append(f"released stale claim {slug}: {reason}")
        log.append({"heal": "release-shipped", "slug": slug, "reason": reason, "dry_run": dry_run,
                    "ok": (err is None) if not dry_run else None, "utc": _now_utc(now)})

    send_errs = {}
    def _apply_send(text, extra):
        try:
            _send_expired(extra, repo)
        except Exception as e:
            send_errs[extra.get("id")] = f"{type(e).__name__}: {str(e)[:100]}"
    expired = heal_expire_unackable_broadcasts(repo, rows=rows, now=now,
                                               send_fn=None if dry_run else _apply_send)
    for host, bid in expired:
        err = None if dry_run else send_errs.get(bid)
        if dry_run:
            lines.append(f"would expire HIGH {bid} on {host} as expired (no session, pending >{HEAL_BROADCAST_H} h)")
        elif err:
            lines.append(f"parking of HIGH {bid} on {host} deferred ({err}); idempotent, retried next run")
        else:
            lines.append(f"expire HIGH {bid} on {host} as expired (no session, pending >{HEAL_BROADCAST_H} h)")
        log.append({"heal": "expire-broadcast", "id": bid, "host": host, "dry_run": dry_run,
                    "ok": (err is None) if not dry_run else None, "utc": _now_utc(now)})

    if main_checkout is not None:
        for l in heal_main_checkout(main_checkout, git_fn=git_fn):
            lines.append(l)
            log.append({"heal": "main-checkout", "line": l, "dry_run": dry_run, "utc": _now_utc(now)})

    p = Path(out_dir)
    p.mkdir(parents=True, exist_ok=True)
    with open(p / "heal_log.jsonl", "a", encoding="utf-8", newline="\n") as fh:
        for row in log:
            fh.write(json.dumps(row) + "\n")
    if not lines:
        lines.append("no HEAL row fired: all clear")
    return lines


def _send_expired(extra, repo):
    """The real (non-dry) sender for a parked broadcast: an `expired` ack record, so mts_signal.pending stops listing the host."""
    import mts_signal as S
    note = extra.get("note", "")
    return S.send(f"ack {extra.get('id')} expired {note}", kind="ack",
                  extra={"id": extra.get("id"), "state": "expired", "host": extra.get("host"), "note": note})


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
SHIP_MAX_S = 120            # OURS: the operator's 2-minute ship; WARN when the median or p90 of ship_wall rows (24 h) is over it
HOOKS_BEHIND_MAX = 50       # OURS
DISK_MIN_GB = 15            # OURS
HOOK_NAMES = ("role_loader", "ci_watch")
CHECK_NAMES = ("SIZE-HEADROOM", "CI-REVERT", "SHIP-TIME", "HOOK-REG", "DISK", "CONTEXT-GAP", "WAITING-ON-OPERATOR", "BROADCAST", "STALE-CLAIMS", "SCRATCH-TRACKED", "CONFLICT-OPEN", "ASK-GAPS")


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


def _p90(v):
    s = sorted(v)
    return s[min(len(s) - 1, int(0.9 * len(s)))]


def ship_time(log, now=None, hours=24):
    """gate_timing.jsonl (written by sync.record_ship_timing for ships, run_all_tests.record_timing for gate steps). Ship = one `ship`
    row's secs; gate = wall time of one run of step rows (same sha). WARN when the median or p90 of ship_wall rows is over SHIP_MAX_S."""
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
        if r.get("step") == "ship_wall":
            ships.append(secs)
            continue
        if r.get("step") == "ship":
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
    parts = [f"ship_wall n={len(ships)} median {_median(ships):.0f}s p90 {_p90(ships):.0f}s" if ships else "ship_wall no rows"]
    parts.append(f"gate n={len(g)} median {_median(g) / 60:.1f} max {max(g) / 60:.1f} min" if g else "gate no rows")
    if ships and max(_median(ships), _p90(ships)) > SHIP_MAX_S:
        return "WARN", f"{'; '.join(parts)}; ship over {SHIP_MAX_S}s: profile the slowest gate steps in {log.as_posix()}"
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


WAIT_HOURS = 24
WAIT_RE = re.compile(r"approv|until the operator|ask the operator", re.I)
WAIT_FIX = "decide on the default and continue; only money, mainnet, going private, deleting data or a live-tree change wait for him"


def _parse_utc(t):
    try:
        d = datetime.fromisoformat(str(t).replace("Z", "+00:00"))
        return d if d.tzinfo else d.replace(tzinfo=timezone.utc)
    except ValueError:
        return None


def waiting_on_operator(repo, now=None, questions=None):
    """WARN when a raw/ready card older than 24 h has a note or approved_by that waits for the operator, or when an operator question
    has been open longer than 24 h. `questions` = list of {utc, id, prompt} (default: operator_questions.pending_questions())."""
    now = now or datetime.now(timezone.utc)
    cards = []
    for p in sorted((Path(repo) / "MyTradingSys" / "system" / "tasks").glob("*.json")):
        try:
            c = json.loads(p.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            continue
        t = _parse_utc(c.get("created"))
        if c.get("state") in ("raw", "ready") and t and (now - t).total_seconds() > WAIT_HOURS * 3600                 and WAIT_RE.search(f"{c.get('note', '')} {c.get('approved_by', '')}"):
            cards.append(c.get("id", p.stem))
    if questions is None:
        try:
            sys.path.insert(0, str(Path(__file__).resolve().parent))
            import operator_questions
            questions = operator_questions.pending_questions()
        except Exception:
            questions = []
    qs = [q.get("id") or str(q.get("utc", ""))[:16] for q in questions
          if _parse_utc(q.get("utc")) and (now - _parse_utc(q.get("utc"))).total_seconds() > WAIT_HOURS * 3600]
    if not cards and not qs:
        return "OK", "nothing waits on the operator for more than 24 h"
    parts = []
    if cards:
        parts.append(f"{len(cards)} card(s): {', '.join(cards[:10])}")
    if qs:
        parts.append(f"{len(qs)} open question(s): {', '.join(qs[:10])}")
    return "WARN", "; ".join(parts) + f" | fix: {WAIT_FIX}"


def ask_gaps(repo):
    """WARN when operator asks older than 24 h have no card, commit or ledger row, or an OPEN item has no live card (T054 news step sat 33 days)."""
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    import operator_questions
    g = operator_questions.asks_gaps(repo)
    if not g["asks"] and not g["items"]:
        return "OK", "every ask older than 24 h has a card, commit or ledger row; every OPEN item has a live card"
    return "WARN", (f"{len(g['asks'])} ask(s) without card/commit, {len(g['items'])} open item(s) without a live card: "
                    f"{', '.join(i['id'] for i in g['items'][:8])} | fix: python scripts/dev/operator_questions.py gaps")


CONFLICT_WARN = 3   # OURS: more open bug-conflict cards than this = WARN


def conflict_open(repo):
    """WARN when more than CONFLICT_WARN bug-conflict-* cards are open (not done): contradicting instructions nobody settled."""
    open_ids = []
    for p in sorted((Path(repo) / "MyTradingSys" / "system" / "tasks").glob("bug-conflict-*.json")):
        try:
            c = json.loads(p.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            continue
        if c.get("state") != "done":
            open_ids.append(c.get("id", p.stem))
    if len(open_ids) > CONFLICT_WARN:
        return "WARN", f"{len(open_ids)} open conflict card(s) (limit {CONFLICT_WARN}): {', '.join(open_ids[:6])} | fix: operator picks the winner, then fix the loser's text and tasks.py done"
    return "OK", f"{len(open_ids)} open conflict card(s)"


BROADCAST_WARN_H = 6     # OURS: a HIGH broadcast needing action (never acked, or `told` expired) on a recently seen host this long = WARN
BROADCAST_SEEN_H = 24


def broadcast_check(repo, rows=None, now=None):
    """WARN when a host seen in the last 24 h has a HIGH broadcast at `none` or expired `told` for over 6 h (operator 2026-10-25:
    broadcasts are only delivered by Claude prompt hooks, so a host without a session, like the live Lenovo, never acked one).
    rows = mts_signal records (default: fetched from the signals branch). Names host and id; `aud top` broadcasts are skipped."""
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    import mts_signal as S
    if rows is None:
        h = S.ensure(repo)
        if h is None:
            return "unavailable", "no origin for the signals branch"
        rows = S.load(h)
    at = now or datetime.now(timezone.utc)
    stale = []
    for host in sorted(S.hosts_active(rows, BROADCAST_SEEN_H, at)):
        for p in S.pending([r for r in rows if r.get("aud") != "top"], host, at):
            if p["hours"] > BROADCAST_WARN_H:
                stale.append(f"{host} {p['id']} ({p['state']}, {p['hours']:.0f} h)")
    if not stale:
        return "OK", f"no HIGH broadcast waits over {BROADCAST_WARN_H} h on a host seen in the last {BROADCAST_SEEN_H} h"
    return "WARN", "; ".join(stale[:8]) + " | fix: python scripts/dev/mts_signal.py pending --host <host>; run the cmd there, then ack <id> done (no session on that host: run it by hand)"

STALE_CLAIM_MAX = 5      # OURS: reports 10-23..10-25 counted 18, 18 and 22 stale claims; each one blocks its task for every login
SCRATCH_RE = re.compile(r"(^|/)_scratch[^/]*$|(^runtime_data|^MyTradingSys/research)/.*ship[^/]*\.log$|(^|/)[^/]*_ship\.log$")


def stale_claims(repo, claims=None, now=None):
    """WARN when more than 5 open claims are over 24 h old. claims = [(slug, {epoch, host, account})] (default: sync.open_claims)."""
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    import sync as Y
    if claims is None:
        claims = Y.open_claims(Path(repo))
    t = (now or datetime.now(timezone.utc)).timestamp()
    old = sorted((slug for slug, kv in claims if kv.get("epoch") and (t - int(kv["epoch"])) / 3600 > Y.STALE_HOURS))
    if len(old) > STALE_CLAIM_MAX:
        return "WARN", f"{len(old)} claims over {Y.STALE_HOURS} h old (limit {STALE_CLAIM_MAX}): {', '.join(old[:6])} | fix: python scripts/dev/sync.py release <slug> from the owner host, or ask the owner"
    return "OK", f"{len(old)} stale claim(s) of {len(claims)} open"


def scratch_tracked(repo, files=None):
    """WARN when a scratch or ship-log file is tracked (the repo is public; PILOT3 committed scratch ship logs, removed in f97ecc125)."""
    files = tracked(repo) if files is None else files
    bad = sorted(f for f in files if SCRATCH_RE.search(f))
    if bad:
        return "WARN", f"{len(bad)} tracked scratch/ship-log file(s): {', '.join(bad[:5])} | fix: git rm them (public repo, never commit runtime data)"
    return "OK", "no tracked scratch or ship-log files"


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
           ("CONTEXT-GAP", lambda: context_gap(repo)),
           ("WAITING-ON-OPERATOR", lambda: waiting_on_operator(repo, now)),
           ("BROADCAST", lambda: broadcast_check(repo, now=now) if process else ("unavailable", "skipped (--no-process, no network)")),
           ("STALE-CLAIMS", lambda: stale_claims(repo, now=now) if process else ("unavailable", "skipped (--no-process, no network)")),
           ("SCRATCH-TRACKED", lambda: scratch_tracked(repo)), ("CONFLICT-OPEN", lambda: conflict_open(repo)),
           ("ASK-GAPS", lambda: ask_gaps(repo)))
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
    ap.add_argument("--heal", action="store_true", help="run the safe HEAL rows only (HEAL_MAP.md); default is a dry run, --apply makes it real")
    ap.add_argument("--apply", action="store_true", help="with --heal: actually release the claims and park the broadcasts (main checkout stays print-only)")
    a = ap.parse_args()
    sys.stdout.reconfigure(errors="replace")
    if a.heal:
        main_checkout = None
        common = _git(REPO, "rev-parse", "--git-common-dir").stdout.strip()
        if common:
            main_checkout = (Path(REPO) / common).resolve().parent      # the checkout every session loads hooks from
        for l in heal(REPO, out_dir=a.out, dry_run=not a.apply, main_checkout=main_checkout):
            print(l)
    else:
        p, f = run(REPO, a.out, a.memory or default_memory(), not a.no_process, a.hours)
        print(p.read_text(encoding="utf-8").splitlines()[0])
        print(f"{p}: {len(f)} findings")
