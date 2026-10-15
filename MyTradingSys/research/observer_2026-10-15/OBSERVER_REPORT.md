# Observer report, 2026-10-15 (cross-session alignment)

Observer: Opus session local_9e6b2df7. It was started by the coordinator local_1c4041fd, whose transcript file is 62faa820. Read-only on other sessions' files.
The operator added, mid-run: "arrange those things, not just prepare a report". So the actions under "Already done" were taken directly. Everything else goes to the coordinator, which decides.
Inputs: list_sessions (60, incl. archived), list_events on 10 sessions, get_usage, origin/fast-track at 0f55c970, NUC lab status over the ssh gate at 13:21Z, and the files cited inline.

## Already done by the observer (13:20-13:45Z)
| Action | Why | Check |
|---|---|---|
| Started **lab-unstall** (Sonnet, local_df85faaa). It ships the stalled NUC lab tree, spot-checks lc-levels-hold, and parks 2 missing-input CODEX cards. | The NUC `codex_run.py status` (13:21Z) says: lab idle 14.4 h, "41 unshipped file(s)"; lc-levels-hold at 2026-10-14 23:00Z SHIP_FAILED after 2.7M tokens, with a finished result. T2/T3 (Astra light) cannot run until this ships. | `codex_run.py status` shows no unshipped hold; lc-levels-hold report on origin with a spot-check line |
| Started **krown-g2** (Sonnet, local_e1e06d4d): Krown S1-S9 in the catalogue format plus a cross-trader overlap table. | LAYER_REBUILD_PLAN s6 item 4 had no owner. Krown is "G2 on paper" only. | KROWN_SETUP_CATALOG.md on origin, quote check PASS |
| Added **PAIRED REVIEW** (section 4b) to `methodology/screenshot_intake.md`: a blind Haiku reader starts with the Sonnet reader, then reconcile, then one ship. | The operator asked for side-by-side review. The 10-15 review ran after the read: it caught 5 WRONG + 1 UNSUPPORTED of 22 claims, but cost wall-clock and anchored on the draft. | The next set's `_REVIEW.md` has `## Blind read`, and the extract and review land in one sha |
| Told fix-selftest-gate (local_eaaf5745) to notify lab-unstall, krown-g2 and live-read-12h too. | They will hit the same red gate. | Each retries the ship once |
| Corrected a false "shipped" claim to the coordinator. | Below, accuracy A1. | The coordinator corrects it with the operator |

