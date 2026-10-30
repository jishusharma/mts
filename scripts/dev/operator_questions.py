"""Query the operator's verbatim questions log (kept outside the repo; the repo is public).

The log is written by the UserPromptSubmit hook at ~/.claude/hooks/operator_questions.py, one JSON line per
prompt: {utc, session_id, cwd, tags, prompt}. Tag a question by putting #word in it (e.g. "#halt ...").

  python scripts/dev/operator_questions.py list [--tag halt] [--grep TEXT] [--since 2026-10-17] [--session ID] [--limit 50]
  python scripts/dev/operator_questions.py tags
  python scripts/dev/operator_questions.py backfill --transcript PATH   # add prompts from an earlier session transcript

Log path: env OPERATOR_QUESTIONS_FILE, default ~/.claude/operator_questions.jsonl.
"""
import argparse
import json
import os
import re
import sys
from collections import Counter
from pathlib import Path

DEFAULT_LOG = Path.home() / ".claude" / "operator_questions.jsonl"
DEFAULT_DECISIONS = Path(__file__).resolve().parents[2] / "MyTradingSys" / "system" / "OPERATOR_DECISIONS.md"
TAG_RE = re.compile(r"(?<![\w&])#([A-Za-z][\w-]{0,40})")
AUTOMATED_HEADS = ("This session is being continued from a previous conversation", "<task-notification>",
                   "<system-reminder>", "<cross-session-message", "You are the MTS OVERNIGHT SUPER-SESSION COORDINATOR")
MAX_TYPED_CHARS = 3000  # a typed question is short; longer prompts are pasted reports or briefs

WEIGHT_ORDER = {"ROUTINE": 0, "IMPORTANT": 1, "CRUCIAL": 2, "CRITICAL": 3, "B-SHARED": 4}


def is_automated(text):
    """Not typed by the operator: harness events, pasted text from other sessions, long pasted reports or briefs."""
    return text.lstrip().startswith(AUTOMATED_HEADS) or "<pasted_content" in text or len(text) > MAX_TYPED_CHARS


def log_path():
    return Path(os.environ.get("OPERATOR_QUESTIONS_FILE") or DEFAULT_LOG)


def decisions_path():
    return Path(os.environ.get("OPERATOR_DECISIONS_FILE") or DEFAULT_DECISIONS)


def parse_decisions(path=None):
    """Parse OPERATOR_DECISIONS.md. Returns list of dicts:
    {id, asked, stage, question, recommended, answer, state, weight, options, raw_json}"""
    p = Path(path) if path else decisions_path()
    if not p.is_file():
        return []
    rows = []
    text = p.read_text(encoding="utf-8")
    for block in re.split(r"^## ", text, flags=re.M)[1:]:
        lines = block.splitlines()
        head = [x.strip() for x in lines[0].split("|")]
        if len(head) < 2 or not head[1].startswith("asked "):
            continue
        qid = head[0]
        asked = head[1][6:].strip()
        stage = head[2] if len(head) > 2 else ""

        # Extract JSON block if present
        meta = {}
        m_json = re.search(r"```json\s*(\{.*?\})\s*```", block, re.DOTALL)
        if m_json:
            try:
                meta = json.loads(m_json.group(1))
            except Exception:
                pass

        fields = {k: v.strip() for k, v in re.findall(r"^(Recommended|Answer|Applied|Operator note \(verbatim\)):\s*(.*)$", block, re.M)}
        question = next((x.strip() for x in lines[1:] if x.strip() and not x.startswith("Recommended:") and not x.startswith("Answer:")), "")
        answer = fields.get("Answer", "")

        # State resolution
        if not answer or answer.startswith("(none yet)"):
            state = "open"
        elif fields.get("Applied", "").startswith("(not yet"):
            state = "answered, not applied"
        else:
            state = "applied"

        weight = str(meta.get("weight") or "").upper()
        if not weight:
            # fallback: Stage Live testnet defaults high, else ROUTINE
            weight = "CRITICAL" if stage.lower() == "live testnet" else "ROUTINE"

        rows.append({
            "id": qid,
            "asked": asked,
            "stage": stage,
            "question": question,
            "title": meta.get("title", question),
            "recommended": fields.get("Recommended", ""),
            "answer": answer,
            "state": state,
            "weight": weight,
            "no_auto": "NO AUTO-APPLY" in lines[0] or meta.get("no_auto_apply", False),
        })
    return rows


