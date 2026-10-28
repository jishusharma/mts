# NUC GPT plan, 2026-10-15 (operator: Astra light only, only the most valuable tasks)

Nothing here has been launched. The operator approves first. Sibling note: TRACK_RECORD.md (past GPT successes and failures) in this folder.

## 1. Setup found

Read-only, via the nuc_gate. The gate's command set is now bare (`status`, `models`, `ps` ...): the memory line "v3 status" is stale, `v3` is refused ("not whitelisted"). `models` lists Ollama models only and printed nothing (no model loaded, ollama idle); it says nothing about GPT. GPT facts come from `ps` with a read-only PowerShell script on stdin.

| Item | Found |
|---|---|
| Host | JIS-NUC, up 2 days, 17.5 of 31.8 GB RAM free, no Ollama model loaded, no worker process |
| Codex processes | 2 `codex` + 1 `codex-computer-use-swift`, started 2026-10-15 17:44 local: the operator's Codex app is open |
| `CODEX_HOME` | `F:\codex_home` |
| Default model (app sessions) | `F:\codex_home\config.toml`: `model = "gpt-6.1-sol"`, `model_reasoning_effort = "medium"`. This is NOT Astra. Every hand-started app session uses it |
| Allowed efforts in the app | `[desktop] enabled-reasoning-efforts = ["low","medium","high","xhigh","persistent","ultra","max"]` |
| Unattended lab | Windows task `MTS-CodexLab`, `codex_run.py tick` every 30 min; starts `codex exec -m <model> -c model_reasoning_effort="<effort>"` (scripts/dev/codex_run.py:469) with the card's setting from `tasks.codex_setting` (scripts/dev/tasks.py:211-226) |
| Lab model rule today | luna at low/medium by default. Astra only on a card with `crucial: true` or `gpt_only: true`, forced to low whatever the card says (tasks.py:49-50, 221-224). Model names in the repo: `gpt-6-astra`, `gpt-6-luna` |
| Lab state now | last tick 12:30Z IDLE (7 lab runs this window, cap 4). Last runs: `tom-btc-event-study` BLOCKED, `lc-levels-hold` BLOCKED then SHIP_FAILED (runs.jsonl). `gap-g4-through-ticks-flag`, `gap-g6-trial-ledger`, `tom-btc-event-study` are ready CODEX cards and will run on luna when the window resets |

"Astra light" = `gpt-6-astra` at `low` effort. (Assumption: the app's name for it. If the app names it differently, the model id in config.toml must be copied from the app's model picker.)

### Exact change to pin Astra light and block Astra medium
1. Lab path (unattended): already pinned. A crucial card runs `gpt-6-astra` / `low`; `effort` on the card is ignored for astra. Two hardening edits in the repo (one small card, Sonnet): (a) in `scripts/dev/codex_run.py:59` delete the `("gpt-6-astra","high")` and `("gpt-6-astra","medium")` rows of the cost table, and (b) add a test that `codex_setting` never returns astra with effort other than low (a test for this exists in test_codex_run.py:48 for the crucial flag only).
2. App path (hand-started sessions, the real gap): edit `F:\codex_home\config.toml` on the NUC:
   ```
   model = "gpt-6-astra"
   model_reasoning_effort = "low"
   ...
   [desktop]
   enabled-reasoning-efforts = ["low"]
   ```
   `enabled-reasoning-efforts = ["low"]` hides medium/high in the app picker (UNVERIFIED that the app honours the list as a hard block; if not, the config default still starts every session on low). The edit is a settings change on the NUC, so the operator (or a gate `ps` script they approve) makes it; I did not touch it. Never edit `auth.json`.
3. To stop the cheap automatic runs the operator does not want: `python scripts/dev/codex_run.py stop "operator 2026-10-15: GPT only for valuable tasks"`, then `resume` after the 3 cards below are queued (the three ready non-crucial cards run on luna, not astra, so this is about spend, not the model).

## 2. The 3 tasks (each justified as "needs a second model family", none overlaps Claude's Tom/Malkan/Fabio extraction sessions)

### T1. Independent blind eye-read of the 80 Tom lab charts (gate G3, third reader)
- Goal: a second, model-independent reader marks every chart take/skip, which Tom concept (TOM_ON_BTC ids A-C3, A-P1..A-P8) is visible, and where stop and target would be, before seeing any other reader's marks. Kappa per concept against Claude's and the operator's marks.
- Inputs: `MyTradingSys/research/tom_btc_2026-10-13/charts/C001.png..` (82 tracked files, checked with `git ls-files`), the concept table in `TOM_ON_BTC.md`, the mark format of the existing card `tom-btc-eye-read` (state ready, lane SONNET).
- Output: `MyTradingSys/research/tom_btc_2026-10-13/marks_gpt.csv` and `EYE_READ_GPT.md` (kappa per concept, disagreements listed).
- done_when: all 80 charts have a row; marks written and committed BEFORE the run opens `marks_claude.csv` / the operator's marks (the pack for the run excludes them, see section 3); a script prints kappa per concept vs each other reader.
- Why GPT, not Claude: G3 only means something if the readers' errors are independent. Claude wrote the catalogue and the concept table; a Claude reader shares its blind spots. A different model family on images is the independent check. Vision on 80 images is also work Claude's budget is short on.
- Risk: vision quality on dense TradingView charts is unproven (see TRACK_RECORD.md). Gate: run 10 charts first and have the operator spot-check 3 before the other 70.

