"""scripts/dev/role_hook_launcher.py: user-level role hook that works in ANY checkout (old commits, stale worktrees).

Claude Code reads hooks from the session's own folder, so a checkout older than the role_loader hook gets no role
injection and no error. This launcher is installed once at the user level (~/.claude/mts_role_launcher.py plus a
SessionStart + UserPromptSubmit entry in ~/.claude/settings.json) and guarantees: a role request ends in the banner
instruction (role_loader taken from origin/fast-track) or a visible ROLE NOT LOADED, never silence.

  hook        (default; stdin = hook JSON) run as the user-level hook
  install     copy this file to ~/.claude/mts_role_launcher.py and add the two hook entries (idempotent)
  uninstall   remove them

Skips (prints nothing) when the cwd checkout's own .claude settings already register role_loader (no double run), when
the cwd is not an MTS checkout, or when the prompt names no role. Stdlib only; fails open on its own errors except for
the explicit ROLE NOT LOADED case.
"""
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

TRUNK = "origin/fast-track"
LOADER_REL = "scripts/dev/role_loader.py"
MARK = "mts_role_launcher.py"
KNOWN = ["Eagle_Eyes", "Lab_Guy", "Session_Planner", "MTS_Doctor", "1985Artifacts_Guy", "Artifacts_Guy", "Admin_Guy",
         "Q&A_Helper", "Network_Admin_Guy", "Pipeliner", "Traffic_Controller", "Supervisor", "Builder", "Thinker"]
PREFIX = r"(?:you are|you're|act as|be the|be|role:|i need(?: an| a| the)?|start(?: an| a| the)?)"
HOME = Path.home() / ".claude"


def _git(repo, *args):
    r = subprocess.run(["git", "-C", str(repo), *args], capture_output=True, timeout=10,
                       creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0) if sys.platform == "win32" else 0)
    return r.returncode, r.stdout.decode("utf-8", "replace")


def toplevel(cwd):
    try:
        rc, out = _git(cwd, "rev-parse", "--show-toplevel")
        return Path(out.strip()) if rc == 0 and out.strip() else None
    except Exception:
        return None


def project_has_hook(top):
    for n in ("settings.json", "settings.local.json"):
        try:
            if "role_loader.py" in (top / ".claude" / n).read_text(encoding="utf-8"):
                return True
        except Exception:
            pass
    return False


def names_role(prompt):
    for n in KNOWN:
        pat = PREFIX + r"\s+(?:the\s+)?" + r"[_ ]".join(re.escape(p) for p in re.split(r"[_ ]+", n)) + r"\b"
        if re.search(pat, prompt, re.I):
            return n
    return None


def not_loaded(event, why):
    return json.dumps({"hookSpecificOutput": {"hookEventName": event, "additionalContext":
        f"ROLE LOADER (user-level launcher): the role loader could not run ({why}). Your FIRST reply must begin with "
        f"exactly `ROLE NOT LOADED: {why}`; you may then read MyTradingSys/system/roles/<role>.md by hand, but do not "
        f"claim a banner or token."}})


def run(payload):
    event = payload.get("hook_event_name") or "UserPromptSubmit"
    top = toplevel(payload.get("cwd") or ".")
    if top is None or not (top / "MyTradingSys").is_dir():
        return ""
    if project_has_hook(top):
        return ""
    prompt = payload.get("prompt") if isinstance(payload.get("prompt"), str) else ""
    role = names_role(prompt) if event == "UserPromptSubmit" else None
    try:
        rc, src = _git(top, "show", f"{TRUNK}:{LOADER_REL}")
    except Exception as e:
        src, rc = "", 1
    if rc != 0 or not src.strip():
        return not_loaded(event, f"{LOADER_REL} missing on {TRUNK} in {top.name}; run git fetch") if role else ""
    g = {"__name__": "mts_role_loader_trunk", "__file__": str(top / LOADER_REL)}
    try:
        exec(compile(src, f"{TRUNK}:{LOADER_REL}", "exec"), g)
        out = g["handle"](payload, top)
    except Exception as e:
        return not_loaded(event, f"trunk role_loader failed: {type(e).__name__}") if role else ""
    return out or ""


def hook():
    try:
        out = run(json.loads(sys.stdin.read() or "{}"))
    except Exception:
        return 0
    if out:
        sys.stdout.write(out)
        sys.stdout.flush()
    return 0


def _cmd(dest):
    return f'python "{dest.as_posix()}" hook'


def _edit(settings, dest, add):
    data = json.loads(settings.read_text(encoding="utf-8")) if settings.exists() else {}
    hooks = data.setdefault("hooks", {})
    for ev in ("SessionStart", "UserPromptSubmit"):
        groups = hooks.setdefault(ev, [])
        for g in groups:
            g["hooks"] = [h for h in g.get("hooks", []) if MARK not in h.get("command", "")]
        groups[:] = [g for g in groups if g.get("hooks")]
        if add:
            groups.append({"hooks": [{"type": "command", "command": _cmd(dest), "timeout": 20}]})
        if not groups:
            del hooks[ev]
    if not hooks:
        del data["hooks"]
    settings.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8", newline="\n")


def install(home=HOME, add=True):
    home.mkdir(parents=True, exist_ok=True)
    dest = home / MARK
    if add:
        shutil.copyfile(__file__, dest)
    _edit(home / "settings.json", dest, add)
    print(("installed " if add else "removed ") + str(dest))
    return 0


if __name__ == "__main__":
    c = sys.argv[1] if len(sys.argv) > 1 else "hook"
    sys.exit(install() if c == "install" else install(add=False) if c == "uninstall" else hook())
