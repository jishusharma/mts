"""nuc_lab.py - run codex_run.py tick/status or gemini_queue.py from a supervisor on another device.

Why: codex_run.py and gemini_queue.py only work on JIS-NUC (F:/MTS/mts-codex-lab); a supervisor on JIS-NB or the
laptop had to hand-type the ssh command (SUPER_SESSION.md boot facts: "Status from NUC: printf 'Set-Location
F:/MTS/mts-codex-lab; python scripts/dev/codex_run.py status\\n' | ssh ..."). This wraps the nuc_gate ssh verb
`ps` (same gate as nuc_wake.py: it runs a script as the logged-in user, not SYSTEM) so one command does it.

Usage:
  python scripts/dev/nuc_lab.py status                       codex_run.py status
  python scripts/dev/nuc_lab.py tick                          starts codex_run.py tick in the logged-on session (log: F:/MTS/nuc_wake/tick.log)
  python scripts/dev/nuc_lab.py gemini <card>:<low|medium|high> [...]   gemini_queue.py run <card>:<effort> ...

On a device with no ~/.ssh/nuc_gate key this exits 0 and prints "no gate key": calling code does not need to
know which device it runs on first. It never starts a second run itself - codex_run.py's lab.lock and the
20-minute gap guard (LAYER_LAB.md), and gemini_queue.py's own claim check, already stop overlap; this is a thin
ssh wrapper, nothing more.
"""
import argparse
import os
import shutil
import subprocess
import sys
from pathlib import Path

HOST = "e-ngineers@192.168.29.110"
LAB_CD = "Set-Location F:/MTS/mts-codex-lab"
# An ssh logon cannot read the saved GitHub login, so a tick run inside the ssh session fails its claim push with
# "could not read Username" (card nuc-codex-run-py-tick-cannot-push-claims, 2026-11-04). The interactive task runs in
# the logged-on user's own session, where the login works. It has no trigger: it runs only when started here.
TICK_SCRIPT = "schtasks /run /tn MTS-Wake-codextick"


def ssh_exe():
    """Resolve via shutil.which (checks PATHEXT on Windows, so a test's ssh.cmd shim on PATH is found; a bare
    'ssh' passed straight to subprocess without shell=True would not try .cmd/.bat extensions)."""
    return shutil.which("ssh") or "ssh"


def key_path():
    """~/.ssh/nuc_gate, overridable by MTS_NUC_GATE_KEY (tests only; production never sets it)."""
    return Path(os.environ.get("MTS_NUC_GATE_KEY") or (Path.home() / ".ssh" / "nuc_gate"))


def have_gate_key():
    return key_path().is_file()


def gate_cmd():
    return [ssh_exe(), "-i", str(key_path()), "-o", "BatchMode=yes", "-o", "ConnectTimeout=10", HOST]


def build_script(verb, specs=None):
    if verb == "status":
        cmd = "python scripts/dev/codex_run.py status"
    elif verb == "tick":
        return TICK_SCRIPT + "\n"
    elif verb == "gemini":
        if not specs:
            raise SystemExit("nuc_lab gemini: needs at least one <card>:<effort>")
        cmd = "python scripts/dev/gemini_queue.py run " + " ".join(specs)
    else:
        raise SystemExit(f"nuc_lab: unknown verb {verb!r}")
    return f"{LAB_CD}; {cmd}\n"


# Max wall time per verb (bg-process-audit 2026-10-28, OURS): a NUC verb with no deadline sat silent for 1h39m+.
# status is a NUC verb (5 min). tick and gemini run a whole Codex/Gemini job inside the ssh session (the 2-hour silent
# probe of 2026-10-27 was `codex_run.py tick` piped over ssh), so they get the worker cap: 45 min.
VERB_TIMEOUT_S = {"status": 300, "tick": 2700, "gemini": 2700}


def run(verb, specs=None, runner=subprocess.run, timeout=None):
    if not have_gate_key():
        print("no gate key")
        return 0
    script = build_script(verb, specs)
    limit = timeout or VERB_TIMEOUT_S.get(verb, 300)
    try:
        r = runner(gate_cmd() + ["ps"], input=script, text=True, capture_output=True, timeout=limit)
    except subprocess.TimeoutExpired:
        print(f"TIMEOUT nuc_lab {verb} after {limit}s: no reply from the NUC gate; not retried (check `nuc_wake.py` / NUC power)")
        return 124
    out = "\n".join(l for l in (r.stdout + r.stderr).splitlines() if "quantum" not in l and "upgraded" not in l)
    print(out.strip() or f"exit {r.returncode}")
    return r.returncode


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="verb", required=True)
    sub.add_parser("status")
    sub.add_parser("tick")
    g = sub.add_parser("gemini")
    g.add_argument("specs", nargs="+", help="<card-id>:<low|medium|high>")
    a = ap.parse_args(argv)
    return run(a.verb, getattr(a, "specs", None))


if __name__ == "__main__":
    sys.exit(main())
