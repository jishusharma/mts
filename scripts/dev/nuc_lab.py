"""nuc_lab.py - run codex_run.py tick/status or gemini_queue.py from a supervisor on another device.

Why: codex_run.py and gemini_queue.py only work on JIS-NUC (F:/MTS/mts-codex-lab); a supervisor on JIS-NB or the
laptop had to hand-type the ssh command (SUPER_SESSION.md boot facts: "Status from NUC: printf 'Set-Location
F:/MTS/mts-codex-lab; python scripts/dev/codex_run.py status\\n' | ssh ..."). This wraps the nuc_gate ssh verb
`ps` (same gate as nuc_wake.py: it runs a script as the logged-in user, not SYSTEM) so one command does it.

Usage:
  python scripts/dev/nuc_lab.py status                       codex_run.py status
  python scripts/dev/nuc_lab.py tick                          codex_run.py tick
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
        cmd = "python scripts/dev/codex_run.py tick"
    elif verb == "gemini":
        if not specs:
            raise SystemExit("nuc_lab gemini: needs at least one <card>:<effort>")
        cmd = "python scripts/dev/gemini_queue.py run " + " ".join(specs)
    else:
        raise SystemExit(f"nuc_lab: unknown verb {verb!r}")
    return f"{LAB_CD}; {cmd}\n"


def run(verb, specs=None, runner=subprocess.run):
    if not have_gate_key():
        print("no gate key")
        return 0
    script = build_script(verb, specs)
    r = runner(gate_cmd() + ["ps"], input=script, text=True, capture_output=True)
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
