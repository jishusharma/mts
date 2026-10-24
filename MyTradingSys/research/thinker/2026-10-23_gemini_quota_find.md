# Gemini/Antigravity quota command: find (card find-gemini-antigravity-quota-command-an)

Result: NOT_IN_DATA. No command in the repo reads the Gemini/Antigravity quota.

Searched: `grep -ril antigravity scripts MyTradingSys/system` (20 hits). Read for a quota/usage call: scripts/dev/gemini_queue.py (only launches `agy --print`, path ~/.gemini/bin/agy.exe, no usage call), scripts/dev/ask_model.py (same, no usage call), MyTradingSys/system/GEMINI_START.md. Other hits (stop_guard, wt_maint, ROSTER, HTML artifacts, desk_queue) mention the name only.

Only quota source named: GEMINI_START.md lines 17-19: the Antigravity model menu `View Usage` (GUI), three pools (Gemini 3.8 Flash; Claude Opus/Sonnet 5.5 + GPT-OSS; Gemini 4 Argon weekly only), weekly + five-hour limits. No CLI form, no sample output line: NOT_IN_DATA. Not tried: running `agy` with a usage flag (starting a Gemini run is out of scope).

DECISION (OURS): Gemini column in the usage ledger is `source=gemini_manual`, filled by the operator from `View Usage`, never blocking, no network login.

Codex: allowance line parsed by scripts/dev/codex_status_parse.py (standalone). Real sample (LAYER_LAB.md:213):
`Codex allowance (plus): 5-hour window 6% used (resets 10-19 08:32Z); week 27% used (resets 10-24 20:41Z)`
Parsed: window 6.0%, week 27.0%. Must be read on JIS-NUC (ssh gate); local machine shows no allowance. usage_log.py wiring is a later card.