### T2. Independent "NOT STATED" and quote-support audit of SETUP_CATALOG.md (gate G2 -> G3)
- Goal: for the 10 setups that have real trades (TOM-1, -2, -3, -5, -8; FAB-1 to FAB-5), check each row's entry / stop / target cells against the raw transcripts: (a) every cell marked NOT STATED, find any place the trader does state a stop or target (false NOT STATED means a SOURCED number gets replaced by an OURS one at G5); (b) every quoted line really says what the row claims (meaning, not just that the string exists: `verify_extract_quotes.py` already proves the string exists); (c) wrong setup assignment of real trades.
- Inputs: `MyTradingSys/research/setup_catalog_2026-10-15/SETUP_CATALOG.md` (1219 lines; sections 0, 3, 4 and the trade rows), the raw transcripts the rows cite (`raw_transcripts_canonical/`), the Tom and Fabio ledgers.
- Output: `MyTradingSys/research/gpt_lane_review_2026-10-15/CATALOG_AUDIT.md`: table of setup x cell x verdict (confirmed / false NOT STATED with file:line quote / quote does not support / mis-assigned trade). Changes nothing in the catalogue.
- done_when: all 10 setups covered; every finding has file:line and a verbatim quote of at most 25 words; the run finishes the quote check script on its own quotes.
- Why GPT, not Claude: Claude (Sonnet sessions) wrote the catalogue and a Claude reader tends to confirm it. Fable's audit on 10-20 (FABLE_PROMPT_PACK A3) reads raw sources too, so GPT's output is a cheap pre-pass that gives Fable a list of cells to settle instead of a full re-read. Long-document reading across many transcripts is where a second strong model adds the most.

### T3. Independent re-derivation of the G5 formula chain in FORMULAS.md
- Goal: from the written definitions only (never the code), recompute the worked examples and expected numbers for the chain that every G5 event study uses: section 7 forward return / MAE, section 12 core ATR (SMA), section 13 shared cost model, section 17 net R:R fee model. Compare with the numbers in FORMULAS.md, the layer TEST_PLANs and the implementations (`runtime/mts_math.py` calculate_net_rr, `layers/positioning/trade_costs.py`, `layers/runner.py`).
- Inputs: `MyTradingSys/backtest/layers/FORMULAS.md` (sections 7, 12, 13, 17), the implementations only for the comparison step, run after the numbers are written.
- Output: `MyTradingSys/research/gpt_lane_review_2026-10-15/FORMULAS_REDERIVE.md` plus its own scratch script `.../rederive.py` (stdlib only).
- done_when: a table example x FORMULAS.md value x GPT value x repo value x match; every mismatch has the definition line that decides it. Mismatches become B-items, not edits.
- Why GPT, not Claude: fees and stop sizes enter only at G5 and every verdict after that rests on this chain; the 2026-09-28 audit that wrote these numbers was Claude (LESSONS_LEARNED D1 shows a Claude-derived test inherited a wrong formula). This is the same-model-family trap the second model removes. It does not duplicate the raw card `indicator-values-multi-model-audit` (that samples live indicator values from snapshots; this checks the fee/R chain); say the word and T3 folds into it.

Not picked (trivial or already Claude's): any extraction, the Malkan or Krown work, `gap-g4-through-ticks-flag`, `gap-g6-trial-ledger`, the Fabio date-match card.

## 3. How to launch each one (after the operator's yes; nothing was run)

Existing lane (CODEX_START.md, LAYER_LAB.md): a card in `MyTradingSys/system/tasks/`, lane CODEX, shipped to `origin/fast-track`; `MTS-CodexLab` on JIS-NUC picks the first ready unclaimed card at its next 30-minute tick, runs `codex exec`, ships, releases. No manual start is needed. Spend guard: `codex_run.py status` shows the window (50 pts, 4 runs, 1 astra run per window); the lab is waiting for its window now, so the first run starts at the reset.

Per task (from the repo root of a work tree):
```
python scripts/dev/codex_run.py ask "GPT blind eye-read of the 80 Tom lab charts (third reader)" --kind audit --id gpt-g3-tom-eye-read --scope MyTradingSys/research/tom_btc_2026-10-13/charts --scope MyTradingSys/research/tom_btc_2026-10-13/TOM_ON_BTC.md --goal "<T1 goal and done_when>"
python scripts/dev/codex_run.py ask "GPT audit of SETUP_CATALOG NOT STATED cells and quote support, 10 setups with real trades" --kind audit --id gpt-catalog-notstated-audit --scope MyTradingSys/research/setup_catalog_2026-10-15/SETUP_CATALOG.md --goal "<T2 goal and done_when>"
python scripts/dev/codex_run.py ask "GPT re-derivation of FORMULAS.md sections 7, 12, 13, 17" --kind audit --id gpt-formulas-rederive --scope MyTradingSys/backtest/layers/FORMULAS.md --goal "<T3 goal and done_when>"
python scripts/dev/tasks.py flag gpt-g3-tom-eye-read crucial
python scripts/dev/tasks.py flag gpt-catalog-notstated-audit crucial
python scripts/dev/tasks.py flag gpt-formulas-rederive crucial
python scripts/dev/tasks.py check <id>
python scripts/dev/sync.py ship
```
`crucial` is what makes the card run `gpt-6-astra` at `low` (the card's own effort is ignored); without it the card falls back to luna. Run them one per window (the lab allows 1 astra run per window), T2 first, then T3, then T1 after its 10-chart spot check. Hand-start alternative: in the Codex app project `F:\MTS\mts-codex`, after the config.toml edit above, paste the CODEX_START.md block and let it take the card; `python scripts/dev/codex_pack.py <card-id>` builds the pack. For T1 the pack must exclude `marks_claude.csv` and the operator's marks (blind): scope_out on the card, and run it from a tree at a commit before those files exist if the card cannot enforce it.

Open for the operator: (1) approve the three cards and the order; (2) make the config.toml change (item 2 above) or allow a gate `ps` script to do it; (3) pause the lab (`codex_run.py stop`) until then, or accept that the three ready luna cards run first.