def pending_questions(log_path=None, decisions_path=None):
    """Typed operator questions with no recorded decision in OPERATOR_DECISIONS.md, ranked,
    with pasted reports and harness events filtered out (RU7).
    Also includes questions already in OPERATOR_DECISIONS.md with state == 'open'."""
    lp = Path(log_path) if log_path else globals()["log_path"]()
    dec_rows = parse_decisions(decisions_path)

    # Decisions with an answer recorded (applied or answered)
    answered_decisions = [d for d in dec_rows if d["state"] in ("applied", "answered, not applied")]
    open_decisions = [d for d in dec_rows if d["state"] == "open"]

    answered_texts = [d["title"].lower().strip() for d in answered_decisions if d["title"]]
    answered_texts += [d["question"].lower().strip() for d in answered_decisions if d["question"]]

    def is_decision_answered(prompt):
        low = prompt.lower().strip()
        for at in answered_texts:
            if at and (at in low or low in at):
                return True
        return False

    def match_open_decision(prompt):
        low = prompt.lower().strip()
        for od in open_decisions:
            ot = od["title"].lower().strip()
            oq = od["question"].lower().strip()
            if (ot and (ot in low or low in ot)) or (oq and (oq in low or low in oq)):
                return od
        return None

    raw_rows = read_rows(lp)
    # Filter out automated, pasted, or overlong items
    typed_rows = [r for r in raw_rows if not is_automated(r.get("prompt", ""))]

    matched_open_ids = set()
    result = []

    for r in typed_rows:
        prompt = r.get("prompt", "").strip()
        if is_decision_answered(prompt):
            continue
        od = match_open_decision(prompt)
        weight = "ROUTINE"
        qid = ""
        stage = ""
        if od:
            weight = od.get("weight", "ROUTINE")
            qid = od.get("id", "")
            stage = od.get("stage", "")
            matched_open_ids.add(od.get("id"))
        result.append({
            "utc": r.get("utc", ""),
            "session_id": r.get("session_id", ""),
            "tags": r.get("tags", []),
            "prompt": prompt,
            "weight": weight,
            "id": qid,
            "stage": stage,
        })

    # Include any open questions in OPERATOR_DECISIONS.md that didn't appear in the local log file
    for od in open_decisions:
        if od["id"] not in matched_open_ids:
            result.append({
                "utc": od.get("asked", ""),
                "session_id": "",
                "tags": [od.get("stage", "").lower()] if od.get("stage") else [],
                "prompt": od.get("question") or od.get("title", ""),
                "weight": od.get("weight", "ROUTINE"),
                "id": od["id"],
                "stage": od.get("stage", ""),
            })

    # Rank by weight (higher weight first), then date/utc
    result.sort(key=lambda x: (-WEIGHT_ORDER.get(x.get("weight", "ROUTINE"), 0), x.get("utc", "")))
    return result



def read_rows(path):
    if not path.exists():
        return []
    rows = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.strip():
            rows.append(json.loads(line))
    return rows


def show(row):
    tags = ",".join(row.get("tags", [])) or "-"
    print(f"{row['utc']}  [{tags}]  session={row.get('session_id', '')[:8]}")
    print(f"  {row['prompt']}")


def cmd_list(args):
    rows = read_rows(log_path())
    if args.tag:
        wanted = {t.lower().lstrip("#") for t in args.tag}
        rows = [r for r in rows if wanted & set(r.get("tags", []))]
    if args.grep:
        rows = [r for r in rows if args.grep.lower() in r["prompt"].lower()]
    if args.since:
        rows = [r for r in rows if r["utc"][:10] >= args.since]
    if args.session:
        rows = [r for r in rows if r.get("session_id", "").startswith(args.session)]
    rows = rows[-args.limit:] if args.limit else rows
    print(f"{len(rows)} question(s) from {log_path()}")
    for r in rows:
        show(r)


def cmd_tags(_args):
    counts = Counter(t for r in read_rows(log_path()) for t in r.get("tags", []))
    print(f"{sum(counts.values())} tag uses in {log_path()}")
    for tag, n in counts.most_common():
        print(f"  #{tag}: {n}")


def transcript_prompts(path):
    """Yield (utc, session_id, prompt) for real operator text messages in a Claude Code transcript."""
    for line in Path(path).read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        d = json.loads(line)
        if d.get("type") != "user":
            continue
        content = d.get("message", {}).get("content")
        if isinstance(content, list):  # tool results and pasted blocks come as lists; keep plain text items only
            texts = [c.get("text", "") for c in content if isinstance(c, dict) and c.get("type") == "text"]
            content = "\n".join(t for t in texts if t) if texts and not any(
                isinstance(c, dict) and c.get("type") == "tool_result" for c in content) else None
        if isinstance(content, str) and content.lstrip().startswith(("<system-reminder>", "Launching skill")):
            continue  # injected context, not typed by the operator
        if isinstance(content, str) and is_automated(content):
            continue
        if isinstance(content, str) and "\n## User Request\n" in content:
            continue  # a skill body loaded as a user message
        if isinstance(content, str) and content.strip():
            utc = d.get("timestamp", "")[:19] + "Z"
            yield utc, d.get("sessionId", ""), content