## Findings with evidence
### Waste
- W1. **The ship gate has been red on one known flaky test for about 13 h.** The card `aibridge-live-selftest-flaky` was filed 10-14 (d140cbaa), and nobody owned it until 13:15Z today (local_eaaf5745). Today it blocked live-read (afaf3dae, 6d000c06, 1ba57f23), gpt-cards (cc7feda5, 2 failed ships at about 11 min each) and malkan-extract (re-ship running). It fails only in the parallel run, on a different sub-check each time (gpt-cards' report, local_e18ebf13).
- W2. **GPT lane: about 2.5M tokens went on missing-input cards** (TRACK_RECORD.md "Did not work"), and the lab then idled 14.4 h on an unshipped tree. Origin still listed 5 luna/medium cards as ready, including qriptal-call-ledger and tom-btc-other-setups, whose inputs are known missing. This happened although LAYER_LAB.md:55-58 already warned.
- W3. **Commit mix over 3 days** (593 non-merge commits on origin, classified by path, script in the observer scratchpad): 244 claim/release (41%), 237 infra/process (40%), 68 research (11%), 44 lane-health pings (7%). Since the rebuild plan (8f5b3f1e, 14:42 IST) the mix is better: 50 commits = 21 claim/release, 15 research, 14 infra.
- W4. **The dispatcher still starts a Haiku Claude session to say NOOP** (local_f5dda709 at 13:08Z: "TICK NOOP ... runnable=0"). That is hourly since 07:39Z and was every 10 min before; about 44 sessions today. 9fe73003 intended "Claude starts only on TICK KICK". Each run costs little, but it adds rows and noise.
- W5. **Over-long threads.** The coordinator runs on Opus, with 1562 messages in 6 h and one compaction. Most of its turns relay status. live-read went "well past" the 15-turn cap because of ship retries. The red gate (W1) is the main driver of the extra turns.

### Accuracy
- A1. **A false "shipped" claim was relayed to the operator.** live-read (local_528d979d) said "The extract is on fast-track", and the coordinator told the operator "the summary is on the shared branch". In fact `git merge-base --is-ancestor afaf3dae origin/fast-track` gives NOT_ANCESTOR, and `git cherry` gives "+". Only the claim file is on origin. The pushed merge db5c31ae is afaf3dae's parent, not its child. LESSONS_DIGEST s1 already says "is it merged uses `git cherry`".
- A2. **The live-read engine has two field defects that are not fixed yet.** `state_code.json` session_cvd is 370-400 BTC off the 1m archive. `session.vwap_anchor_utc` reads 13:30Z, but the value fits a 00:00Z anchor (live-read report; card `audit-state-code-cvd-and-vwap-anchor`, still raw). Every live read, and every FAB-* setup that uses session CVD or VWAP, inherits them.
- A3. **Fabio's "holdout FAIL" is a mislabel.** LAYERS.md:60 says "v3 tried 2026-10-04, holdout FAIL". But P2_FABIO_V3_HOLDOUT_STATUS.md (the B147 correction) says the 2026-06-26.. holdout was NOT read for Fabio v3: the FAIL is model C's OOS read, and A, B and D were not evaluable. The holdout is burned for Tom (read twice), not for Fabio. This settles plan item 5, and it matters for the A7 holdout decision.
- A4. **Spot-checks that passed:**
  - SETUP_CATALOG.md: `verify_extract_quotes.py` PASS, 0 problems; TOM-1..16 and FAB-1..8 are present.
  - Malkan SETUP_SUMMARY.md: PASS. The 7-star rule is now in his words (SETUP_SUMMARY.md:538), with no chartink source.
  - gpt-cards: T2/T3 are on astra-low (tasks.py:49-50, per the coordinator's grep).
  - The catalogue labels 26 OURS and 74 NOT STATED, so it follows the SOURCED/OURS rule.
- A5. **Reviewers:**
  - The Haiku live review caught real errors (retrace 102% vs 94%, 1m CVD pixel reads, wrong FAB citations).
  - The GPT audits caught real defects before (B144, profile-shape T2 0.500 vs 0.200; TRACK_RECORD.md "Worked"), but none has returned SOUND, and none has touched the new catalogue yet. T2 is that check.
  - No reviewer covers coordinator-to-operator relays (A1).

### Alignment (gates G0-G6)
| Layer | Gate now | Moving? |
|---|---|---|
| Tom | G2: 16 setups, 26 unread videos read (103b65c3), V1 re-extracts (c5457597) | yes, today |
| Fabio | G1-G2: 8 setups; V2 extracts of 7 of 8 raw transcripts (114b74fc). Plan s3 lists 13 staged and 3 long sessions; coverage against that list is not checked | partly |
| Malkan | G1 for 6 videos, 19 setups (a7ac506a) | yes |
| Krown | G1 done (15/15); G2 not in catalogue format | krown-g2 started |
| Any | G3 (blind marks): 0 marks; `tom-btc-eye-read` claim and release in the same minute (43f0ce7f, 6daa1fbc) | **no: the real bottleneck to any G5 number** |

- Drift: NEXT_SESSION.md (the relay queue) still lists Krown Q66-Q69 detectors, code and backtest. LAYER_REBUILD_PLAN s3 says those "wait until G2-G3". The only thing stopping a Sonnet KICK on Q66 is that Q65 sits on the DSA lane.

### Missed (repeat mistakes)
1. "Shipped" or "merged" stated without `git cherry` (A1; LESSONS s1).
2. Missing-input GPT cards issued again (W2; LAYER_LAB.md:55-58).
3. A known red test with no owner for about 13 h (W1).
4. YouTube 429 again: caption-fetch was rate-limited on every request (local_ce8e2fac). LESSONS s6 caps fetches at about 5 per session.
5. Infra share above research (W3), which STATE_OF_PLAY s4 already named.

### New
- N1. **Fee arithmetic favours higher-timeframe setups.** BTC fees force stops of at least 0.40% taker (STATE_OF_PLAY s4), which can sink Tom's small-stop intraday fades. Malkan's weekly/monthly RSI and Krown's daily setups have stops many times wider, so fees are a small fraction of R. They are cheap to test first, but have fewer events: print the MDE line with the gap-g1 helper (f01208e7).
- N2. **Cross-trader agreement as a prior.** A chart event that 2 or more independent traders describe (krown-g2 overlap table) is a better first G3/G5 candidate than a single-trader row.
- N3. **Live reads as a data-quality probe.** Each set found engine defects (A2; earlier 13 mismatches, screenshot_intake.md:11). The MISMATCH count is the cheapest live-path audit we have.

## Recommendations (ranked by expected value per cost; at most 12)
### Do now (today, cheap)
| # | Change | Who | Evidence | Worked when |
|---|---|---|---|---|
| 1 | Finish the gate fix. Then a standing rule: when 2 sessions report the same failing gate test, the coordinator spawns a Sonnet fixer within the hour. | fix-selftest-gate (running); coordinator owns the rule | W1 | No SHIP_FAILED on the same test twice in a day |
| 2 | Ship the stalled lab tree and park missing-input cards; then T2 (catalogue NOT STATED audit) runs before A3. | lab-unstall (running) | W2 | T2's CATALOG_AUDIT.md is on origin before 10-20 |
| 3 | A "shipped" claim quotes an empty `git cherry origin/fast-track <sha>`. The coordinator checks before telling the operator. Add one line to every brief. | coordinator | A1 | Zero corrections to operator reports |
| 4 | Park Q66-Q69 in NEXT_SESSION.md ("PARKED until Krown G2+G3, LAYER_REBUILD_PLAN s3"). Point the relay queue at plan s6 items only. Turn the hourly NOOP dispatcher session off when the T0 gate already says NOOP. | coordinator (one edit + relay handoff); dispatcher schedule by the session that owns 9fe73003 | Drift, W4 | The dispatcher only KICKs plan items; no NOOP sessions |
| 5 | Fix A2 (session_cvd, VWAP anchor): refine the card, then a Sonnet live-path fix with restart/reset tests. Deploy only via AutoDeploy. | Sonnet builder | A2 | The next live read's engine JSON matches the 1m archive on both fields |
| 6 | Paired blind review for live reads (screenshot_intake 4b, this commit). Coordinator briefs say "follow 4b". | live-read sessions | A5 and the operator's ask | REVIEW has a blind section; same-sha ship; WRONG rate tracked |
| 7 | Correct the Fabio holdout label at the LAYERS.md source ("OOS FAIL model C; holdout unread"). Feed this into the A7 decision. | Haiku (one edit) | A3 | LAYERS.md no longer says "holdout FAIL" |
| 8 | **Gate board, the standing mechanism.** make_status.py prints one line per layer: gate now, proof file, hours since it moved, and "non-gate commits 24h: x%". If no gate moved in 24 h, the coordinator's next spawn must target a gate. | Sonnet (T0 script, about 1 h) | W3, Drift | STATUS.md shows the board; the infra share stays under 30% |

### Decide at the 10-20 Fable A3 audit
| # | Question | Evidence | Input A3 needs |
|---|---|---|---|
| 9 | G3 first: which layer and setups get blind marks. Proposed rule: score = BTC-visible Y x stop CLEAR x number of traders who agree (N2). Then build a phone-friendly marking page for the operator plus one blind second reader. | G3 = 0 marks; tom-btc-event-study BLOCKED twice for no marks | the krown-g2 overlap table, T2 audit |
| 10 | First G5 order: higher-timeframe (Malkan, Krown) before intraday Tom, by fee arithmetic, with a power line (N1) | STATE_OF_PLAY s4-s5 | catalogue stop classes, MDE helper |
| 11 | GPT lane after T2/T3: keep it only if T2 finds at least 1 catalogue error that Claude confirms; otherwise end before the 11-11 trial end | TRACK_RECORD | T2/T3 reports, astra-low token cost |
| 12 | Fabio G1 coverage: are the 13 staged and 3 long sessions all extracted? If not, run a targeted extraction from A3's findings, as plan s6 item 7 says | Fabio row above | A3's list of missing concepts |

## Coordinator decisions (2026-10-15, on the operator's behalf) and what the observer did
| Item | Decision | Done in the observer's second commit |
|---|---|---|
| #1 red-gate owner rule | approved | LESSONS_DIGEST s5 (plus: at most 2 ship/gate runs per machine at once); story in LESSONS_LEARNED.md. Gate lock = fix-selftest-gate's call |
| #3 shipped = empty `git cherry` | approved | `tasks.py brief` Close line, relay_session.md step 6, LESSONS_DIGEST s1, screenshot_intake 4b step 3 |
| #4 park Krown Q65-Q69 | approved | NEXT_SESSION.md PARKED block, queue = plan s6 (R1-R4); OPERATOR_DECISIONS.md q-pause-krown-detectors; audit Q2 marked decided. The 3 cards set on hold (`tasks.py apply-op <id> hold`) |
| #4 drop NOOP dispatcher | not now | card `dispatcher-t0-precheck`: measured 50 runs on 10-15 00:18-13:07Z, all 15-26 s NOOP; scheduled task not edited |
| #5 / #8 gate board | approved | `make_status.py` "## Gate Board" from `system/gate_board.json` + 4 tests in test_make_status.py |
| #7 Fabio holdout label | approved | layer_index.json -> LAYERS.md: "OOS FAIL (model C); holdout NOT read for Fabio" |
| G3 | coordinator starts it after fix-selftest-gate and lab-unstall | brief below |

## G3 brief (REVISED 2026-10-16, CATALOGUE_AUDIT P3/P4/P6 and decisions D1, D3, D4; the 2026-10-15 text is replaced)
Goal: the first G3 marks. Two blind readers mark the setups on BTC charts. G4 recall needs these marks; nothing else unblocks G5.
- Definitions first: research/layer_rebuild_2026-10-15/READER_PROTOCOL.md (session anchor 00:00 UTC, balance, P/b/D by closes, thin top, big trade, healthy trend, timeframe per row). OURS, fixed before G3, never varied during it.
- Rows (D4): start with the rows marked YES in audit 4.3: TOM-4, TOM-6, TOM-12, TOM-15, FAB-1, FAB-4, FAB-5, plus Krown KR-S1, KR-S8 and Malkan MAL-2/5, MAL-16/17 (P6 order: clear stops, daily/weekly bars). MAL-5 is MAL-2's order mechanic and MAL-16/17 are the two sides of one divergence: one mark each (D3). TOM-1a and TOM-2 follow after the protocol is on origin. G3 marks the event only; the stop stays OURS for G5.
- Windows (replaces "30 windows per row with a random right edge"): per row 20 windows, half random (the false-positive floor), half candidate-enriched from a cheap causal pre-filter that is written down in g3_pack.py (OURS, logged, selection only, never an entry rule). Rare events (the screen's flow flag fired 40 times in 912 DEV days) make random edges give a yes-rate near zero and an undefined kappa. The two halves are reported separately; a row whose enriched half has fewer than 5 YES marks from both readers is extended by 20 more windows from the same generator with a new seed suffix (logged; not built yet, `pick` takes the seed as a parameter) before it is judged.
- Charts: BTCUSDT DEV only, no bar after the right edge, dates hidden, price axis in % from the last close, only the panels the protocol names per row. Footprint rows (Tom/Fabio, 15m/30m/5m) use F:/MTS/data/orderflow_1m, 2024-12-02..2025-03-31 (the Tom footprint track's DEV, per task brief; it lies inside the standard VALIDATION dates and is logged as such in EXPOSURE_LEDGER.csv). Daily/weekly rows (Krown, Malkan) use daily klines 2021-03-01..2024-06-30 (standard DEV, before 2024-07-01).
- Readers: (1) the operator, one window per screen: TAKE / SKIP, side, tap on the trigger bar (offset), stop % and target %. (2) A blind Sonnet subagent that sees the same PNG, the protocol and the row's catalogue text only, never reader 1's marks and never the answer key.
- Answer key: ANSWER_KEY_CLOSED/KEY.csv (half, pre-filter tag, dates) stays closed until both marking sheets are committed; its sha256 is recorded in g3_marks_2026-10-16/README.md. Window ids carry no hint of the half.
- Output: `research/g3_marks_2026-10-16/` holding WINDOWS.csv (ids, rows, right edges, seeds), MARKING_SHEET_reader1_operator.csv and MARKING_SHEET_reader2_claude.csv (one row per window), the key, and later G3_REPORT.md: per row and per half, the yes-rate per reader and agreement (Cohen kappa; undefined kappa is reported as undefined, never as 0). A row with kappa < 0.4 goes back to G2 with the disagreeing windows listed. PNGs are rebuilt from WINDOWS.csv (`g3_pack.py draw`) and not committed.
- Done when: both readers have marked every window of the first batch; G3_REPORT.md is on origin (`git cherry` empty); `gate_board.json` moves each layer whose rows passed to G3, with proof G3_REPORT.md, in the same commit.
- Not in scope: encoding, event studies, any row not listed above.

## GPT (NUC Codex lab) and NUC-only queue (coordinator task, 2026-10-15 14:30Z)
Rules: GPT only for high-value work, gpt-6-astra at low effort only (a card needs `crucial` for astra: tasks.codex_setting); the lab
allows 1 astra run per 5-hour window (codex_run.py ASTRA_RUNS_PER_WINDOW), so about 4 cards a day. No layer is past G2, so no G4/G5
build or event study is gate-ready (plan s2: no layer skips a gate). GPT work now = second-model-family audits that guard G2 and G3.

| order | card | why it is worth an astra run |
|---|---|---|
| 1 | gpt-catalog-notstated-audit (gpt-cards; asked to add TOM-4 + FAB-8 and prio 1) | the rows G3 spends 210 blind marks on; a wrong row wastes the operator's marks and carries into G4 |
| 2 | gpt-formulas-rederive (gpt-cards) | every fee-net G5 verdict rests on FORMULAS.md 7/12/13/17; an independent re-derivation before G5 |
| 3 | malkan-hindi-rows-gpt-read (new) | 7 Malkan rows and the 5-star/7-star rule exist only as YouTube machine translation; Malkan G2 needs his words |
| 4 | krown-catalogue-gpt-audit (new) | Krown G2 catalogue (krown-g2, f4a5182a) checked by another model family before its G3 marks |

Parked (hold, note on card): gap-g4-through-ticks-flag (old DAX tom_bt flag, mechanical; ran 14:03Z luna/medium, BLOCKED),
gap-g6-trial-ledger (mechanical; reopen on SONNET at the first G5), tom-btc-event-study (gpt-cards: G5 before Tom G3/G4).
Next when Tom reaches G3: point-in-time-factor-design (raw, audit) for G4.

NUC-only: tom-btc-data-check done by the observer through the gate (`ps`, read only): F:\MTS\data\orderflow_1m holds 211 of 212
days of 2024-12-01..2025-06-30 (missing 2024-12-01). JIS-NB holds orderflow_1m and tom_raw too, so G3 chart windows render on JIS-NB.
DSA-NUC: rv-dsa-ledger-mechanical stays ready (Tom ledger feeds the catalogue's real-trade column); rv-dsa-q33-rerun (parked
guidance layer, heavy fetch) and rv-dsa-test-sweep (every ship runs these tests) held. Heavy NUC runs (tom-btc-dev-backtest,
lc-validation, Tom/Fabio G5) start only when a layer reaches G4.

## How to tell the whole thing is working (daily, about 5 min, Haiku)
Read the gate board line in STATUS.md, the SHIP_FAILED count (`git log --grep SHIP_FAILED --since=1.day`) and the shots line. The day is on track if one gate moved, there were 0 repeated ship failures, and no operator report needed correcting. If not, the coordinator gets one line naming the stuck gate.
