# Night plan 2026-11-02 (operator order, voice)

Login C is at about 84% weekly and must stay under 90% until its reset (Wed 2026-11-04 01:30 IST = 2026-11-03T20:00Z); the last 10% is kept for the final 24 h. So logins A and B take the work now, B first (its week reset on 2026-11-01, next reset 2026-11-08). Test first, ship each card with `sync.py ship --release <slug>`, one line per ship with `Result:`.

## Login B (JIS-NUC), take in this order
| Card | Model |
|---|---|
| sonnet-new-tests-must-fail-on-old-code-audit | Sonnet |
| tl-michael-lines-detect-alert | Sonnet |
| fee-figure-unify | Sonnet |
| run-all-tests-quick-takes-25-min | Sonnet |
| codex-run-auth-failure-must-not-mark-gpt-lane-down | Sonnet |
| cost-checkup-doctor-section | Opus (set_session_model, read back, then the task) |
| haiku-recount-testnet-readout | Haiku |
| every ready [GEMINI] card via `gemini_queue.py run <id>:low` | Gemini |

## Login A (JIS-LAPTOP)
gpt-audit-formulas-vs-cowen-band-phase-tag, gpt-audit-formulas-vs-stochastic-rsi-chart-verify, fabio-v3-model-b-managed-is-rerun, ask-p0-13-positioning-flags (JIS-NB lane: take it if JIS-NB has no free slot).

## Console API credit (all logins)
Pre-approved, see OPERATOR_DECISIONS 2026-11-02. Bulk read-only work (quote checks, recounts, labels, blind reads) goes through `scripts/dev/api_batch.py` on Haiku; one hard question at a time on Opus or Fable with `--max-tokens` 32000+. The key file is on JIS-NB only (F:/ClaudePlaform/key.txt); ask login C's coordinator to run a job, never copy the key.