def cmd_backfill(args):
    path = log_path()
    existing = {(r["session_id"], r["prompt"]) for r in read_rows(path)}
    added = 0
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8", newline="\n") as fh:
        for utc, sid, prompt in transcript_prompts(args.transcript):
            if (sid, prompt) in existing:
                continue
            row = {"utc": utc, "session_id": sid, "cwd": "", "source": "backfill",
                   "tags": sorted({t.lower() for t in TAG_RE.findall(prompt)}), "prompt": prompt}
            fh.write(json.dumps(row, ensure_ascii=False) + "\n")
            added += 1
    print(f"backfilled {added} prompt(s) into {path}")


def cmd_prune(args):
    """Drop rows that is_automated() flags (pasted reports, harness events) from the log; the removed rows go to --out."""
    path = log_path()
    rows = read_rows(path)
    keep = [r for r in rows if not is_automated(r["prompt"])]
    removed = [r for r in rows if is_automated(r["prompt"])]
    if args.out:
        Path(args.out).write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in removed), encoding="utf-8")
    if args.apply:
        path.write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in keep), encoding="utf-8")
    print(f"{'removed' if args.apply else 'would remove'} {len(removed)}, keep {len(keep)} in {path}")


def cmd_pending(args):
    """Typed operator questions with no recorded decision in OPERATOR_DECISIONS.md, ranked (RU7)."""
    pending = pending_questions()
    if args.json:
        print(json.dumps(pending, indent=2, ensure_ascii=False))
        return
    print(f"{len(pending)} pending question(s) for the operator:")
    for n, r in enumerate(pending, 1):
        tags = ",".join(r.get("tags", [])) or "-"
        qid = f" [{r['id']}]" if r.get("id") else ""
        print(f"{n}. [{r.get('weight', 'ROUTINE')}]{qid} {r.get('utc', '')} tags={tags}")
        print(f"   {r.get('prompt', '')}")

# ---- gaps: asks and open items nobody holds (operator 2026-10-30: T054 news step sat unbuilt 33 days) ----
ASK_RE = re.compile(r"\b(build|add|fix|make|create|implement|research|investigate|wire|need|want|should|please|change|remove|"
                    r"design|show|put|test|ensure|update|move|record|stop|start)\b", re.I)
GAP_STOP = {"about", "there", "their", "would", "could", "should", "which", "these", "those", "where", "while", "being", "think",
            "thing", "things", "really", "please", "again", "right", "first", "other", "after", "before", "still", "going"}
LIVE_ITEM_STATES = ("OPEN", "PARTIAL", "QUEUED")
CARD_DEAD = ("done", "dropped")


def _tokens(text):
    return {w for w in re.findall(r"[a-z0-9]{5,}", text.lower()) if w not in GAP_STOP}


def _utc(t):
    from datetime import datetime, timezone
    try:
        d = datetime.fromisoformat(str(t).replace("Z", "+00:00"))
        return d if d.tzinfo else d.replace(tzinfo=timezone.utc)
    except ValueError:
        return None


