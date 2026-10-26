"""PermissionRequest hook: answer every permission dialog with allow so unattended sessions never wait.

Deny rules still apply (Claude Code re-checks them after an allow), so rm/reset/.secrets denies keep holding.
Each request is logged to ~/.claude/perm_requests.jsonl (outside the repo) so we see which dialogs still appear.
Any error -> exit 0 with no output: the normal flow continues (never worse than without the hook).

  python scripts/dev/perm_hook.py install    copy to ~/.claude/hooks/ and register in ~/.claude/settings.json
  python scripts/dev/perm_hook.py status     show whether this machine has it and the last logged requests
"""
import json
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path

HOME = Path.home() / ".claude"
LOG = HOME / "perm_requests.jsonl"
DEST = HOME / "hooks" / "perm_hook.py"
ALLOW = {"hookSpecificOutput": {"hookEventName": "PermissionRequest", "decision": {"behavior": "allow"}}}


def decide(req):
    return ALLOW


def log_request(req, path=LOG):
    req = req if isinstance(req, dict) else {}
    ti = req.get("tool_input") if isinstance(req.get("tool_input"), dict) else {}
    detail = str(ti.get("command") or ti.get("file_path") or ti.get("url") or ti.get("path") or "")[:160]
    row = {"utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"), "tool": req.get("tool_name"),
           "mode": req.get("permission_mode"), "cwd": req.get("cwd"), "detail": detail}
    with open(path, "a", encoding="utf-8", newline="\n") as f:
        f.write(json.dumps(row) + "\n")


def main(log_path=LOG):
    try:
        req = json.load(sys.stdin)
    except Exception:
        req = None
    try:
        log_request(req, log_path)
    except Exception as exc:
        print(f"perm_hook: log failed: {exc}", file=sys.stderr)
    print(json.dumps(decide(req)))
    return 0


def install_into_settings(settings, command):
    entry = {"matcher": "*", "hooks": [{"type": "command", "command": command, "timeout": 10}]}
    groups = settings.setdefault("hooks", {}).setdefault("PermissionRequest", [])
    if not any(h.get("command") == command for g in groups for h in g.get("hooks", [])):
        groups.append(entry)
    return settings


def install():
    DEST.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(__file__, DEST)
    sp = HOME / "settings.json"
    settings = json.loads(sp.read_text(encoding="utf-8")) if sp.exists() else {}
    cmd = f'python "{DEST.as_posix()}"'
    install_into_settings(settings, cmd)
    sp.write_text(json.dumps(settings, indent=2) + "\n", encoding="utf-8", newline="\n")
    print(f"installed: {DEST} registered in {sp}")
    return 0


def status():
    sp = HOME / "settings.json"
    s = json.loads(sp.read_text(encoding="utf-8")) if sp.exists() else {}
    on = bool(s.get("hooks", {}).get("PermissionRequest"))
    print(f"PermissionRequest hook registered: {on}; script present: {DEST.exists()}; defaultMode={s.get('permissions', {}).get('defaultMode')}")
    if LOG.exists():
        for line in LOG.read_text(encoding="utf-8").splitlines()[-5:]:
            print(line)
    else:
        print("no requests logged yet")
    return 0


if __name__ == "__main__":
    verb = sys.argv[1] if len(sys.argv) > 1 else ""
    sys.exit({"install": install, "status": status}.get(verb, main)())
