"""nuc_wake.py - wake the NUC from NB over the SSH gate by running one headless Claude worker there.

Why: the NUC coordinator is an App session that only acts when prompted; if it idles, nothing moves.
How: the gate verb `ps` runs a PowerShell script as the logged-in user (ps-bg runs as SYSTEM, which has no Claude login);
the script runs `claude -p` (CLI fallback, SURFACE_POLICY.md: the App cannot reach an idle NUC) with the
boot prompt below. One tick = one card, shipped through sync.py, then it exits. No standing NUC task.
Usage: python scripts/dev/nuc_wake.py [--dry] [--model claude-sonnet-5-5]
Logs on the NUC: F:/MTS/nuc_wake/out.log (read with the gate `ps` verb).
"""
import argparse
import subprocess
import sys

GATE = ["ssh", "-i", "~/.ssh/nuc_gate", "-o", "BatchMode=yes", "-o", "ConnectTimeout=10",
        "e-ngineers@192.168.29.110"]

PROMPT = (
    "You are a NUC worker tick for MTS. Follow CLAUDE.md in the repo. Boot: python scripts/dev/mts_signal.py read; "
    "read MyTradingSys/system/PLAN_2026-10-17_NEXT_5H.md. Take ONE card, fundamentals first in this order: "
    "G3 chart rebuild, wavetrend-priority-source-parity if unclaimed, context-factors-pit-audit, "
    "then whatever python scripts/dev/tasks.py next lists for JIS-NUC or SONNET. Skip gptb-* event tables, "
    "confluence-read-encode and Q86. sync.py start/claim, do the card, run a Sonnet review Agent if rule 11 applies, "
    "sync.py ship --release, check git cherry origin/fast-track HEAD is empty, send one mts_signal done line, then stop. "
    "Never ask the operator; take defaults and log them."
)


def build_script(model: str) -> str:
    # `ps` runs as the logged-in user (the SYSTEM ps-bg job has no Claude login: "Not logged in").
    # Start-Process detaches the worker so it survives the ssh disconnect.
    lines = [
        '$env:Path += ";C:/Users/E-ngineers/.local/bin"',
        '$d = "F:/MTS/nuc_wake"; New-Item -ItemType Directory -Force $d | Out-Null',
        "$p = @'",
        PROMPT,
        "'@",
        '[IO.File]::WriteAllText("$d/prompt.txt", $p)',
        f'Start-Process -FilePath (Get-Command claude.exe).Source -ArgumentList "-p","--model","{model}",'
        '"--permission-mode","bypassPermissions" -WorkingDirectory F:/MTS -WindowStyle Hidden '
        '-RedirectStandardInput "$d/prompt.txt" -RedirectStandardOutput "$d/out.log" -RedirectStandardError "$d/err.log"',
        '"started"',
    ]
    return "\n".join(lines) + "\n"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry", action="store_true")
    ap.add_argument("--model", default="claude-sonnet-5-5")
    a = ap.parse_args()
    script = build_script(a.model)
    if a.dry:
        print(script)
        return 0
    r = subprocess.run(GATE + ["ps"], input=script, text=True, capture_output=True)
    out = "\n".join(l for l in (r.stdout + r.stderr).splitlines() if "quantum" not in l and "upgraded" not in l)
    print(out.strip() or f"exit {r.returncode}")
    return r.returncode


if __name__ == "__main__":
    sys.exit(main())
