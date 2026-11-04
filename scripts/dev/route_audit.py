"""route_audit.py: every shipped Result carries a route tag (`Next:`) that points somewhere real (d-route-tag-every-session-1104).

  python scripts/dev/route_audit.py check [--days 7] [--ref origin/fast-track] [--stale-h 72]   # exit 1 when any finding
  python scripts/dev/route_audit.py audit [--days 7] [--top 10]   # pre-gate history: routing evidence in the text (AUDIT.md method)

Grammar (shared by sync.py ship and tasks.py done): `Next: <card-id> | <stage> | END: <reason>`; tasks.py done also takes
new:"<title>" and files that card raw. Stages: PROMOTION_PIPELINE.md 1-5 plus BACKTEST_CANDIDATES.
check flags, per Result commit after the gate went live (the first trunk commit of this file): no Next on it or on a later commit
of the same ship (same author, descendant, within SHIP_GROUP_H); a Next card id with no card file; a Next card still open and
untouched for --stale-h hours. Run at Supervisor and coordinator load (no scheduler, SCHEDULING_POLICY.md).
"""
import argparse
import json
import re
import subprocess
import sys
from datetime import datetime, timedelta, timezone

TRUNK = "fast-track"
TASKS = "MyTradingSys/system/tasks"
STAGES = ("research", "pre-reg", "backtest", "shadow", "testnet", "backtest_candidates")   # PROMOTION_PIPELINE.md stages 1-5
SHIP_GROUP_H = 12          # OURS: a Next on a later commit of the same ship (same author, descendant) covers the earlier ones
CARD_ID = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_.-]{1,80}$")
NEXT_LINE = re.compile(r"^\s*Next:\s*(.*)$", re.M | re.I)
RESULT_LINE = re.compile(r"^\s*Result:", re.M | re.I)
# Tool bookkeeping commits (sync.py claim/release/heartbeat/LAYERS regen, desk.py, context_gap.py, lane_health.py, tasks.py) and
# reverts (a red trunk's fix ships in minutes) need no route tag.
EXEMPT_SUBJECT = re.compile(r"^(Merge |Revert |revert |claim |release |heartbeat |ship: regenerated LAYERS\.md|"
                            r"fold context into card |lane health|signals?\b|desk (task|assign|done|take)\b|task: \S+ (done|closed))")
# A commit that only touches cards, claims or LAYERS.md is routing itself: the card is where the work goes next.
EXEMPT_PATH = re.compile(r"^(MyTradingSys/system/tasks/|MyTradingSys/system/claims/|MyTradingSys/system/LAYERS\.md$)")
FIX = 'add a line `Next: <card-id | stage | END: reason>` (sync.py ship --next "..."; tasks.py new files a card)'


def git(repo, *args, check=True):
    r = subprocess.run(["git", "-C", str(repo), *args], capture_output=True, text=True, encoding="utf-8", errors="replace")
    if check and r.returncode:
        raise SystemExit(f"route_audit: git {' '.join(args[:3])} failed: {r.stderr.strip()[:200]}")
    return r.stdout


def parse_next(value, allow_new=False):
    """('end'|'stage'|'card'|'new', value) for a valid tag, else (None, why)."""
    v = (value or "").strip()
    if not v:
        return None, "empty Next"
    if re.match(r"^END\s*:", v, re.I):
        reason = v.split(":", 1)[1].strip()
        return ("end", reason) if reason else (None, "END needs a reason (Next: END: <why nothing follows>)")
    if re.match(r"^new\s*:", v, re.I):
        title = v.split(":", 1)[1].strip().strip('"').strip()
        if not allow_new:
            return None, 'new:"<title>" only works in tasks.py done; name the filed card id here'
        return ("new", title) if title else (None, 'new: needs a title')
    tok = re.split(r"[\s,;(]+", v, maxsplit=1)[0].strip("`'\".")
    if tok.lower() in STAGES:
        return "stage", tok.lower()
    if CARD_ID.match(tok):
        return "card", tok
    return None, f"Next {v[:40]!r} is not a card id, stage or END: <reason>"


def next_tags(body):
    return [m.strip() for m in NEXT_LINE.findall(body or "")]


def exempt(subject, files):
    return bool(EXEMPT_SUBJECT.match(subject or "")) or (bool(files) and all(EXEMPT_PATH.match(f) for f in files))


