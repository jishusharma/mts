"""Score DSA chat replies against fixed scenarios built from past failures.

Workflow (after any change to DSA_SESSION_PROMPT.md or the boot paste):
  1. python scripts/dev/dsa_eval.py sheet            -> writes Dumps/dsa_eval_sheet.md (messages to send, in order)
  2. Fresh DeepSeek chat, paste Dumps/SESSION_PASTE.txt, then send each message in a NEW fresh chat
     (one scenario per chat keeps them independent); copy each reply.
  3. python scripts/dev/dsa_eval.py template         -> writes Dumps/dsa_eval_replies.json; paste each reply in
  4. python scripts/dev/dsa_eval.py score Dumps/dsa_eval_replies.json   -> per-scenario PASS/FAIL, appended to
     MyTradingSys/research/dsa_eval_history.jsonl so a prompt change can be compared with the last run.
Exit code 0 only if every scenario passes.
"""
import json
import re
import sys
import datetime
from pathlib import Path

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parent))
from dsa_eval_scenarios import SCENARIOS  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]
HISTORY = ROOT / "MyTradingSys" / "research" / "dsa_eval_history.jsonl"


def score_reply(sc, reply):
    """Return (passed, [failure strings]) for one scenario and one reply."""
    fails = []
    if not reply or not reply.strip():
        return False, ["empty reply"]
    for pat in sc.get("must", []):
        if not re.search(pat, reply):
            fails.append("missing: " + pat)
    for pat in sc.get("must_not", []):
        m = re.search(pat, reply)
        if m:
            fails.append("forbidden: " + pat + " -> " + repr(m.group(0)[:60]))
    mb = sc.get("max_blocks")
    if mb is not None:
        blocks = len(re.findall(r"(?m)^```", reply)) // 2
        if blocks > mb:
            fails.append("blocks: %d > %d" % (blocks, mb))
    return (not fails), fails


def score_all(replies):
    rows = []
    for sc in SCENARIOS:
        ok, fails = score_reply(sc, replies.get(sc["id"], ""))
        rows.append({"id": sc["id"], "pass": ok, "fails": fails})
    return rows


def write_lf(path, text):
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(text)


def cmd_sheet():
    out = ["# DSA eval sheet", "", "One fresh chat per message, after pasting Dumps/SESSION_PASTE.txt.", ""]
    for sc in SCENARIOS:
        out += ["## " + sc["id"], "Source: " + sc["source"], "", sc["message"], ""]
    p = ROOT / "Dumps" / "dsa_eval_sheet.md"
    write_lf(p, "\n".join(out))
    print("wrote", p)


def cmd_template():
    p = ROOT / "Dumps" / "dsa_eval_replies.json"
    write_lf(p, json.dumps({sc["id"]: "" for sc in SCENARIOS}, indent=1) + "\n")
    print("wrote", p)


def cmd_score(path):
    replies = json.loads(Path(path).read_text(encoding="utf-8-sig"))
    rows = score_all(replies)
    for r in rows:
        print("%-5s %s" % ("PASS" if r["pass"] else "FAIL", r["id"]))
        for f in r["fails"]:
            print("        " + f)
    n = sum(r["pass"] for r in rows)
    print("\nSCORE: %d/%d" % (n, len(rows)))
    prev = None
    if HISTORY.exists():
        lines = HISTORY.read_text(encoding="utf-8").strip().splitlines()
        prev = json.loads(lines[-1]) if lines else None
    if prev:
        print("previous run %s: %d/%d" % (prev["ts"], prev["passed"], prev["total"]))
    rec = {"ts": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%MZ"),
           "passed": n, "total": len(rows), "failed": [r["id"] for r in rows if not r["pass"]]}
    HISTORY.parent.mkdir(parents=True, exist_ok=True)
    with open(HISTORY, "a", encoding="utf-8", newline="\n") as fh:
        fh.write(json.dumps(rec) + "\n")
    return 0 if n == len(rows) else 1


def main(argv):
    if len(argv) >= 2 and argv[1] == "sheet":
        return cmd_sheet() or 0
    if len(argv) >= 2 and argv[1] == "template":
        return cmd_template() or 0
    if len(argv) >= 3 and argv[1] == "score":
        return cmd_score(argv[2])
    print(__doc__)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv))
