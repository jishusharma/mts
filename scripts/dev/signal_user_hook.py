"""User-level signal hook: every Claude session on a machine sees MTS asks and broadcasts, wherever its folder is.

Operator 2026-11-09: the NUC super session ran in C:/Users/E-ngineers/IdeaProjects, outside the repo. The repo's hook
(.claude/settings.json -> mts_signal.py hook) only runs for sessions opened inside a clone, so 6 HIGH broadcasts and the
asks to the NUC sat unseen for up to 18 h and C reported the NUC "maybe off".

  python scripts/dev/signal_user_hook.py install [--repo DIR]   copy the runner to ~/.mts/, add SessionStart,
        UserPromptSubmit and Stop entries to ~/.claude/settings.json (merge, idempotent, settings.json.bak first) and
        remember DIR (default: this clone) as a clone the runner may use
  python scripts/dev/signal_user_hook.py status                  installed? which clone does the runner use?
mts_signal.py calls ensure_installed() at every repo SessionStart (quiet, never raises), so each machine gets the hook
on its next session inside a clone; nobody has to run install by hand.

The runner (~/.mts/signal_user_hook_runner.py) does nothing for a session whose folder (or a parent) already carries the
repo hook, so a session inside a clone is never served twice. Otherwise it sets the payload cwd to the newest clone in
~/.mts/repo_paths.json that still exists and runs that clone's mts_signal.py hook, passing its output (a Stop block is
JSON on stdout) straight through. It never raises and never blocks beyond its timeout.
"""
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

VERSION = 2
EVENTS = ("SessionStart", "UserPromptSubmit", "Stop")
MARK = "signal_user_hook_runner"
KEEP = 6                     # OURS: clones remembered per machine
TIMEOUT_S = 11               # OURS: under the 12 s hook timeout

RUNNER = r'''# MTS signal hook runner v%(v)d (written by scripts/dev/signal_user_hook.py; do not edit, it is rewritten)
import json, subprocess, sys
from pathlib import Path
HOME = Path(%(home)r)


def has_repo_hook(cwd):
    try:
        p = Path(cwd).resolve()
    except Exception:
        return False
    for d in (p, *p.parents):
        if d == Path.home():          # ~/.claude/settings.json is the user file that runs this runner, not a repo hook
            continue
        f = d / ".claude" / "settings.json"
        try:
            if f.is_file() and "mts_signal.py" in f.read_text(encoding="utf-8", errors="replace"):
                return True
        except OSError:
            pass
    return False


try:
    raw = sys.stdin.buffer.read().decode("utf-8", "replace")
    d = json.loads(raw) if raw.strip() else {}
    if not has_repo_hook(d.get("cwd") or "."):
        repos = json.loads((HOME / "repo_paths.json").read_text(encoding="utf-8"))
        repo = next((r for r in repos if (Path(r) / "scripts" / "dev" / "mts_signal.py").is_file()), None)
        if repo:
            d["cwd"] = repo
            r = subprocess.run([sys.executable, str(Path(repo) / "scripts" / "dev" / "mts_signal.py"), "hook"],
                               input=json.dumps(d).encode("utf-8"), capture_output=True, cwd=repo, timeout=%(t)d,
                               creationflags=0x08000000 if sys.platform == "win32" else 0)
            sys.stdout.buffer.write(r.stdout)
except Exception:
    pass
'''


def mts_home():
    return Path(os.environ.get("MTS_USER_HOOK_HOME") or Path.home() / ".mts")


def claude_settings():
    return Path(os.environ.get("MTS_USER_HOOK_SETTINGS") or Path.home() / ".claude" / "settings.json")


def runner_path():
    return mts_home() / (MARK + ".py")


def runner_text():
    return RUNNER % {"v": VERSION, "home": mts_home().as_posix(), "t": TIMEOUT_S}


def command():
    return '"%s" "%s"' % (Path(sys.executable).as_posix(), runner_path().as_posix())


def remember(repo):
    """Put repo first in repo_paths.json (deduplicated, at most KEEP). Returns True when the file changed."""
    f = mts_home() / "repo_paths.json"
    try:
        old = json.loads(f.read_text(encoding="utf-8"))
        old = old if isinstance(old, list) else []
    except (OSError, ValueError):
        old = []
    key = Path(repo).resolve().as_posix()
    got = ([key] + [r for r in old if isinstance(r, str) and r.lower() != key.lower()])[:KEEP]
    if got == old:
        return False
    f.parent.mkdir(parents=True, exist_ok=True)
    f.write_text(json.dumps(got, indent=1), encoding="utf-8", newline="\n")
    return True