def commits(repo, rev_range, since=None):
    """Non-merge commits in rev_range: dicts sha, at (aware datetime), author, subject, body, files, added."""
    extra = [f"--since={since.isoformat()}"] if since else []
    raw = git(repo, "log", "--no-merges", *extra, "--format=%x1e%H%x1f%cI%x1f%ae%x1f%s%x1f%B%x1d", "--name-status", rev_range)
    out = []
    for rec in raw.split("\x1e"):
        if not rec.strip():
            continue
        head, _, tail = rec.partition("\x1d")
        sha, at, author, subject, body = (head.split("\x1f") + [""] * 5)[:5]
        files, added = [], []
        for line in tail.splitlines():
            parts = line.split("\t")
            if len(parts) >= 2 and parts[0]:
                files.append(parts[-1])
                if parts[0].startswith("A"):
                    added.append(parts[-1])
        out.append({"sha": sha, "at": datetime.fromisoformat(at), "author": author, "subject": subject, "body": body,
                    "files": files, "added": added})
    return out


def card_ids(repo, ref):
    names = git(repo, "ls-tree", "-r", "--name-only", ref, "--", TASKS, check=False).splitlines()
    return {n.rsplit("/", 1)[-1][:-5]: n for n in names if n.endswith(".json")}


def gate_start(repo, ref):
    """When the Next gate went live on ref: the commit that added this file (None = not on ref yet: no floor)."""
    at = git(repo, "log", ref, "--diff-filter=A", "--format=%cI", "--", "scripts/dev/route_audit.py", check=False).split()
    return datetime.fromisoformat(at[-1]) if at else None


def covered_by_later(repo, c, tagged):
    for t in tagged:
        if t["author"] == c["author"] and c["at"] <= t["at"] <= c["at"] + timedelta(hours=SHIP_GROUP_H) \
                and subprocess.run(["git", "-C", str(repo), "merge-base", "--is-ancestor", c["sha"], t["sha"]]).returncode == 0:
            return True
    return False


def check(repo, ref, days, stale_h, now=None):
    """Findings list of (kind, sha, subject, detail) for shipped Result commits on ref."""
    now = now or datetime.now(timezone.utc)
    floor = now - timedelta(days=days)
    start = gate_start(repo, ref)
    if start and start > floor:
        floor = start
    cs = [c for c in commits(repo, ref, since=floor) if c["at"] >= floor and RESULT_LINE.search(c["body"])
          and not exempt(c["subject"], c["files"])]
    tagged = [c for c in cs if next_tags(c["body"])]
    ids = card_ids(repo, ref)
    out, seen_cards = [], {}
    for c in cs:
        tags = next_tags(c["body"])
        if not tags:
            if not covered_by_later(repo, c, tagged):
                out.append(("UNTAGGED", c["sha"][:9], c["subject"], FIX))
            continue
        for t in tags:
            kind, val = parse_next(t)
            if kind is None:
                out.append(("BAD-TAG", c["sha"][:9], c["subject"], val))
            elif kind == "card" and val not in ids:
                out.append(("NO-CARD", c["sha"][:9], c["subject"], f"Next card {val} has no file in {TASKS}; tasks.py new ... --id {val}"))
            elif kind == "card":
                seen_cards.setdefault(val, c)
    for cid, c in seen_cards.items():
        path = ids[cid]
        try:
            card = json.loads(git(repo, "show", f"{ref}:{path}"))
        except (ValueError, SystemExit):
            continue
        if card.get("state") in ("done", "dropped"):
            continue
        last = git(repo, "log", "-1", "--format=%cI", ref, "--", path).strip()
        if last and now - datetime.fromisoformat(last) > timedelta(hours=stale_h):
            out.append(("STALE-CARD", c["sha"][:9], c["subject"], f"Next card {cid} ({card.get('state')}) untouched {stale_h}h+: refine, run or drop it"))
    return out, len(cs)


# --- audit: pre-gate history, where no commit carried a Next line yet -------------------------------------------------------
ROUTE_TEXT = re.compile(r"\bnext:|\btasks\.py new\b|\bcards? (filed|added|opened|created)\b|\bfiled\b|\bfollow-?on\b|\bdead[- ]end\b|"
                        r"\bEND:|BACKTEST_CANDIDATES|\bPRE_REG\b|\btestnet candidate|\bshadow\b|\bhand-?over\b|\bqueued?\b|"
                        r"\bnext step|\bcompanion card|\b(gemini|codex|gpt)[- ](blind|rederive|spec)", re.I)
OUTPUT = re.compile(r"(^MyTradingSys/research/.*/(RESULT|REPORT|VERDICT|AUDIT|DEV_CHECK|FINDINGS)[^/]*\.md$)|(^scripts/.*\.py$)|"
                    r"(^MyTradingSys/.*\.py$)")


