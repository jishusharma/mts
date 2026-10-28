# Layer rebuild plan, 2026-10-15 (ground up, keeping existing work)

Operator goal (2026-10-15): rebuild every layer from the ground up, look at every issue met so far, start fresh where that is easier, never lose existing work.
Inputs: two read-only inventories of the disk (2026-10-15; file:line in each section) and STATE_OF_PLAY_2026-10-15.md. Claims are second-hand unless marked; Fable checks them on 10-20.
Corrections applied 2026-10-16 from fable_audit_2026-10-16/CATALOGUE_AUDIT.md section 5: P3 (s5 rule 2, READER_PROTOCOL.md), P4 (G3 window design, OBSERVER_REPORT G3 brief), P5 (s3 Tom, exposure ledger), P7 (s2 G5, s3 Tom/Fabio, s6 order); the gate-board part of P6 (Malkan at G2). P1 and P2 (catalogue fixes, caption conversion) run in other sessions.

## 1. Why the work drifted (the root cause, one line)
Every layer jumped from extraction straight to code and backtests, with our own numbers filling the gaps, before anyone wrote down the trader's bare setups or checked them on a BTC chart. The NO-EDGE verdicts therefore test our encodings, not the traders (Tom: 0 of 7 real entries matched; Malkan: single timeframe, no 5-star gate, his exit never tested).

## 2. One gate order for every layer (no layer skips a gate)
| Gate | Done when |
|---|---|
| G0 Sources | everything the operator asked for is on disk, or listed as unobtainable with the reason |
| G1 Extraction | every source extracted with verbatim quotes that pass `verify_extract_quotes.py` |
| G2 Setup catalogue | one row per setup: what you SEE on the chart, entry / stop / target in his words (NOT STATED where silent), quote + source, BTC-visible Y/P/N, his real trades that match |
| G3 Eye-read marks | two readers (operator + one) mark the setup on BTC charts, blind to what came next; terms as defined in READER_PROTOCOL.md; windows half random, half drawn from a written-down cheap pre-filter, the two halves reported separately (OBSERVER_REPORT G3 brief) |
| G4 Encode + fidelity | code written FROM the catalogue fires where the marks are (recall vs random-clock baseline) |
| G5 DEV event study | fee-net, against the same location without the flow (control), stops from G2. Template: the orderflow_views_2026-10-14 negative result and the gross_effect_screen_2026-10-15 control design (arm C = location without flow) |
| G6 VALIDATION once, HOLDOUT sealed (A7) | |

Fees and stop sizes enter only at G5. Rows marked OURS stay variants and never decide a verdict.

## 3. Per layer: where it stands, what to keep, what to fix, what starts fresh
### Tom (gate G1-G2)
- Keep: TOM_LAYER_V2_SPEC family A (the model row) and its A-C / A-P tables (kept as the OURS variant list for G5, never as his rules), TOM_TRADE_LEDGER (37 rows), TOM_ON_BTC concept inventory, chart lab (105 candidates, 80 charts; the candidates are a ready cheap pre-filter for the G3 enriched windows), DAX lessons.
- First G5 lesson (gross-effect screen, 2026-10-15, INCONCLUSIVE): read it as a rate estimate, not as a verdict on TOM-1. Its location rule L (00:00 UTC anchor, top-quintile leg, new session extreme in 3 bars) is OURS; the control arm (n = 1,439, mean -0.008 %, t_cost -6.0) says that plain rule has no gross edge at 1m / 60 min, so G5 for TOM-1a must not reuse L; the T arm (n = 40 in 912 DEV days, MDE 0.365 %) says the flow-at-extreme event is rare, which sets the G3 sample design (half enriched windows). The 1m / 60 min horizon is our choice, not his (he holds "to the start of the impulse"). Q66-Q69 and Tom T5 stay parked as the PRE_REG says.
- Fix: 26 of 84 transcripts never extracted, 47 V1 only, 32 V1 extracts fail the quote check (transcript_inventory_2026-10-09.md:15,21). Merge the NEVER/WRONG list (TOM_ON_BTC.md:38-109) and the screenshot gaps G2-G7 (research/screenshots/2026-10-12_BTCUSDT_set_5b0e17d24d71.md:79-87, 2026-10-14_BTCUSDT_6b27526d76bd.md:13-18) into the catalogue as "missed concepts".
- Fresh: the BTC encoding (LAYERS.md:13 STOP). Old code stays for reference, not patched.
- Now: catalogue session (running) -> extract the 26 only where the catalogue shows gaps -> G3 eye-read card (ready).

### Fabio (gate G1-G2)
- Keep: FABIO_TRADE_MODEL (best plain description), V3 spec quotes, rulebook, ledger.
- Fix: the "13 staged raw transcripts never extracted" count has no source on disk (CATALOGUE_AUDIT s3.4; the real G1 gap is the 2 caption files on F: without canonical transcripts, plan correction P2); the 2 long sessions without captions (Is1HvdfQm5c, xUyqIjCfZzg) stay "frames only" (D2), not "unread, to extract"; one session read to 250 s (FABIO_TRADE_LEDGER.md:48,90); ledger 8 of 20 trades. Holdout CONFLICT: LAYERS.md:60 says FAIL, P2_FABIO_V3_HOLDOUT_STATUS.md:9 says NOT read. Resolve before anything else claims it.
- Fresh: v3 models A-D as code (formulas without stated thresholds).
- Now: same catalogue session -> extract the staged 13 and unread sessions.