def merge_settings(s, cmd):
    """(settings, changed): each EVENT ends with exactly one runner entry running cmd; every other hook is untouched."""
    changed = False
    hooks = s.setdefault("hooks", {})
    for ev in EVENTS:
        groups = hooks.setdefault(ev, [])
        found = False
        for g in groups:
            keep = []
            for h in g.get("hooks", []):
                if MARK in str(h.get("command", "")):
                    if found:                       # a duplicate runner entry: drop it
                        changed = True
                        continue
                    if h.get("command") != cmd or h.get("timeout") != TIMEOUT_S + 1:
                        changed = True
                    h.update(type="command", command=cmd, timeout=TIMEOUT_S + 1)
                    found = True
                keep.append(h)
            g["hooks"] = keep
        hooks[ev] = [g for g in groups if g.get("hooks")]
        if not found:
            hooks[ev].append({"hooks": [{"type": "command", "command": cmd, "timeout": TIMEOUT_S + 1}]})
            changed = True
    return s, changed


def install(repo):
    """Idempotent. Returns what changed (empty: already current). A settings.json that does not parse is never
    overwritten (ValueError propagates)."""
    did = []
    rp = runner_path()
    rp.parent.mkdir(parents=True, exist_ok=True)
    txt = runner_text()
    try:
        cur = rp.read_text(encoding="utf-8")
    except OSError:
        cur = ""
    if cur != txt:
        rp.write_text(txt, encoding="utf-8", newline="\n")
        did.append("runner")
    if remember(repo):
        did.append("clone")
    sf = claude_settings()
    try:
        raw = sf.read_text(encoding="utf-8")
    except FileNotFoundError:
        raw = ""
    s = json.loads(raw) if raw.strip() else {}
    s, changed = merge_settings(s, command())
    if changed:
        sf.parent.mkdir(parents=True, exist_ok=True)
        if raw:
            shutil.copyfile(sf, sf.with_name(sf.name + ".bak"))
        sf.write_text(json.dumps(s, indent=2, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
        did.append("settings")
    return did


def ensure_installed(cwd):
    """Called by mts_signal.py at a repo SessionStart. Quiet; never raises. Skipped in tests (MTS_SIGNALS_HOME set,
    unless MTS_USER_HOOK_HOME points the install at a temp dir) and with MTS_USER_HOOK=off."""
    if os.environ.get("MTS_USER_HOOK", "").lower() == "off":
        return []
    if os.environ.get("MTS_SIGNALS_HOME") and not os.environ.get("MTS_USER_HOOK_HOME"):
        return []
    try:
        r = subprocess.run(["git", "-C", str(cwd or "."), "rev-parse", "--show-toplevel"], capture_output=True,
                           text=True, timeout=5, creationflags=0x08000000 if os.name == "nt" else 0)
        top = r.stdout.strip()
        if r.returncode or not top or not (Path(top) / "scripts" / "dev" / "mts_signal.py").is_file():
            return []
        return install(top)
    except Exception:
        return []


def status():
    try:
        s = json.loads(claude_settings().read_text(encoding="utf-8"))
    except (OSError, ValueError):
        s = {}
    evs = [ev for ev in EVENTS if any(MARK in str(h.get("command", "")) for g in s.get("hooks", {}).get(ev, [])
                                      for h in g.get("hooks", []))]
    try:
        repos = json.loads((mts_home() / "repo_paths.json").read_text(encoding="utf-8"))
    except (OSError, ValueError):
        repos = []
    live = next((r for r in repos if (Path(r) / "scripts" / "dev" / "mts_signal.py").is_file()), None)
    ok = bool(runner_path().is_file() and len(evs) == len(EVENTS) and live)
    print("USER HOOK %s: runner %s; events %s; clone %s" % ("OK" if ok else "MISSING", runner_path().is_file(),
                                                           ",".join(evs) or "none", live or "none"))
    return 0 if ok else 1


def main(argv):
    if not argv or argv[0] in ("-h", "--help"):
        print(__doc__)
        return 0
    if argv[0] == "install":
        repo = argv[argv.index("--repo") + 1] if "--repo" in argv else str(Path(__file__).resolve().parents[2])
        print("installed: %s" % (", ".join(install(repo)) or "already current"))
        return status()
    if argv[0] == "status":
        return status()
    print(__doc__)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