def card_texts(repo, ref):
    """[(created, lowercase json text)] of every card on ref (open, done, archived): a card made after an output that names it is
    downstream; the card that ordered the work names it too but was created before (upstream)."""
    paths = sorted(set(card_ids(repo, ref).values()))
    if not paths:
        return []
    r = subprocess.run(["git", "-C", str(repo), "cat-file", "--batch"], input="".join(f"{ref}:{p}\n" for p in paths),
                       capture_output=True, text=True, encoding="utf-8", errors="replace")
    out = []
    for chunk in re.split(r"^[0-9a-f]{40} blob \d+$", r.stdout, flags=re.M):
        m = re.search(r'"created":\s*"([^"]+)"', chunk)
        if m:
            try:
                at = datetime.fromisoformat(m.group(1).replace("Z", "+00:00"))
                out.append((at if at.tzinfo else at.replace(tzinfo=timezone.utc), chunk.lower()))
            except ValueError:
                pass
    return out


def picked_up(c, outs, cards):
    """True when a card created after the commit names one of its output files or its research folder."""
    blob = "\n".join(t for at, t in cards if at > c["at"])
    for f in outs:
        name = f.rsplit("/", 1)[-1].lower()
        # built from a stem so wiring_scan does not read the generic name as a reference to a real study script
        generic = ("result.md", "report.md", "study.py", "analyze" + ".py")
        keys = [] if name in generic else [name]
        m = re.search(r"/research/([^/]+)/", f)
        if m:
            keys.append(m.group(1).lower())
        if any(k and k in blob for k in keys):
            return True
    return False


def audit_rows(cs, cards=()):
    """Classify Result commits: chore | named (Next line, new card file, routing words) | picked-up (a card names the output later)
    | orphan-output (a study/verdict/tool nothing names) | unrouted-other (no output file, no route)."""
    rows = []
    for c in cs:
        if not RESULT_LINE.search(c["body"]):
            continue
        if exempt(c["subject"], c["files"]):
            rows.append((c, "chore", ""))
            continue
        new_cards = [f for f in c["added"] if f.startswith(TASKS + "/")]
        if next_tags(c["body"]):
            rows.append((c, "named", "Next line"))
        elif new_cards:
            rows.append((c, "named", f"filed {len(new_cards)} card(s)"))
        elif ROUTE_TEXT.search(c["subject"] + "\n" + c["body"]):
            rows.append((c, "named", "routing words: " + ROUTE_TEXT.search(c["subject"] + "\n" + c["body"]).group(0)))
        else:
            outs = [f for f in c["files"] if OUTPUT.search(f) and not re.search(r"(^|/)test_[^/]*\.py$", f)]
            new_tools = [f for f in c["added"] if OUTPUT.search(f) and f.endswith(".py") and "/test_" not in "/" + f]
            kind = "unrouted-other" if not outs else "picked-up" if picked_up(c, outs, cards) else "orphan-output"
            rows.append((c, kind, ", ".join((new_tools or outs)[:2])))
    return rows


def should_have(c, what):
    f = what.split(",")[0]
    if f.endswith(".py"):
        return "[GEMINI] blind read card of the new tool (feeder rule A-20261104-1)"
    if "/RESULT" in f or "/VERDICT" in f or "/REPORT" in f:
        return "BACKTEST_CANDIDATES row or Next: END: <no edge> + the [GEMINI] blind read"
    if "/AUDIT" in f or "/FINDINGS" in f:
        return "one fix card per finding (tasks.py new)"
    return "a follow-on card or Next: END: <reason>"


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sp = ap.add_subparsers(dest="cmd", required=True)
    for name in ("check", "audit"):
        p = sp.add_parser(name)
        p.add_argument("--days", type=float, default=7)
        p.add_argument("--ref", default=f"origin/{TRUNK}")
        p.add_argument("--repo", default=".")
        p.add_argument("--stale-h", type=float, default=72)
        p.add_argument("--top", type=int, default=10)
    a = ap.parse_args(argv)
    if a.cmd == "check":
        found, n = check(a.repo, a.ref, a.days, a.stale_h)
        for kind, sha, subj, detail in found:
            print(f"{kind} {sha} {subj[:70]} | {detail}")
        print(f"route_audit check: {len(found)} finding(s) over {n} gated Result commit(s), {a.days:g} d on {a.ref}")
        return 1 if found else 0
    since = datetime.now(timezone.utc) - timedelta(days=a.days)
    rows = audit_rows(commits(a.repo, a.ref, since=since), card_texts(a.repo, a.ref))
    counts = {}
    for _, k, _ in rows:
        counts[k] = counts.get(k, 0) + 1
    print(f"route_audit audit: {len(rows)} Result commit(s) in {a.days:g} d on {a.ref}: " + ", ".join(f"{k}={v}" for k, v in sorted(counts.items())))
    orphans = sorted((r for r in rows if r[1] == "orphan-output"),
                     key=lambda r: (not any(f.endswith(".py") for f in r[0]["added"]), -len(r[0]["files"])))
    for c, _, what in orphans[:a.top]:
        print(f"ORPHAN {c['sha'][:9]} {c['at']:%m-%d} {c['subject'][:80]} | {what} | next should be: {should_have(c, what)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