### Krown (gate G2, furthest along on paper)
- Keep: 15/15 extracted, 120 rules, 9 setups S1-S9 (krown_ta101_2026-10-13/STATE.md, KROWN_LAYER_SPEC.md:57-65).
- Fix: 4 transcripts missing (HTTP 429, intermittent: STATE.md:13,27; decision q-krown-captions open); 18 playlist entries hidden by YouTube; daily BTC videos not fetched. Q65 started and lost at the turn cap (NEXT_SESSION.md:2).
- Fresh: nothing; no code exists. Rewrite S1-S9 into the G2 catalogue format (see-on-chart, his stop/target, BTC-visible).
- Now: fetch the 4 captions (retry, spaced); Q66-Q69 detector/backtest cards wait until G2-G3.

### Malkan RSI 40/60, 5-star / 7-star (gate G0-G1)
- Keep: 4 extracts (V1, pass), RSI_2A_SPEC sourced answers, rsi/ code and tests.
- Fix: A-CQiV_UFB4 (the 7-star source, raw_transcripts_canonical/A-CQiV_UFB4_raw.txt:292-294) and W1HrDl70Lhk (5-star, Hindi) are on disk but NOT extracted: this is the extraction that was lost midway. 5 videos blocked by 429, 1 private, 1 members-only, up to 10 Hindi picks never started (transcript_inventory_2026-10-09.md:163-196). The 7-star definition currently comes from a chartink web page, not his words (malkan_rsi_2026-09-28/WEB_RESEARCH.md:171-172).
- The NO-EDGE verdict (MARKET_GUIDE_RESULTS_2026-10-07.md:21) tested one timeframe without the 5-star monthly+weekly gate and without his exit: it does not cover his method.
- Now: extract the 2 on-disk transcripts; fetch the blocked ones; then G2.

### Parked (no work until the four above reach G3)
Qriptal (22 of ~40 transcripts, no call list), CryptoCred and FlowHorse (raw transcripts missing, FAIL), Kurisko (spec only), guidance / session / volume-candle-MA (no source or FAIL).

## 4. Screenshots (operator's live BTC chart reads)
- Finding: all 30 chart shots are the operator's own BTC charts (CoinGlass / TradingView), not Tom's sessions. They found real gaps (section 3 Tom fix list), but these sit in single write-ups and about 8 raw cards; no file merges them.
- Fix: merge into the Tom/Fabio catalogue's "missed concepts" section (catalogue session or its follow-up).
- Bug: the STATUS line counts claims per shot, not per write-up (shot.py:671-674): 437/69/107 shown, about 111/19/27 real.
- 3 pending shots are app screenshots, not charts: close with `noaction:`.

## 5. How we keep it pointed in the right direction
1. LAYERS.md gets one table: layer x gate (G0-G6). A layer moves only when its gate's "done when" holds, with the file as proof.
2. Every catalogue row quotes the trader; gaps say NOT STATED. No OURS *tuned* number before G5; OURS *definitions* needed to mark a row are written once in READER_PROTOCOL.md, labelled OURS, and never varied during G3.
3. Weekly check (start of each week): which gate moved; work that moved no gate (relay, token trimming, pages, hygiene) is named and capped. Operator decision needed: cap infra work while layers sit at G0-G2.
4. Fable on 10-20 audits the catalogue and this plan against raw sources (FABLE_PROMPT_PACK.md A3). Done early on 2026-10-16: fable_audit_2026-10-16/CATALOGUE_AUDIT.md.
5. Every read of DEV data, by eye or by code, gets one line in gross_effect_screen_2026-10-15/EXPOSURE_LEDGER.csv (the G3 chart pack is logged there).

## 6. Work order (each line one short session or one queued job)
1. [running] Tom + Fabio catalogue from existing files.
2. Source fetch job (DSA/Haiku, free public YouTube): Krown 4 captions, Malkan 5 blocked + Hindi picks, retried with spacing.
3. Malkan: extract A-CQiV_UFB4 + W1HrDl70Lhk (V2 format, quote check).
4. Krown: rewrite S1-S9 into catalogue format.
5. Resolve the Fabio holdout conflict (one read of both files and the holdout log).
6. Fable 10-20 evening: catalogue + plan audit (A3).
7. Gap extraction (Tom 26, Fabio 13 + unread sessions) targeted by Fable's findings.
8. G3 eye-read marks: operator + second reader, per layer. Order (D4, P6): the rows markable as written first (TOM-4, TOM-6, TOM-12, TOM-15, FAB-1, FAB-4, FAB-5) together with Krown KR-S1, KR-S8 and Malkan MAL-2/5, MAL-16/17 (clear stops, daily/weekly bars, where a weekly stop dwarfs fees); G3 and G5 for Krown/Malkan run in parallel with Tom's catalogue fixes, not after them. TOM-1a and TOM-2 join once READER_PROTOCOL.md is on origin. Pack: g3_marks_2026-10-16/.
