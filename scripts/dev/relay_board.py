"""Claude-GPT relay board: shared notes both sides read, and the one-screen view of what is flowing between them.

  python scripts/dev/relay_board.py notes [--all]                    # open notes (or all)
  python scripts/dev/relay_board.py add --from jis --to gpt "text"   # append a note to system/RELAY_NOTES.md
  python scripts/dev/relay_board.py close N003 [--reply "text"]
  python scripts/dev/relay_board.py show                             # the board as JSON (what the Control Room embeds)

Notes live in git (MyTradingSys/system/RELAY_NOTES.md) because that is the only channel Codex/GPT can read; codex_pack.py
copies the open notes addressed to gpt/all into every pack. The Control Room renders this board; it never edits it.
"""
import argparse
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parent))
HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
NOTES = "MyTradingSys/system/RELAY_NOTES.md"
SIDES = ("jis", "claude", "gpt", "all")
HDR = re.compile(r"^## (N\d+) \| (\S+) \| from=(\w+) \| to=(\w+) \| status=(open|done)\s*$")


def parse(text):
    """RELAY_NOTES.md -> list of {id, at, frm, to, status, text, reply}. Body runs to the next '## N...' header;
    a line starting 'Reply:' ends the text and starts the reply."""
    out, cur = [], None
    for line in text.splitlines():
        m = HDR.match(line)
        if m:
            cur = {"id": m[1], "at": m[2], "frm": m[3], "to": m[4], "status": m[5], "_b": []}
            out.append(cur)
        elif cur is not None and line != "# END":
            cur["_b"].append(line)
    for n in out:
        body = "\n".join(n.pop("_b")).strip()
        txt, _, rep = body.partition("\nReply:")
        if txt.startswith("Reply:"):
            txt, rep = "", txt[6:]
        n["text"], n["reply"] = txt.strip(), rep.strip()
    return out


def load(repo=REPO):
    p = Path(repo) / NOTES
    return parse(p.read_text(encoding="utf-8")) if p.exists() else []


def open_for(notes, side):
    return [n for n in notes if n["status"] == "open" and n["to"] in (side, "all")]


def next_id(notes):
    return "N%03d" % (max([int(n["id"][1:]) for n in notes] + [0]) + 1)


def add(repo, frm, to, text, now=None):
    if frm not in SIDES[:3] or to not in SIDES:
        raise SystemExit(f"relay_board: from in {SIDES[:3]}, to in {SIDES}")
    if not text.strip() or text.lstrip().startswith(("## N", "Reply:")):
        raise SystemExit("relay_board: empty note, or text that looks like a header")
    notes = load(repo)
    nid = next_id(notes)
    at = (now or datetime.now(timezone.utc)).strftime("%Y-%m-%dT%H:%MZ")
    p = Path(repo) / NOTES
    body = p.read_text(encoding="utf-8").rstrip("\n") if p.exists() else ""
    body = re.sub(r"\n# END$", "", body).rstrip("\n")
    p.write_text(f"{body}\n\n## {nid} | {at} | from={frm} | to={to} | status=open\n{text.strip()}\n", encoding="utf-8", newline="\n")
    return nid


def close(repo, nid, reply=""):
    p = Path(repo) / NOTES
    lines, hit, i = p.read_text(encoding="utf-8").split("\n"), False, 0
    while i < len(lines):
        m = HDR.match(lines[i])
        if m and m[1] == nid:
            lines[i] = lines[i].replace("status=open", "status=done")
            hit = True
            if reply:
                j = i + 1
                while j < len(lines) and not lines[j].startswith("## N"):
                    j += 1
                while j > i + 1 and not lines[j - 1].strip():
                    j -= 1
                lines[j:j] = ["Reply: " + reply.strip()]
        i += 1
    if not hit:
        raise SystemExit(f"relay_board: no note {nid}")
    p.write_text("\n".join(lines), encoding="utf-8", newline="\n")


def tail_jsonl(path, n):
    if not path.exists():
        return []
    rows = []
    for line in path.read_text(encoding="utf-8").splitlines()[-n:]:
        try:
            rows.append(json.loads(line))
        except ValueError:
            pass
    return rows


