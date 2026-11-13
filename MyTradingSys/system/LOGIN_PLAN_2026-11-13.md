# LOGIN PLAN, 2026-11-13 18:25Z (Supervisor C on the desktop, operator order 18:15Z)

Operator order: logins A and B and both Gemini accounts sit idle; load them in line with the edge push
(`PLAN_EDGE_5H_2026-11-13.md`). Gemini quota on both accounts expires in about 24 h: run every card.
A card that is no longer `ready` is skipped (`tasks.py check <id>`). Before each claim: `sync.py claims`, `mts_signal.py read --hours 1`.
Workers are Sonnet background Agents (Haiku for mechanical); Gemini always `:low`. Testnet only; no deploy; no Chrome on the laptop.

Readings 18:03Z: A 5h 20% week 4% (reset 11-20) | B about 29% of the week left (reset 11-15T17:00Z, stale reading) | C 5h 63% week 68%/85, CRUCIAL-ONLY.

## Login A (laptop, Supervisor A): BULK. Keep 3 workers running until the 5-hour window is at 85%.
Wave 2 edge tests first (pass rule in PLAN_EDGE_5H; PRE_REG needs `## Context` + `Regime mix:`; layer_map row `"trials": null`; public Bybit / data-api.binance.vision data only):
1. edge4-rsi-4h-le12-daily-lt30-1113: 4h RSI <=12, daily RSI <30, next candle closes higher, stop = low of the signal candle, exits 1R/2R/3R/time; also 8h and 12h RSI extremes; 20 perps since 2020. (Seen on BTC: 4 of 5 episodes reached 2-3R; too few, so pool coins.)
2. edge4-malkan-divergence-r03-r04-1113: Malkan divergence rules MAL-R03/R04 from the Gemini rule mining (closes only, 12/18 bars), 20 perps 1h/4h.
3. event-sweep-squeeze-sequence-study-1111 (his sequence: event before the US open sweeps a prior level, then squeeze).
4. placebo-for-the-77-acceptance-claim-rand; flip-engine-follow-up-session-adjusted-s.
Then, in order: tf-x1-fabio-orderflow-gaps-1113, tf-x3-tom-pbd-balance-1113, tf-x2/x4/x5, tf-s1-answer-ledger-1113 (rule answers from held transcripts);
live-aid-flag-hitrate-grey-1113, live-aid-one-bias-line-1110, live-aid-closed-bars-sweep-1110 (Live Aid; one worker at a time on `tools/live_aid/`);
cbp-extract-errors-1112, cbp-yt-budget-starved-1111; then `tasks.py next` (SONNET lane, no F: drive).
Gemini on the laptop (argon account): Supervisor A runs the line in `GEMINI_NOW.md` itself from a shell (`gemini_queue.py run ... :low:argon`); if `agy` is not signed in, signal `gemini-laptop BLOCKED <reason>` and move on.

## Login B (NUC): needs one operator-started session (no session is alive there; last seen 16:15Z).
Start line: `You are Builder. Login B. Follow MyTradingSys/system/LOGIN_PLAN_2026-11-13.md section Login B; tasks.py next loop; report each ship with mts_signal.py.`
Queue (needs F:/MTS data, so NUC only): rule-book section 5 (our measured numbers) for each Gemini-filled book in `research/indicator_rulebooks/INDEX.md`;
lab-verify-footprint-vs-indicator-delta; sim-desk-11-09-census-regenerate-per-tra; krown-s8-forward-weekly-readout; forward-slots-audit-and-readout-1111; main-folder-staged-blocks-ff.

## Gemini flash account (NUC `agy`, ordered from the desktop by the gemini-yt session)
Run order: remaining `gemini-rulebook-*-1113` cards, then every `gemini-edge-*-1113` flash card still `ready`
(mine-cbp, mine-malkan, mine-nk, hilega-formula, the blind reviews, nk-batch1..5), then gemini-conceptualizer-quote-audit-flash-1113,
gemini-crypto-statements, tf-g1/tf-g3 leftovers. Outputs land on `gemini-q/<id>`; a Claude session verifies quotes and ships.

## Login C (desktop): no new workers this window (plan: CRUCIAL-ONLY). Runs: feed watcher (Haiku, to 21:00Z), gemini-yt, CI watch, cleanup.
