# Desk inject check (card aibridge-desk-no-inject-after-075)

Status: PARTIAL. Repo side verified; the Desk post-F5 panel count is operator-only and still missing.

## Versions (this checkout, host JIS-NB, 2026-11-04, `aibridge_health.py`)
- installed 0.7.25 = running agent 0.7.25 = checkout 0.7.25 = trunk 0.7.25
- The Desk report (panel 0.7.5, 0/200) predates 0.7.7-0.7.25: a stale install is the likely cause.

## Selector evidence (no new failing case found)
- `scripts/aibridge/tests/fixtures/deepseek_reply.html` and `block_select.test.js` already cover the DeepSeek reply DOM: 11/11 PASS (incl. 0.7.8 "Thought for N seconds" root, 4-block reply, whitespace jitter).
- `handsfree.test.js` PASS.
- DECISION (OURS): no content.js change, no version bump; no failing selector was reproduced.

## Still needed from the Desk (operator click, agents cannot drive Chrome)
1. On Desk: merge origin/fast-track; `python scripts/dev/aibridge_install.py F:/AIBridge --restart-agent`; `python scripts/dev/aibridge_health.py` (expect 0.7.25 x4).
2. chrome://extensions > AIBridge > Reload in each profile; F5 the DeepSeek tab.
3. Record the panel count n/200 and whether a posted block ran here. If no block runs: save that DOM as a new fixture, write the failing block_select test first.
