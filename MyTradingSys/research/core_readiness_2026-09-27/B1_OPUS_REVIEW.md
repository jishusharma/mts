# B1 Opus review — 2026-09-27

Verdict: DO NOT COMMIT AS-IS. One blocking defect, one-line fix. verdict.py.new and build_mo_cli.py.new are OK.

## BLOCKER — no-candidate candles: live logs pd=error, replay says aligned
- math_object_builder.py:406 only sets proof_direction_status inside `if candidates` (line ~380). With no setup_candidates the key is absent.
- start-trading-day.ps1.new: $pd starts as "error" and only becomes aligned or contradiction if status is one of those. No candidate means pd=error on EVERY no-candidate candle, plus a PD_ERROR log line each time.
- verdict.py.new proof_dir_of: pd None + no setup_candidates returns "aligned" (both modes).
- parity.py:33 requires pdp == pd, so every no-candidate candle becomes a MISS and parity exits 1. The PD_ERROR spam also hides the real error signal the fix exists to surface.
- Fix (ps1.new, after the status check; $snap is already loaded at line 444):
    if ($status -eq "aligned" -or $status -eq "contradiction") { $pd = $status }
    elseif (-not $status -and -not $snap.setup_candidates) { $pd = "aligned" }
  This mirrors verdict.py.new exactly. It's still gated on rc=0, so it stays fail-closed on a crash.
- Not verified: whether WATCH/SETUP_FORMING can occur with zero candidates, i.e. whether the defect also changes verdicts and not just pd/parity. Either way the fix is needed.
- After patching, re-run fail_closed_spec.py and parity.py (the scratch-copy proof predates this fix).

## Checked OK
- Invoke-WithTimeout returns the int ExitCode (-1 timeout, -2 spawn fail), so the $moRc -eq 0 gate is valid.
- The rc gate also stops a stale app_mo.json left by a failed ConvertFrom-Json from being read next candle.
- build_mo_cli.py.new: atomic tmp+os.replace; on exception exit 1 and tmp removed. The comment says "leave no output file", but a prior file may exist; it's harmless because of the rc gate plus the Remove-Item. Cosmetic only.
- verdict.py.new cap mirrors PS cap (WATCH/SETUP_FORMING -> WAIT_PROOF when pd not in aligned/contradiction).
- Minor: parity.py/replay.py still call proof_dir_of(s) with default fail_closed=False. Correct for pre-B1 archived logs; post-B1 logs need fail_closed=True or the error cases diverge. Decide the cutover (timestamp switch) before logs mix.
