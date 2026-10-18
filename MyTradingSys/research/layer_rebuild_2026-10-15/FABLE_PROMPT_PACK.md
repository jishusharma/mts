# Fable 5.1 prompt pack (run window: evening of Tue 2026-10-20 IST, before the 01:30 IST Wed reset)

Order (updated 2026-10-15): B (Sonnet, morning of 10-20) -> A3 (Fable, evening; catalogue + rebuild audit) -> gap extraction and eye-read marks. A1/A2/REFRAME/C/D are kept for reference only.
Fable is used once, on the question only it is worth paying for: is the whole project aimed at a real edge?
Everything cheaper (week digest, execution of A's follow-ups) runs on Sonnet/Haiku.

---

## B. Week brief (Sonnet 5.5, ~10 tool turns, morning 2026-10-20) - so Fable does not spend tokens discovering the week

MTS builder session. Boot per CLAUDE.md. One task: write `MyTradingSys/research/fable_audit_2026-10-20/WEEK_BRIEF.md` (max 6 KB), facts only, every line with a commit hash or file path:
1. `get_usage` snapshot (all three meters, UTC time).
2. (origin/fast-track had ~1,650 commits in the last 7 days, mostly claim/release/merge/lane-health noise: write a short script that drops those subjects and buckets the rest by changed-path prefix; do not read commits one by one.) Commits on origin/fast-track in the last 7 days, bucketed by rung: R0 premise/direction, R1 data, R2 simulator/backtest, R3 rule extraction and layer fidelity, R4 statistics (splits, ledgers, holdout), R5 economics/fees/venue, R6 execution/live, R7 process/infra (relay, tokens, CI, hygiene, pages). Give counts and the share per rung; use `git log --name-only`, no judgement beyond the bucket.
3. Every new result number since 2026-10-14 (reports under research/, layer_lab/reports/) in one table: claim, number, file, data split used, fee-net yes/no.
4. Decisions answered and still open (OPERATOR_DECISIONS.md), incl. Q2 (pause Krown Q65-Q69) and A7 (holdout).
5. Contradictions you noticed between two documents (quote both lines, file:line). Do not resolve them.
Do not interpret or recommend. Ship with `sync.py ship`, Result line = the share-per-rung table. Reply in 3 lines.

---

## A1. STEERING AUDIT, RUN NOW (Fable 5.1, effort high; operator decision 2026-10-15: align the coming week first)

Paste everything in this section into a new session. It is the top of the ladder only (R0, R4 on paper, R5, R7), because those rungs decide what the week should work on and need reading and reasoning, not heavy recomputation. R1-R3 and R6 stay for A2 on 10-20.

MTS Fable session. Boot per CLAUDE.md steps 1-2 (sync.py start, STATUS.md). OPERATOR OVERRIDE for this session only: the 15-tool-turn cap is lifted to 25. Write the findings file section by section as you go.

**Usage guard.** `get_usage` first and last into `PILOT_USAGE.md` (all meters, UTC). Weekly all-models is about 21% at the start. Stop, write up and ship if it rises 4 points or reaches 30%, whichever first. Do not read VALIDATION or HOLDOUT data; do not run backtests.

**Question.** Is the work queue for 2026-10-16..20 aimed at the weakest point of the belief that MTS has a fee-net edge? Existing reports (research/layer_lab/reports/2026-10-15_*, research/mts_flow_audit_2026-10-13, research/backtest_gap_review_2026-10-13, tom_btc_2026-10-13/TOM_ON_BTC.md, orderflow_views_2026-10-14/RESULT.md) are claims, not evidence: read the primary files they rest on (study.py, tom_bt.py, the 62-strategy and MFE study results) and re-derive at least one number per rung that you rate.
- R0 Premise: falsifiable statement of what must hold for money to be made; what observation would kill it; could any run so far have produced that observation?
- R4 Statistics (paper check): split discipline, trial ledger completeness, holdout exposure, power. Could the "none survive" results (62 strategies, MFE exits, ETH 0 of 9) have detected a real edge of plausible size? Do a rough power calculation from the numbers in those reports.
- R5 Economics: venue (Binance research, Deribit execution check), fees, size, slippage, decay after latency. Is there any realistic regime where a minute-scale flow signal clears costs? Name the minimum gross effect that would be needed.
- R7 Process: bucket the last 7 days of commits by rung (R1 data .. R7 infra) and the open queue (NEXT_SESSION.md, tasks.py next, Codex lab queue) by which rung each item serves. State the effort share versus where the risk is.

**Deliverable** `MyTradingSys/research/fable_audit_2026-10-15/STEERING_AUDIT.md`:
1. Verdict paragraph and the weakest rung.
2. Rung table (rung, verdict SOUND/DOUBTFUL/BROKEN/UNTESTED, RE-DERIVED/READ/TRUSTED, reason, file:line).
3. The queue for 2026-10-16..20: which items to PAUSE (with the reason), which to RUN, what to ADD (at most 3 new cards, each runnable mechanically by Sonnet/Codex/DSA). Mark where it agrees or disagrees with the 10-15 claude-side audit's road forward, and with the operator's open Q2 (pause Krown Q65-Q69).
4. What A2 (the 10-20 evening Fable run) must cover: the rungs not done here, plus what the week's results should be checked against.
5. Operator decisions needed (max 5, each with a default).
Do not edit the task queue yourself: propose; the operator confirms. Ship with `sync.py ship`, Result line = verdict + weakest rung + usage delta. Reply in 6 lines.

---

## A2. Bottom-up direction audit (Fable 5.1, effort high, ONE session, evening 2026-10-20). A1 was HELD by the operator, so there is no STEERING_AUDIT.md: ignore any mention of it and cover ALL rungs R0-R7 below. Start from WEEK_BRIEF.md. The text below is the complete prompt.

MTS Fable session. Boot per CLAUDE.md steps 1-2 only, then read `fable_audit_2026-10-20/WEEK_BRIEF.md`.
OPERATOR OVERRIDE for this session only: the 15-tool-turn cap is lifted to 40. Do not hand over mid-way; write the findings file as you go (section by section) so nothing is lost if you stop.

**Usage guard.** Call `get_usage` first and last, record both in `PILOT_USAGE.md` (all three meters, UTC). Stop, write up what you have and ship if the all-models weekly meter rises 6 points or reaches 95%, whichever first.

**The question.** Is MTS pointed at a real, fee-net edge, and where is the ground under that belief weakest? Not "how good is the work" and not another opinion on strategy: today's audits (research/layer_lab/reports/2026-10-15_*, research/mts_flow_audit_2026-10-13, research/backtest_gap_review_2026-10-13) already hold opinions. Treat every existing report as a CLAIM, not evidence. Your job is independent re-derivation from code and data wherever a conclusion depends on it.

**Method: an evidence ladder, bottom up.** For each rung give a verdict SOUND / DOUBTFUL / BROKEN / UNTESTED, and say how you know: RE-DERIVED (you recomputed it), READ (you read the code/data), or TRUSTED (only a report says so). At least one re-derivation per rung R1-R5, small and cheap (one number, one function, one sample). No HOLDOUT reads; no VALIDATION reads.
- R0 Premise: state in falsifiable form what must be true for MTS to make money (operator belief: order flow is real, Tom's rules work). What observation would kill it? Has any run been able to produce that observation?
- R1 Data: tape and klines correct, timestamps, gaps, venue (Binance research vs Deribit execution).
- R2 Simulator: fills, fees, gap and stop booking, look-ahead. Recompute 3 numbers independently from `backtest/layers/FORMULAS.md`, never from existing code.
- R3 Rule fidelity: do coded layers equal what the trader actually said? Sample 5 rules: quote at source vs code.
- R4 Statistics: split discipline, trial ledger completeness, holdout exposure (incl. the 2026-06-26 contamination), multiple-comparison handling, power. Would the 62-strategy "none survive" result have detected a real edge of plausible size?
- R5 Economics: instrument, size, fees, slippage, decay after latency, benchmark. Is there any size/venue where a flow signal of this kind can clear costs?
- R6 Execution/live: testnet vs real venue liquidity, PnL accounting (L6/B149), fail-closed checks. Short: is it premature to polish this before R0-R5 pass?
- R7 Process: from the week brief, what share of effort sat on which rung vs where the risk is. Is the queue (Krown chain, relay, token work, labs) aimed at R0?

**Deliverable** `MyTradingSys/research/fable_audit_2026-10-20/DIRECTION_AUDIT.md`:
1. One-paragraph verdict: continue / redirect / stop-and-reframe, with the weakest rung named.
2. Ladder table (rung, verdict, how known, one-line reason, file:line evidence).
3. At most 7 corrections, ranked by (risk removed per effort), each: what, who runs it (Sonnet / Codex lab / DSA / operator), cost S/M/L, and the observation that would prove you wrong.
4. Kill/pause list: work to stop now.
5. The single next experiment, specified well enough that a Sonnet card can run it mechanically (this absorbs the gross-effect PRE_REG: either specify it here or say why another test comes first).
6. Operator decisions needed (max 5, each with your default).
Disagree with earlier audits where you find a reason, and say which. Do not pad. Ship with `sync.py ship`, Result line = verdict + weakest rung + usage delta. Reply in 6 lines.

---

## C. Gross-effect screen pre-registration (fallback or follow-up; Opus/Sonnet is enough)
Use the content of `fable-pilot-prompt.md` (saved in memory) unchanged. Run it on Fable only if A leaves spare quota and says this test is the next experiment; otherwise run it on Opus.

## D. Live-path / mainnet-readiness review (Fable, only if A says R0-R5 are SOUND)
Scope: L6/B149 PnL source (settlement and funding excluded, session UPL reset 08:00 UTC), restart/reset state, non-trade balance moves, API errors, fail-closed checks, per CLAUDE.md live-path rules. Do not run before a candidate edge exists: polishing execution of a strategy with no edge is the wrong order.

---

## A3. CATALOGUE + REBUILD AUDIT (Fable 5.1, effort high, evening 2026-10-20). SUPERSEDES A2 and REFRAME (operator 2026-10-15: build every layer from the ground up, setups first, keep existing work).

MTS Fable session. Boot per CLAUDE.md steps 1-2 only. OPERATOR OVERRIDE for this session only: the 15-tool-turn cap is lifted to 40. Write the findings file section by section as you go.

**Usage guard.** `get_usage` first and last into `PILOT_USAGE.md` (all meters, UTC). Stop, write up and ship if all-models weekly rises 6 points or reaches 95%.

**Read first:** `MyTradingSys/research/layer_rebuild_2026-10-15/LAYER_REBUILD_PLAN_2026-10-15.md` (gate order G0-G6, per-layer state), `MyTradingSys/research/setup_catalog_2026-10-15/SETUP_CATALOG.md` (Tom + Fabio setups), `WEEK_BRIEF.md` if it exists. All are claims to check, not evidence.

**The question.** Is the setup catalogue a faithful and complete record of what the traders actually do, and is the rebuild plan the right order? No backtests, no fees, no VALIDATION or HOLDOUT reads.
1. Fidelity: sample at least 8 catalogue rows (Tom and Fabio, include family A and one Fabio row). Open the raw transcript at the cited line: does the quote say what the row claims? Is anything in the row OURS presented as his?
2. Completeness: read at least 3 Tom transcripts listed as never extracted and 2 Fabio sources listed as unread. Name every setup or rule there that the catalogue lacks.
3. Merges: are any two rows one setup, or one row two setups?
4. Chart-visibility: for each row, can a person mark it on a BTC chart without hindsight? Which rows cannot be marked as written, and what is missing?
5. Plan: attack the gate order and the per-layer next steps (Krown, Malkan included). Is anything in the plan wrong, missing, or in the wrong order? Which existing work does the plan discard that it should keep?

**Deliverable** `MyTradingSys/research/fable_audit_2026-10-20/CATALOGUE_AUDIT.md`:
1. Verdict paragraph: catalogue usable for eye-read marking yes/no, with the main defect.
2. Fidelity table (row, quote checked, verdict OK/WRONG/OVERSTATED, source file:line).
3. Missing setups found (quote + source).
4. Rows to merge/split; rows not markable and why.
5. Plan corrections (at most 7, each: what, who runs it Sonnet/Codex/DSA/operator, cost S/M/L).
6. Operator decisions needed (max 5, each with a default).
Ship with `sync.py ship`, Result line = verdict + count of wrong rows + count of missing setups + usage delta. Reply in 6 lines.

---

## REFRAME (2026-10-15, after the operator asked "what is a real edge, are Tom/Fabio even in the code?")
Give the Fable session `MyTradingSys/research/layer_rebuild_2026-10-15/STATE_OF_PLAY_2026-10-15.md` (copy: memory `state-of-play-2026-10-15`) in addition to the week brief. Its job is not a neutral ladder tour: settle the three questions in that brief (Q1 fidelity, Q2 their edge, Q3 gross effect of order flow on BTC after costs), attack the brief's hypothesis that Q3 is testable first and Tom-independent, verify R2/R3/R4 on the points it rests on, and output the ordered plan plus the one pre-registered experiment. Cap 25 tool turns.