def claims(repo):
    out = []
    d = Path(repo) / "MyTradingSys/system/claims"
    for f in sorted(d.glob("*.md")) if d.exists() else []:
        kv = dict(l.split(": ", 1) for l in f.read_text(encoding="utf-8").splitlines() if ": " in l)
        out.append({"task": kv.get("task", f.stem), "host": kv.get("host", "?"), "account": kv.get("account", "?"),
                    "epoch": int(kv["epoch"]) if kv.get("epoch", "").isdigit() else 0})
    return out


def gpt_lane(repo, now):
    """GPT lane health + moved/paused cards (lane_health.py); a failure here must not blank the whole relay section."""
    try:
        import lane_health
        return lane_health.view(repo, now=now)
    except Exception as e:   # noqa: BLE001
        return {"status": "unknown", "reason": f"lane health unreadable: {e}", "rerouted": [], "paused": []}


def gpt_usage(repo):
    """What the Codex lab's runs really cost (codex_run.py writes MyTradingSys/system/codex_usage.json with each run): effective model and
    effort, tokens, allowance points, and the lab's spend against its caps. {} when absent or unreadable."""
    try:
        d = json.loads((Path(repo) / "MyTradingSys/system/codex_usage.json").read_text(encoding="utf-8"))
        return d if isinstance(d, dict) else {}
    except (OSError, ValueError):
        return {}


def board(repo=REPO, cards=None, now=None):
    """What is flowing between Claude and GPT right now. `cards` = tasks.summary(repo)["rows"] (passed in to avoid a second load)."""
    repo, now = Path(repo), now or datetime.now(timezone.utc)
    cards = cards or []
    lanes = {}
    for c in cards:
        k = "gpt" if c["lane"] == "CODEX" else "claude" if c["lane"] in ("SONNET", "HAIKU", "OPUS") else "desk"
        lanes.setdefault(k, {"ready": 0, "other": 0, "next": []})
        if c["state"] == "ready":
            lanes[k]["ready"] += 1
            if len(lanes[k]["next"]) < 4:
                lanes[k]["next"].append({"id": c["id"], "title": c["title"], "lane": c["lane"], "prio": c["prio"]})
        else:
            lanes[k]["other"] += 1
    notes = load(repo)
    reports = sorted((repo / "MyTradingSys/research/layer_lab/reports").glob("2*.md"), reverse=True)[:5]
    runs = tail_jsonl(repo / "MyTradingSys/system/relay_runs.jsonl", 5)[::-1]
    age = lambda e: round((now.timestamp() - e) / 3600, 1) if e else None
    return {"notes_open": [n for n in notes if n["status"] == "open"],
            "notes_done": [n for n in notes if n["status"] == "done"][-3:][::-1],
            "lanes": lanes,
            "claims": [{**c, "age_h": age(c["epoch"])} for c in claims(repo)],
            "runs": [{"utc": r.get("utc"), "host": r.get("host"), "account": r.get("account"), "session": r.get("session"),
                      "state": r.get("state")} for r in runs],
            "gpt_reports": [f.name for f in reports],
            "gpt_lane": gpt_lane(repo, now),
            "gpt_usage": gpt_usage(repo)}


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("notes"); s.add_argument("--all", action="store_true")
    s = sub.add_parser("add"); s.add_argument("--from", dest="frm", required=True); s.add_argument("--to", required=True); s.add_argument("text")
    s = sub.add_parser("close"); s.add_argument("id"); s.add_argument("--reply", default="")
    sub.add_parser("show")
    a = ap.parse_args(argv)
    if a.cmd == "notes":
        for n in load():
            if a.all or n["status"] == "open":
                print(f"{n['id']} {n['at']} {n['frm']}->{n['to']} [{n['status']}] {n['text'][:100]}")
    elif a.cmd == "add":
        print("added", add(REPO, a.frm, a.to, a.text))
    elif a.cmd == "close":
        close(REPO, a.id, a.reply)
        print("closed", a.id)
    else:
        import tasks
        print(json.dumps(board(REPO, tasks.summary(REPO)["rows"]), indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