def asks_gaps(repo=None, now=None, hours=24, days=14, rows=None, cards=None, commits=None, ledger_text=None, index_text=None):
    """Asks with no card, no commit and no non-OPEN ledger row after `hours`, plus OPEN/PARTIAL/QUEUED items with no live card.
    Link = a card created after the ask or a commit subject after it sharing 3+ words, or a card/ledger row carrying the ask's
    'MM-DD HH:MM' stamp. Returns {"asks": [{utc, prompt}], "items": [{id, state, line}]}. Heuristic by design: lean, no paperwork."""
    import subprocess
    from datetime import datetime, timezone, timedelta
    repo = Path(repo) if repo else Path(__file__).resolve().parents[2]
    now = now or datetime.now(timezone.utc)
    if cards is None:
        cards = []
        for f in sorted((repo / "MyTradingSys" / "system" / "tasks").glob("*.json")):
            try:
                cards.append(json.loads(f.read_text(encoding="utf-8")))
            except (OSError, ValueError):
                pass
    if rows is None:
        rows = read_rows(log_path())
    if ledger_text is None:
        lf = repo / "MyTradingSys" / "research" / "asks_audit_2026-10-30" / "LEDGER.md"
        ledger_text = lf.read_text(encoding="utf-8") if lf.is_file() else ""
    if index_text is None:
        xf = repo / "MyTradingSys" / "items" / "INDEX.md"
        index_text = xf.read_text(encoding="utf-8") if xf.is_file() else ""
    lo, hi = now - timedelta(days=days), now - timedelta(hours=hours)
    cand = []
    for r in rows:
        t, text = _utc(r.get("utc")), (r.get("prompt") or "").strip()
        if t and lo <= t <= hi and len(text) >= 25 and not is_automated(text) and ASK_RE.search(text):
            cand.append((t, text))
    if commits is None:
        commits = []
        if cand:
            try:
                out = subprocess.run(["git", "-C", str(repo), "log", "origin/fast-track", f"--since={min(c[0] for c in cand).isoformat()}",
                                      "--format=%aI\t%s"], capture_output=True, text=True, timeout=60).stdout
                for ln in out.splitlines():
                    a, _, b = ln.partition("\t")
                    if _utc(a):
                        commits.append((_utc(a), b))
            except (OSError, subprocess.SubprocessError):
                pass
    card_info = [(_utc(c.get("created")), _tokens(" ".join(str(c.get(k, "")) for k in ("title", "goal", "note", "refs"))),
                  json.dumps(c)) for c in cards]
    com_info = [(t, _tokens(s)) for t, s in commits]
    ledger_rows = [ln for ln in ledger_text.splitlines() if ln.startswith("|") and "| OPEN |" not in ln]
    gaps = []
    for t, text in cand:
        stamp, tk = f"{t:%m-%d %H:%M}", _tokens(text)
        if any(stamp in ln for ln in ledger_rows) or any(stamp in raw for _, _, raw in card_info):
            continue
        if any(ct and ct >= t and len(tk & ctk) >= 3 for ct, ctk, _ in card_info) or any(ct >= t and len(tk & ctk) >= 3 for ct, ctk in com_info):
            continue
        gaps.append({"utc": t.strftime("%Y-%m-%dT%H:%MZ"), "prompt": text[:110].replace("\n", " ")})
    live = [raw for (_, _, raw), c in zip(card_info, cards) if c.get("state") not in CARD_DEAD]
    items = []
    for ln in index_text.splitlines():
        cols = [x.strip() for x in ln.split("|")]
        if len(cols) >= 4 and cols[1] in LIVE_ITEM_STATES and re.fullmatch(r"[A-Z]\d{3}", cols[0]):
            if not any(re.search(rf"\b{cols[0]}\b", raw) for raw in live):
                items.append({"id": cols[0], "state": cols[1], "line": cols[3][:90]})
    return {"asks": gaps, "items": items}


def cmd_gaps(args):
    g = asks_gaps(hours=args.hours, days=args.days)
    if args.json:
        print(json.dumps(g, indent=2, ensure_ascii=False))
        return
    print(f"ASK-GAPS: {len(g['asks'])} ask(s) older than {args.hours} h with no card/commit/ledger row; "
          f"{len(g['items'])} open item(s) with no live card")
    for a in g["asks"][:8]:
        print(f"  ask {a['utc']} {a['prompt']}")
    for i in g["items"][:8]:
        print(f"  item {i['id']} {i['state']} {i['line']}")
    print("fix: tasks.py new ... --ref <item id or ask stamp 'MM-DD HH:MM'>, or add a ledger row; then rerun")


def main(argv=None):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")  # Windows consoles default to cp1251/cp1252
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)
    ls = sub.add_parser("list")
    ls.add_argument("--tag", action="append")
    ls.add_argument("--grep")
    ls.add_argument("--since")
    ls.add_argument("--session")
    ls.add_argument("--limit", type=int, default=50, help="last N matches; 0 = all")
    ls.set_defaults(fn=cmd_list)
    sub.add_parser("tags").set_defaults(fn=cmd_tags)
    bf = sub.add_parser("backfill")
    bf.add_argument("--transcript", required=True)
    bf.set_defaults(fn=cmd_backfill)
    pr = sub.add_parser("prune", help="drop pasted or automated rows from the log")
    pr.add_argument("--apply", action="store_true", help="write the pruned log (default: dry run)")
    pr.add_argument("--out", help="file to receive the removed rows, for audit")
    pr.set_defaults(fn=cmd_prune)
    pend = sub.add_parser("pending", help="typed operator questions with no recorded decision, ranked")
    pend.add_argument("--json", action="store_true", help="print JSON array")
    pend.set_defaults(fn=cmd_pending)
    gp = sub.add_parser("gaps", help="asks with no card/commit after N hours; open items with no live card")
    gp.add_argument("--hours", type=int, default=24)
    gp.add_argument("--days", type=int, default=14, help="look back this far")
    gp.add_argument("--json", action="store_true")
    gp.set_defaults(fn=cmd_gaps)
    args = p.parse_args(argv)
    args.fn(args)
    return 0


if __name__ == "__main__":
    sys.exit(main())
