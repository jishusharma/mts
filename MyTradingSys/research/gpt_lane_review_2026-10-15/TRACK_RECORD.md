# GPT / Codex lane: track record before new work (2026-10-15)

Read-only review. Sources: LAYER_LAB.md, CODEX_START.md, layer_lab/INDEX.md and the 2026-10-11..15 reports, `codex_usage.json` (10 retained runs), `git log origin/fast-track` (2026-09-24 on). Model/param quality was not re-audited beyond what the reports themselves cite.

Counts (parsed from git): 23 lab run commits (`lab <card>: DONE|BLOCKED`) = **12 DONE, 11 BLOCKED**; 9 `lane health: GPT down (window)` commits; 148 commits mention codex in all (mostly claim/release/merge churn). INDEX.md lists 20 deliveries (9 audits, 11 builds) and 18 cards queued/raw/blocked.

## Delivered
- Audit of the DAX backtest harness, 8 HIGH + 6 MED: `reports/2026-10-11_lab-audit-tom-dax-bt.md` (commit a331bcc2 then d3153179). Claude spot-check: H1, H5 MATCH.
- Eight DAX harness fixes H1-H8, each red-then-green (33 -> 62 tests): `reports/2026-10-12_lab-dax-*.md`, commits 6167c20f, 88be8fcd, babde551, 46e0592e, 4503f2cb, fc94fc2e, 88f5fbde.
- Ledger/frame audits: Tom 37 rows (4 HIGH, 4 MED) `2026-10-12_lab-audit-tom-ledger-frames.md`; Fabio `rv05`, `rv06`; DAX re-audit `rv02` (4 HIGH, 7 MED).
- BTC builds: G1 power/MDE helper (`gap-g1-power-mde-helper`, 7 tests, f01208e7); Tom BTC chart lab, 105 candidates / 80 blind charts (cc6d1b8f); candle-close DEV study, 126 arms, 0 pass, Claude spot-check MATCH on a raw 1m bar (`2026-10-14_lab-candle-close-dev.md`).
- Candle-close research + independent audit (8 findings): `2026-10-14_lab-candle-close-research.md`, `2026-10-14_candle-close-independent-audit.md`.
- Strategy audits 2026-10-15 (app sessions on NUC): `strategy-direction-audit.md`, `revalidate-strategy-audit-with-counterev.md` + `revalidate_strategy_proofs.py` (4 synthetic witnesses, Claude re-ran: PASS, `claude-side-audit.md`).
- Infra built around it: lane health/reroute (`lane_health.py`), spend guard, usage doc (4857882c, 91701a36).

## Worked
- Narrow, spec-clear audits and fixes with a test that fails first (DAX H1-H8) shipped cleanly, one card each.
- Independent audits found real defects in Claude's work: DAX stale proof count (Java B144), `tom-profile-shape-parity` T2 drawn 0.500 vs computed 0.200 (`reports/2026-10-13_tom-profile-shape-parity.md`).
- Reports cite file:line and MATCH/MISMATCH/NOT_IN_DATA; the `revalidate` report corrected GPT's own earlier advice (items 1-6) and shipped a runnable proof.
- Honest BLOCKED: it refused to invent labels, data or gates (below) instead of fabricating a result.
- Claude's spot-check of the two claims it re-ran (candle-close 126-arm mean, divergence-study stop logic) matched.

## Did not work
- **9 of 11 BLOCKED runs were missing-input cards; the 7 still in `codex_usage.json` burned ~2.5M tokens for no result** (`codex_usage.json`: lc-levels-hold 276k, tom-btc-event-study 428k+274k, tom-v2-btc-min-stop-width 485k+232k, qriptal-score-binance 474k+320k; plus lc-levels-hold 314k INCOMPLETE):
  - `lc-levels-hold`: no 1m klines on the NUC (`2026-10-14_lc-levels-hold.md`; LAYER_LAB.md:55-58 already warned).
  - `tom-v2-btc-min-stop-width`: gate artifact `DAX_BT_V2.md` absent; card contradicts itself (goal/depends keep DAX, note drops it) (`reports/2026-10-14_tom-v2-btc-min-stop-width.md`; `revalidate` R2).
  - `tom-btc-event-study`: no reader marks, A-P10 NOT_IN_DATA (`2026-10-15_tom-btc-event-study.md`:findings table); blocked twice.
  - `qriptal-score-binance`: no call ledger, only raw captions (`2026-10-14_qriptal-score-binance.md`); blocked twice.
  - `tom-profile-shape-parity`: blocked twice (62c914f0, 66c36d93).
- **Rework / duplicate pickups**: `claim lab-dax-unavailable-flow` x6, `lab-dax-readiness-gate` x6, `lab-audit-fabio-ledger-frames` x4 (git log). `rv02` re-audit found 4 HIGH + 7 MED still wrong in the "fixed" harness; candle-close audit found the study's test import can exit 0 with 8 skips.
- **Stalls**: lab stuck on unmerged INDEX.md (bde65eb7, repair 827daf31/7f7b1c9d/e8ec0165); `tom-btc-chart-lab` (2.43M tokens) and `gap-g1` ended SHIP_FAILED, Claude shipped by hand (f1b5e664); `lab-audit-tom-dax-bt` closed by Claude (frames not on NUC).
- **Allowance**: astra/high 3.7-5.1M tokens = 81-90 window pts per run and hit the usage limit after 777 s (LAYER_LAB.md:77-78, 92-93); lane marked down 9 times; weekly use 57% on the Plus plan today.
- **Wrong numbers / unsourced params**: none found in the reports I read; Claude corrected only R3 holdout wording and N2 scope in the GPT revalidation (`claude-side-audit.md`). The 2026-10-15 audits are labeled "quick documentary" and the first was later narrowed by its own revalidation. No profitability result exists from this lane: candle-close 0/126, published screen 0/62.

## Report types received
1. Audit verdict `FIX-FIRST` + findings table (HIGH/MED/LOW, file:line, MATCH/MISMATCH/NOT_IN_DATA): all 9 audit deliveries; none returned `SOUND`.
2. Build report: files, red-then-green test counts (7-62 tests), flag-off.
3. Run/study report: headline counts (126 arms, 105 candidates) with a verifier.
4. BLOCKED report: what was checked, what is NOT_IN_DATA, proposed fix.
5. Free-form strategy memo from app sessions (longest, 16-18 KB): contains advice later withdrawn.

## What must change before new GPT work
1. Pre-flight each card: every input file/data path/gate artifact exists on the NUC (check by script) or the card is not issued. Blocked runs cost 230-485k tokens each for zero output.
2. High-value only = audits/second-checks of Claude work and short spec-complete builds with a red-first test; no data-bound or label-dependent cards (klines, frames after 2026-10-12 copy, Qriptal ledger) until the data is copied.
3. Model: LAYER_LAB.md:17-22 runs `luna/medium` by default and astra only when `crucial: true`, low effort only. "Astra light only" needs `tasks.codex_setting`/`CODEX_KINDS` changed (the operator confirms "light" = astra at low effort; astra-low cost is unmeasured: 0 astra runs in the retained data).
4. One card = one claim: stop the 4-6x claim/release loop (cause not diagnosed here); fix SHIP_FAILED and INDEX.md merge before queueing more.
5. Claude refines the card text (no contradictory goal/depends) and spot-checks one claim per report, as CLAUDE.md already requires.
6. Trial ends about 2026-11-11 (LAYER_LAB.md:106): nothing may depend on the lab.
