"""E2E edge cases for flow-a2 (role_loader + model_guard), run against one code dir.
usage: python e2e_a2.py <code dir with role_loader.py, model_guard.py> <repo with MyTradingSys/system/roles> <label>
Each case plays a session through the real hook: prompts in order, then SessionStart (compaction), then 12 plain prompts
(every-6th reminder), and asks model_guard.role_session about the same transcript."""
import json, os, sys, tempfile
from pathlib import Path

CODE, REPO, LABEL = Path(sys.argv[1]), Path(sys.argv[2]), sys.argv[3]
TMP = Path(tempfile.mkdtemp(prefix="e2e_a2_"))
os.environ["MTS_ROLES_HOME"] = str(TMP / "state")
sys.path.insert(0, str(CODE))
import role_loader as rl                               # noqa: E402
import model_guard as mg                               # noqa: E402
rl.git_fetch = lambda repo: True                       # offline: read role files from the worktree, not trunk
rl.git_show = lambda repo, rel: (Path(repo) / rel).read_text(encoding="utf-8") if (Path(repo) / rel).exists() else None
rl.git_sha8 = lambda repo: "e2e00000"

def hook(prompt, sid, event="UserPromptSubmit"):
    out = rl.handle({"prompt": prompt, "session_id": sid, "hook_event_name": event}, REPO)
    return json.loads(out)["hookSpecificOutput"]["additionalContext"] if out else ""

def loaded(text):
    for line in text.splitlines():
        if line.startswith("ROLE LOADED:"):
            return line.split()[2]
    if "ROLE LOADER (hook): you are " in text:
        return text.split("ROLE LOADER (hook): you are ")[1].split(".")[0]
    return None

LONG = "x" * 3100 + "\nYou are Supervisor."
CASES = [  # id, desc, prompts (first is the session's first prompt), expected: re-injected after compaction?
    ("R01", "explicit `You are Supervisor.`", ["You are Supervisor. Login A."], True),
    ("R02", "this session's bug: fallback from the word revalidat", ["Run the doctor: revalidate the stale pages and report."], False),
    ("R03", "fallback from chart words", ["Here is a chart screenshot of BTC 15m, what do you see?"], False),
    ("R04", "fallback first, then `reload role Eagle_Eyes`", ["Here is a chart screenshot of BTC 15m, what do you see?", "reload role Eagle_Eyes"], True),
    ("R05", "lowercase `you are supervisor.`", ["you are supervisor."], True),
    ("R06", "trigger phrase `I need a pipeliner`", ["I need a pipeliner"], True),
    ("R07", "alias with space `You are Eagle Eyes`", ["You are Eagle Eyes. Read BTC."], True),
    ("R08", "role after a sentence `Hi. You are Supervisor.`", ["Hi. You are Supervisor. Login A."], True),
    ("R09", "negation `You are not the Supervisor`", ["You are not the Supervisor, just answer: what is CI?"], False),
    ("R10", "mention only `ask the pipeliner`", ["please ask the pipeliner what is queued"], False),
    ("R11", "role line after 3000 chars", [LONG], False),
    ("R12", "two roles named", ["You are Supervisor.\nYou are Thinker."], False),
    ("R13", "no role, plain question", ["what is the CI status?"], False),
    ("R14", "explicit role in a LATER prompt", ["what is the CI status?", "You are Thinker. Topic: role flow."], True),
    ("R15", "subagent-style brief `You are Thinker.` first", ["You are Thinker. Topic: the refine trigger."], True),
]

rows, fails = [], 0
for cid, desc, prompts, want in CASES:
    sid = f"{LABEL}-{cid}"
    first = [loaded(hook(p, sid)) for p in prompts]
    comp = hook("", sid, "SessionStart")
    re_role = loaded(comp)
    reminders = sum(1 for _ in range(12) if hook("what next?", sid))
    tr = TMP / f"{sid}.jsonl"
    tr.write_text("".join(json.dumps({"type": "user", "message": {"content": p}}) + "\n" for p in prompts), encoding="utf-8")
    guard = mg.role_session(str(tr))
    out_rule = "OUT OF YOUR ROLE" in (comp or "")
    agree = bool(re_role) == bool(guard)
    ok = bool(re_role) == want and agree
    fails += not ok
    rows.append((cid, "PASS" if ok else "FAIL", desc, "/".join(str(x) for x in first), re_role or "-", reminders, guard or "-",
                 "yes" if agree else "NO", "yes" if out_rule else "-", "re-inject" if want else "none"))

print(f"## {LABEL}")
print("| case | result | edge case | loaded on prompt(s) | after compaction | reminders /12 | model_guard role | agree | out-of-role rule | expected |")
print("|---|---|---|---|---|---|---|---|---|---|")
for r in rows: print("| " + " | ".join(str(x) for x in r) + " |")
print(f"\n{LABEL}: {len(rows)} cases, {len(rows) - fails} pass, {fails} fail")
