"""nuc_wake.py - wake the NUC from NB over the SSH gate by running one headless Claude worker there.

Why: the NUC coordinator is an App session that only acts when prompted; if it idles, nothing moves.
How: the gate verb `ps` runs a PowerShell script as the logged-in user (ps-bg runs as SYSTEM, which has no Claude login);
the script runs `claude -p` (CLI fallback, SURFACE_POLICY.md: the App cannot reach an idle NUC) with the
boot prompt below. One tick = one card, shipped through sync.py, then it exits. No standing NUC task (SCHEDULING_POLICY.md allows only the one-shot task this creates; unregister it after it fires).
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


CARD_PROMPT = (
    "You are a NUC worker for MTS. Follow CLAUDE.md in the repo. Boot: python scripts/dev/sync.py start {card}; python scripts/dev/mts_signal.py read; "
    "python scripts/dev/tasks.py brief {card}; python scripts/dev/sync.py claim. Do exactly that one card in full. Rule 11: if the diff touches the live path, "
    "gates, decision numbers, run a Sonnet review Agent in the foreground (diff only, 5-line reply) before ship and fix on BLOCK once. "
    "No VALIDATION/HOLDOUT reads. python scripts/dev/sync.py ship --release {card} with a Result: line, confirm git cherry origin/fast-track HEAD is empty, "
    "send one mts_signal done line, stop. Never ask the operator; take defaults and log them."
)


def build_script(model: str, prompt: str = PROMPT, name: str = "default", card: str = None) -> str:
    # `ps` runs as the logged-in user (the SYSTEM ps-bg job has no Claude login: "Not logged in").
    # Start-Process detaches the worker so it survives the ssh disconnect.
    # B183 trim 1: Launch builder sessions directly inside their assigned worktree cwd with pre-seeded branch context.
    setup_lines = []
    if card:
        target_dir = f"F:/MTS/mts-jis-nuc-{card}"
        branch = f"jis-nuc/{card}"
        setup_lines.extend([
            f'Set-Location F:/MTS',
            f'git fetch -q origin fast-track',
            f'if (!(Test-Path "{target_dir}")) {{',
            f'    git worktree add -q "{target_dir}" -b "{branch}" origin/fast-track 2>$null',
            f'    if ($LASTEXITCODE -ne 0) {{ git worktree add -q "{target_dir}" "{branch}" 2>$null }}',
            f'}}',
            f'if (Test-Path "{target_dir}") {{',
            f'    git -C "{target_dir}" merge -q --ff-only origin/fast-track 2>$null',
            f'}}',
        ])
        set_loc = f'Set-Location {target_dir}'
    else:
        set_loc = 'Set-Location F:/MTS'

    lines = [
        '$env:Path += ";C:/Users/E-ngineers/.local/bin"',
        f'$d = "F:/MTS/nuc_wake/{name}"; New-Item -ItemType Directory -Force $d | Out-Null',
    ] + setup_lines + [
        "$p = @'",
        prompt,
        "'@",
        '[IO.File]::WriteAllText("$d/prompt.txt", $p)',
        # A child of the ssh session dies when it disconnects (empty logs, no process). A one-shot interactive
        # scheduled task for the logged-on user is not tied to the ssh session and needs no password.
        '$c = (Get-Command claude.exe).Source',
        f'$cmd = "{set_loc}; Get-Content -Raw $d/prompt.txt | & \'$c\' -p --model {model} '
        '--permission-mode bypassPermissions > $d/out.log 2> $d/err.log"',
        '$a = New-ScheduledTaskAction -Execute "powershell.exe" -Argument ("-NoProfile -WindowStyle Hidden -Command `"" + $cmd + "`"")',
        '$pr = New-ScheduledTaskPrincipal -UserId "e-ngineers" -LogonType Interactive',
        f'Register-ScheduledTask -TaskName "MTS-Wake-{name}" -Action $a -Principal $pr -Force | Out-Null',
        f'Start-ScheduledTask -TaskName "MTS-Wake-{name}"',
        '"started"',
    ]
    return "\n".join(lines) + "\n"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry", action="store_true")
    ap.add_argument("--model", default="claude-sonnet-5-5")
    ap.add_argument("--name", default="default", help="worker name: own log dir, lets several run in parallel")
    ap.add_argument("--card", help="work exactly this task card id instead of the generic prompt")
    ap.add_argument("--prompt-file", help="override the boot prompt (UTF-8 text file)")
    a = ap.parse_args()
    prompt = open(a.prompt_file, encoding="utf-8").read().strip() if a.prompt_file else PROMPT
    if a.card:
        prompt = CARD_PROMPT.format(card=a.card)
    script = build_script(a.model, prompt, a.name, card=a.card)
    if a.dry:
        print(script)
        return 0
    r = subprocess.run(GATE + ["ps"], input=script, text=True, capture_output=True)
    out = "\n".join(l for l in (r.stdout + r.stderr).splitlines() if "quantum" not in l and "upgraded" not in l)
    print(out.strip() or f"exit {r.returncode}")
    return r.returncode


if __name__ == "__main__":
    sys.exit(main())
