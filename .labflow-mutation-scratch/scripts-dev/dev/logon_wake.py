"""logon_wake.py - after a restart or logon, wake this machine's Supervisor once (SCHEDULING_POLICY.md 4d).

Why: the NUC restarts often; every session dies and nothing is picked up until an operator types. The Claude App starts at
login (its own setting) but an App session only acts when prompted. This closes the gap with no scheduler of its own:
a per-user HKCU Run value (same as c_drive_guard.py, 4c) runs `logon` once at each logon; `logon` waits for the network,
then calls successor_wake.register (4b3): ONE one-shot, self-unregistering task that boots a headless `claude -p`
Supervisor from the hand-over (budget-aware fireAt). No timer, no repeat, no admin rights.
Skips when a Supervisor of this login already planned since boot (reading ~/.claude/mts-superloop/<L>-last-plan.json is newer
than the boot), or when this boot was already woken (stamp file). Fails closed: any error is logged, the run returns 0.
Usage (install from the PRIMARY checkout, not a worktree):
  python scripts/dev/logon_wake.py install --login B     register the Run value MTSLogonWake
  python scripts/dev/logon_wake.py status | uninstall
  python scripts/dev/logon_wake.py logon --login B [--dry] [--grace 90]    what the Run value runs
Log: F:/MTS/succ_wake/logon_wake.log (override: env MTS_SUCC_WAKE_DIR).
"""
from __future__ import annotations

import argparse
import os
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

RUN_KEY = r"Software\Microsoft\Windows\CurrentVersion\Run"
RUN_NAME = "MTSLogonWake"
GRACE_S = 90        # let the network and the App settle after logon (OURS)
BOOT_SLACK_S = 120  # a plan this close to the boot stamp still counts as before it (OURS)


def base_dir() -> Path:
    return Path(os.environ.get("MTS_SUCC_WAKE_DIR") or "F:/MTS/succ_wake")


