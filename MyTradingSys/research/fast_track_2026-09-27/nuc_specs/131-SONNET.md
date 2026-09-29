# 131-SONNET: `mts kill-mainnet` (audit item #5, smoke blocker)

## Why Sonnet, not Qwen
The change is in `mts.ps1` (12.5 KB, PowerShell), which cannot be run offline and is too big to send whole with its test inside
a 5k-token package. It is about 12 lines, but a mistake here means the panic button does not flatten mainnet. A Sonnet edit plus the
static test is the cheapest safe route. `kill_switch.py --mainnet` itself is already fixed (premainnet1 B1/B2) and tested; only the
launcher is missing.

## Edits
1. Verb table (between VERBS-BEGIN/END), directly under `kill`:
   `@("Safety",      "kill-mainnet", "EMERGENCY on MAINNET: cancel every order, close every position, pause")`.
   Column width of `mts help` is `{1,-9}`; change it to `{1,-13}` so the new verb does not break alignment.
2. New case `"kill-mainnet" { ... }` after `"kill"`, 4-space indent like the others (the static test matches `^    "kill-mainnet" \{` ... `^    \}`):
   - Say in Red: "KILL SWITCH - MAINNET (REAL MONEY) - cancels EVERY open order and closes EVERY position on the LIVE account," / "then sets HALT so nothing trades until you run: mts resume".
   - `if (-not (Confirm-Word "KILL" "Are you sure? This acts on the MAINNET account.")) { exit 1 }`
   - `Remove-Item Env:MTS_ACCOUNT -ErrorAction SilentlyContinue` (a stale testnet sub-account label would otherwise stop select_environment; kill_switch also ignores it, this is belt and braces).
   - `Py (Join-Path $Exec "kill_switch.py") "--confirm" "KILL" "--mainnet"; exit $LASTEXITCODE`
     (kill_switch.py then asks for the typed mainnet confirmation itself via select_environment - keep that second prompt).
   - Must not contain `--account`.
3. In the existing `"kill"` case add one line, after the two `Say` lines: `Say "For the MAINNET account use: mts kill-mainnet" Yellow`. Its command line stays without `--mainnet`.
4. `MTS_USER_GUIDE.md`: add the verb wherever the other Safety verbs are listed (`python scripts/dev/check_guide.py` fails otherwise).
5. `MAINNET_READINESS_CHECKLIST.md`: put the exact command `mts kill-mainnet` (and the direct fallback
   `python MyTradingSys/execution/kill_switch.py --confirm KILL --mainnet`) at the very top of section C; tick audit item #5.

## Tests and gates
`MyTradingSys/execution/test_mts_kill_mainnet.py.new` (written; static text checks of mts.ps1; 3 failures + 2 errors on the current file).
Promote to `test_mts_kill_mainnet.py`, and register it in whatever list `run_all_tests.py` uses for the execution suites if it does not glob.
Gates: that test, `python scripts/dev/check_guide.py`, `python scripts/dev/run_all_tests.py --quick`. Then, with the operator (not the agent),
one dry parse: `pwsh -NoProfile -Command "& { . ./mts.ps1 help }"` must list both kill verbs; do NOT run `mts kill-mainnet` against a real account.
