"""laptop_wake.py - wake the Lenovo laptop (DESKTOP-F7IU69N, login A) from the desktop over an SSH gate.

Why: tools reach only the local app; a sleeping/idle Claude session on the laptop acts only when prompted.
How: same one-shot pattern as nuc_wake.py (SCHEDULING_POLICY 4b3): the gate verb `ps` runs a PowerShell script as the
logged-in user; it registers ONE interactive scheduled task that runs `claude -p` with the boot prompt, starts it, and the
task unregisters itself when the worker ends. No standing task. Logs on the laptop: C:/MTS/laptop_wake/<name>/out.log.
Gate: key ~/.ssh/laptop_gate -> e-ngineers@192.168.29.157 (DHCP: override with env MTS_LAPTOP_HOST). Client-side verb
allow-list (ALLOWED_VERBS) so this tool can never send anything but the listed verbs; the key restriction itself
(command= forced wrapper in authorized_keys) is an operator step, see LENOVO_SETUP.md "Wake gate".
Usage: python scripts/dev/laptop_wake.py [status|ps|job-log NAME] [--dry] [--name N] [--model M]
  no verb = wake (verb `ps` with the generated script). `status` and `job-log` are read-only.
"""
import argparse
import os
import subprocess
import sys

ALLOWED_VERBS = ("status", "ps", "job-log")   # OURS: no ps-bg (SYSTEM has no Claude login), no shell
REPO = os.environ.get("MTS_LAPTOP_REPO", "C:/MTS/mts-lenovo")
WAKE_DIR = "C:/MTS/laptop_wake"

PROMPT = (
    "You are a laptop worker tick for MTS (DESKTOP-F7IU69N, login A). Follow CLAUDE.md in the repo. Boot: "
    "python scripts/dev/mts_signal.py read; python scripts/dev/tasks.py next --lane SONNET. Take ONE card, "
    "sync.py start/claim, do it, sync.py ship --release, send one mts_signal done line, then stop. "
    "Never ask the operator; take defaults and log them. Testnet only."
)


def gate_cmd(verb: str, arg: str = "") -> list:
    host = os.environ.get("MTS_LAPTOP_HOST", "192.168.29.157")
    if verb not in ALLOWED_VERBS:
        raise ValueError("verb not allowed: %r (allowed: %s)" % (verb, ", ".join(ALLOWED_VERBS)))
    if verb == "job-log" and not arg.replace("-", "").replace("_", "").isalnum():
        raise ValueError("bad job name: %r" % arg)
    cmd = ["ssh", "-i", "~/.ssh/laptop_gate", "-o", "BatchMode=yes", "-o", "ConnectTimeout=10",
           "e-ngineers@" + host, verb]
    return cmd + ([arg] if arg else [])


def build_script(model: str, prompt: str = PROMPT, name: str = "default") -> str:
    task = "MTS-LaptopWake-" + name
    lines = [
        '$env:Path += ";C:/Users/E-ngineers/.local/bin"',
        '$env:GIT_TERMINAL_PROMPT = "0"',
        f'$d = "{WAKE_DIR}/{name}"; New-Item -ItemType Directory -Force $d | Out-Null',
        "$p = @'", prompt, "'@",
        '[IO.File]::WriteAllText("$d/prompt.txt", $p)',
        '$c = (Get-Command claude.exe).Source',
        f'$cmd = "Set-Location {REPO}; Get-Content -Raw $d/prompt.txt | & \'$c\' -p --model {model} '
        f'--permission-mode bypassPermissions > $d/out.log 2> $d/err.log; '
        f'Unregister-ScheduledTask -TaskName {task} -Confirm:`$false"',
        '$a = New-ScheduledTaskAction -Execute "powershell.exe" -Argument ("-NoProfile -WindowStyle Hidden -Command `"" + $cmd + "`"")',
        '$pr = New-ScheduledTaskPrincipal -UserId "e-ngineers" -LogonType Interactive',
        f'Register-ScheduledTask -TaskName "{task}" -Action $a -Principal $pr -Force | Out-Null',
        f'Start-ScheduledTask -TaskName "{task}"',
        '"started"',
    ]
    return "\n".join(lines) + "\n"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("verb", nargs="?", default="wake")
    ap.add_argument("arg", nargs="?", default="")
    ap.add_argument("--dry", action="store_true")
    ap.add_argument("--model", default="claude-sonnet-5-5")
    ap.add_argument("--name", default="default")
    a = ap.parse_args()
    wake = a.verb == "wake"
    try:
        cmd = gate_cmd("ps" if wake else a.verb, a.arg)
    except ValueError as e:
        print("REFUSED", e)
        return 2
    script = build_script(a.model, PROMPT, a.name) if wake else None
    if a.dry:
        print(" ".join(cmd)); print(script or "")
        return 0
    try:
        r = subprocess.run(cmd, input=script, text=True, capture_output=True, timeout=300)
    except subprocess.TimeoutExpired:
        print("TIMEOUT laptop_wake after 300s: no reply from the laptop gate; not retried")
        return 124
    print(((r.stdout + r.stderr).strip()) or f"exit {r.returncode}")
    return r.returncode


if __name__ == "__main__":
    sys.exit(main())
