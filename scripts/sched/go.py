import sys
sys.dont_write_bytecode = True

"""Launch the queued build task in claude (the body of `mts go`).

One CL writer per file set. A session that is already running under Claude Code (env CLAUDECODE) must not start a
second writer on the same tree, so there the launch is a dry run: the prompt and the session name are printed and
nothing is started (B086). `--dry` forces the same from anywhere. The operator's own terminal has no CLAUDECODE, so
`mts go` there launches live as before.

Session name (B087c): no argument -> the Session ID already inside the prompt (next_task.json). A kebab slug
(<=20 chars, lowercase) -> MTS-YYYY-MM-DD-HHMMZ-CLI-BLD-<slug> from the current UTC (SURFACE_POLICY section 4), and
the prompt's `Session ID:` line is rewritten to match. One builder: pick_task.session_id (B088). An inherited name
composed before B088 with the off-policy code -CL- is launched as -CLI-, prompt line rewritten to match.
`--id <rid>` (B093) launches the slot row queue/slots/<rid>.* instead of next_task.*: the session name is the one stored in
the slot json, the prompt's `Session ID:` line is rewritten to match; the same dry-run gate applies.
Exit 0 on launch, dry run or IDLE; 1 when claude cannot be started; 2 on a bad slug or bad --id; 3 when the slot is missing.
Per-run cap (B094): `--max-usd N` or env MTS_GO_MAX_USD (flag wins, default 5) is passed to claude as --max-budget-usd N;
0 means no cap; a negative or non-numeric value exits 2. `--headless` adds claude -p (print mode, where the cap is enforced).
Test hooks: MTS_PICK_ROOT replaces the repo root, MTS_CLAUDE_BIN replaces the claude executable.
Usage (repo root): python scripts/sched/go.py [slug] [--id <rid>] [--dry] [--headless] [--max-usd N]
"""
import json
import os
import re
import shutil
import subprocess
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from pick_task import SURF, session_id as session_name

ROOT = Path(os.environ.get("MTS_PICK_ROOT") or Path(__file__).resolve().parents[2])
QUEUE = ROOT / "MyTradingSys" / "runtime" / "queue"
SLUG_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
SLUG_MAX = 20
RID_RE = re.compile(r"^[A-Za-z][A-Za-z0-9]*$")
DEFAULT_MAX_USD = "5"
LEGACY_CL = re.compile(r"^(MTS-\d{4}-\d{2}-\d{2}-\d{4}Z-)CL(-[A-Z]+-)")


def m_name(prompt):
    m = re.search(r"(?m)^Session ID: (\S+)", prompt)
    return m.group(1) if m else None


def main(argv, now=None):
    now = now or datetime.now(timezone.utc)
    dry = "--dry" in argv
    headless = "--headless" in argv
    args = [a for a in argv if a not in ("--dry", "--headless")]
    cap = os.environ.get("MTS_GO_MAX_USD", DEFAULT_MAX_USD)
    if "--max-usd" in args:
        i = args.index("--max-usd")
        cap = args[i + 1] if i + 1 < len(args) else ""
        args = args[:i] + args[i + 2:]
    try:
        cap_val = float(cap)
        if cap_val < 0 or cap_val != cap_val:
            raise ValueError(cap)
    except ValueError:
        print("go: --max-usd / MTS_GO_MAX_USD must be a number >= 0 (got %r)" % cap, file=sys.stderr)
        return 2
    rid = None
    if "--id" in args:
        i = args.index("--id")
        rid = args[i + 1] if i + 1 < len(args) else ""
        args = args[:i] + args[i + 2:]
        if not RID_RE.match(rid):
            print("go: --id needs a row id such as B074 (got %r)" % rid, file=sys.stderr)
            return 2
    slug = args[0] if args else ""
    if slug and not (SLUG_RE.match(slug) and len(slug) <= SLUG_MAX):
        print("go: slug must be lowercase kebab, at most %d chars (got %r)" % (SLUG_MAX, slug), file=sys.stderr)
        return 2
    base = (QUEUE / "slots" / rid) if rid else (QUEUE / "next_task")
    task = base.with_name(base.name + ".txt")
    if rid and not task.is_file():
        print("go: no slot for %s (%s)" % (rid, task), file=sys.stderr)
        return 3
    if not task.is_file():
        print("IDLE: queue empty")
        return 0
    prompt = task.read_text(encoding="utf-8").strip()
    if prompt.startswith("IDLE"):
        print("IDLE: queue empty")
        return 0
    name = None
    if slug:
        name = session_name(slug, now)
        prompt = re.sub(r"(?m)^Session ID: .*$", "Session ID: " + name, prompt, count=1)
    else:
        try:
            name = json.loads(base.with_name(base.name + ".json").read_text(encoding="utf-8")).get("session_id")
        except (OSError, ValueError, AttributeError):
            name = None
        if not name:
            m = re.search(r"(?m)^Session ID: (\S+)", prompt)
            name = m.group(1) if m else None
        if name and LEGACY_CL.match(name):
            name = LEGACY_CL.sub(r"\g<1>" + SURF + r"\g<2>", name)
        if name and (rid or name != m_name(prompt)):
            prompt = re.sub(r"(?m)^Session ID: .*$", "Session ID: " + name, prompt, count=1)
    reason = "--dry" if dry else ("running inside Claude Code (CLAUDECODE), one writer per tree" if os.environ.get("CLAUDECODE") else "")
    if reason:
        print("DRY RUN (%s): nothing launched. session name: %s" % (reason, name))
        print("cap: %s" % (("--max-budget-usd " + cap) if cap_val > 0 else "none"))
        print(prompt)
        return 0
    exe = os.environ.get("MTS_CLAUDE_BIN") or shutil.which("claude")
    if not exe:
        print("WARN: claude not found on PATH; nothing launched. session name: %s" % name, file=sys.stderr)
        return 1
    cmd = [exe] + (["--name", name] if name else []) + (["--max-budget-usd", cap] if cap_val > 0 else [])         + (["-p"] if headless else []) + [prompt]
    try:
        return subprocess.call(cmd, cwd=ROOT)
    except OSError as e:
        print("WARN: cannot start claude: %s" % e, file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