def log(msg: str) -> None:
    try:
        base_dir().mkdir(parents=True, exist_ok=True)
        with open(base_dir() / "logon_wake.log", "a", encoding="utf-8", newline="\n") as f:
            f.write("%s %s\n" % (datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%MZ"), msg))
    except OSError:
        pass


def boot_epoch(now: float | None = None) -> float:
    """Unix time of the last boot (GetTickCount64). 0.0 when it cannot be read: then nothing counts as 'since boot'."""
    try:
        import ctypes
        up = ctypes.windll.kernel32.GetTickCount64() / 1000.0
    except Exception:
        return 0.0
    return (now if now is not None else time.time()) - up


def plan_file(login: str, home=None) -> Path:
    import supervisor
    return supervisor.loop_home(home) / f"{login}-last-plan.json"


def stamp_file(login: str, home=None) -> Path:
    return plan_file(login, home).with_name(f"{login}-logon-wake.txt")


def already_up(login: str, boot: float, home=None) -> str | None:
    """Pure-ish: why no wake is needed, or None. A plan newer than the boot = a Supervisor already ran this boot;
    a stamp newer than the boot = this boot was already woken (a logoff/logon must not wake a second one)."""
    for p, why in ((plan_file(login, home), "a Supervisor planned since boot"),
                   (stamp_file(login, home), "this boot was already woken")):
        try:
            if boot and p.stat().st_mtime > boot - BOOT_SLACK_S:
                return why
        except OSError:
            continue
    return None


RECOVERY = (
    "UNPLANNED RESTART RECOVERY (this machine rebooted at {boot}; every worker Agent, background task and gate died; "
    "nothing in memory survived, so rebuild from disk and git, never from memory). Do this BEFORE the normal loop: "
    "1. python scripts/dev/sync.py start supervisor-{login}-restart; work only in the printed WORKTREE. "
    "The hand-over (handover/SUPERVISOR_{login}.md on origin/fast-track) is history and may be hours old; the pacer's last "
    "reading is {plan_path}. "
    "2. python scripts/dev/sync.py station --apply   (trees holding unshipped work, then retire finished worktrees). "
    "A dead worker's tree with commits not on origin/fast-track and a green test run: ship it with sync.py ship --release. "
    "No such commits: sync.py release its slug. "
    "3. python scripts/dev/sync.py claims   every JIS-NUC claim older than the boot belongs to a dead worker: release it "
    "(sync.py release <slug>), so its card is not stuck STALE for days. Leave claims of other hosts. "
    "4. If CI is RED, the red-trunk rule in CLAUDE.md applies first. "
    "5. Then the normal loop: get_usage if you have it, else the USAGE file; supervisor.py plan; spawn per its lines. "
    "A worker that was running before the restart is gone: its card re-enters the plan. Never ask the operator."
)


def refresh_clone(repo: Path, run=None) -> str:
    """Fast-forward the dedicated clone to origin/fast-track so the woken session boots from current scripts. Never raises."""
    import subprocess
    run = run or (lambda *a: subprocess.run(["git", "-C", str(repo), *a], capture_output=True, text=True, timeout=120))
    try:
        run("fetch", "-q", "origin", "fast-track")
        r = run("merge", "-q", "--ff-only", "origin/fast-track")
        return "clone ff ok" if r.returncode == 0 else "clone not fast-forwarded (kept as is)"
    except Exception as e:
        return "clone refresh failed: %r" % (e,)


def recovery_prompt(login: str, boot: float, home=None, base=None) -> str:
    import successor_wake as W
    plan = W.load_plan(login, home)
    usage = W.wake_usage(login, plan, datetime.now(timezone.utc), base)
    head = W.PROMPT.format(login=login, usage_line=W.usage_line(usage))
    b = datetime.fromtimestamp(boot, timezone.utc).strftime("%Y-%m-%dT%H:%MZ") if boot else "an unknown time"
    return head + " " + RECOVERY.format(boot=b, login=login, plan_path=plan_file(login, home))


APP_AUMID = "Claude_pzs8sxrjxfjjc!Claude"   # Get-StartApps; the packaged App's own start entry (OURS: its Run/StartupTask toggle reverts after a power loss)


def launch_app(running=None, start=None) -> str:
    """Start the Claude App when it is not running. The App's own 'Run on startup' is a Windows StartupTask whose
    registry state is lost on a power cut (Event 41), so logon does not rely on it. Never raises."""
    import subprocess
    try:
        if running is None:
            out = subprocess.run(["tasklist", "/FI", "IMAGENAME eq Claude.exe", "/NH"], capture_output=True, text=True, timeout=30).stdout
            running = "Claude.exe" in out
        if running:
            return "already running"
        (start or (lambda: subprocess.Popen(["explorer.exe", "shell:AppsFolder\\" + APP_AUMID])))()
        return "started"
    except Exception as e:
        return "launch failed: %r" % (e,)


def logon(login: str, dry: bool = False, grace: float = GRACE_S, home=None, boot: float | None = None, register=None, sleep=time.sleep, refresh=None, launch=None) -> int:
    login = (login or "").strip().upper()[:1]
    if login not in ("A", "B", "C"):
        log("logon: login must be A, B or C")
        return 0
    try:
        sleep(0 if dry else grace)
        if not dry:
            log("logon %s: app %s" % (login, (launch or launch_app)()))
        b = boot_epoch() if boot is None else boot
        why = already_up(login, b, home)
        if why:
            log("logon %s: skip, %s" % (login, why))
            return 0
        if register is None:
            import successor_wake
            register = successor_wake.register
        note = (refresh or refresh_clone)(HERE.parents[1]) if not dry else "dry"
        pf = base_dir() / ("restart_prompt_%s.txt" % login)
        pf.parent.mkdir(parents=True, exist_ok=True)
        pf.write_text(recovery_prompt(login, b, home, str(base_dir())), encoding="utf-8", newline=chr(10))
        log("logon %s: %s" % (login, note))
        r = register(login, dry=dry, home=home, prompt_file=str(pf))
        if not dry:
            p = stamp_file(login, home)
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text(r["line"] + "\n", encoding="utf-8", newline="\n")
        log("logon %s: %s%s" % (login, r["line"], " (dry)" if dry else ""))
    except Exception as e:      # a restart must not show an error box; the log says why
        log("logon %s: error %r" % (login, e))
    return 0


def logon_command(login: str, python=None, script=None) -> str:
    conhost = os.path.join(os.environ.get("SystemRoot", r"C:\Windows"), "System32", "conhost.exe")
    return '"%s" --headless "%s" "%s" logon --login %s' % (conhost, python or sys.executable,
                                                         script or str(Path(__file__).resolve()), login)


def installed_command(key=RUN_KEY, name=RUN_NAME):
    try:
        import winreg
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, key) as k:
            return winreg.QueryValueEx(k, name)[0]
    except (ImportError, OSError):
        return None


def install(login: str, checkout=None, key=RUN_KEY, name=RUN_NAME) -> int:
    login = (login or "").strip().upper()[:1]
    if login not in ("A", "B", "C"):
        print("refused: --login A|B|C")
        return 2
    root = Path(checkout) if checkout else HERE.parents[1]
    if (root / ".git").is_file():
        print("refused: %s is a git worktree; run install from the primary checkout" % root)
        return 2
    script = root / "scripts" / "dev" / "logon_wake.py"
    if not script.is_file() or os.name != "nt":
        print("refused: %s missing or not Windows" % script)
        return 2
    import winreg
    cmd = logon_command(login, script=str(script))
    with winreg.CreateKeyEx(winreg.HKEY_CURRENT_USER, key, 0, winreg.KEY_SET_VALUE) as k:
        winreg.SetValueEx(k, name, 0, winreg.REG_SZ, cmd)
    print("installed: HKCU\\%s  %s = %s" % (key, name, cmd))
    return 0


def uninstall(key=RUN_KEY, name=RUN_NAME) -> int:
    if os.name != "nt":
        print("refused: Windows only")
        return 2
    import winreg
    try:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, key, 0, winreg.KEY_SET_VALUE) as k:
            winreg.DeleteValue(k, name)
        print("removed: HKCU\\%s  %s" % (key, name))
    except FileNotFoundError:
        print("not installed")
    return 0


def status() -> int:
    cur = installed_command()
    print("logon wake: " + ("installed" if cur else "not installed (python scripts/dev/logon_wake.py install --login B)"))
    if cur:
        print("command: " + cur)
    try:
        last = (base_dir() / "logon_wake.log").read_text(encoding="utf-8").splitlines()[-1]
    except (OSError, IndexError):
        last = "none yet"
    print("last logon line: " + last)
    return 0


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("cmd", choices=["logon", "install", "uninstall", "status"])
    ap.add_argument("--login", default=os.environ.get("MTS_LOGIN", ""))
    ap.add_argument("--dry", action="store_true")
    ap.add_argument("--grace", type=float, default=GRACE_S)
    a = ap.parse_args(argv)
    if a.cmd == "logon":
        return logon(a.login, dry=a.dry, grace=a.grace)
    if a.cmd == "install":
        return install(a.login)
    if a.cmd == "uninstall":
        return uninstall()
    return status()


if __name__ == "__main__":
    sys.exit(main())
