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
Exit 0 on launch, dry run or IDLE; 1 when claude cannot be started; 2 on a bad slug.
Test hooks: MTS_PICK_ROOT replaces the repo root, MTS_CLAUDE_BIN replaces the claude executable.
Usage (repo root): python scripts/sched/go.py [slug] [--dry]
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
LEGACY_CL = re.compile(r"^(MTS-\d{4}-\d{2}-\d{2}-\d{4}Z-)CL(-[A-Z]+-)")


def main(argv, now=None):
    now = now or datetime.now(timezone.utc)
    dry = "--dry" in argv
    args = [a for a in argv if a != "--dry"]
    slug = args[0] if args else ""
    if slug and not (SLUG_RE.match(slug) and len(slug) <= SLUG_MAX):
        print("go: slug must be lowercase kebab, at most %d chars (got %r)" % (SLUG_MAX, slug), file=sys.stderr)
        return 2
    task = QUEUE / "next_task.txt"
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
            name = json.loads((QUEUE / "next_task.json").read_text(encoding="utf-8")).get("session_id")
        except (OSError, ValueError, AttributeError):
            name = None
        if not name:
            m = re.search(r"(?m)^Session ID: (\S+)", prompt)
            name = m.group(1) if m else None
        if name and LEGACY_CL.match(name):
            name = LEGACY_CL.sub(r"\g<1>" + SURF + r"\g<2>", name)
            prompt = re.sub(r"(?m)^Session ID: .*$", "Session ID: " + name, prompt, count=1)
    reason = "--dry" if dry else ("running inside Claude Code (CLAUDECODE), one writer per tree" if os.environ.get("CLAUDECODE") else "")
    if reason:
        print("DRY RUN (%s): nothing launched. session name: %s" % (reason, name))
        print(prompt)
        return 0
    exe = os.environ.get("MTS_CLAUDE_BIN") or shutil.which("claude")
    if not exe:
        print("WARN: claude not found on PATH; nothing launched. session name: %s" % name, file=sys.stderr)
        return 1
    cmd = [exe] + (["--name", name] if name else []) + [prompt]
    try:
        return subprocess.call(cmd, cwd=ROOT)
    except OSError as e:
        print("WARN: cannot start claude: %s" % e, file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
