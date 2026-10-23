# D5. CBP as a module of MTS

Today: CryptoScrapper (F:/CryptoScrapper, own repo) fetches YouTube transcripts of listed analysts, extracts positions with
an LLM, writes consensus.md, daily_actionable.md and analyst_feed.json, and offers alerts through mts_queue/
(pending.json, consumed.json, schema.json, acks/). MTS reads it with queue/consumer.py (acks only, never orders) and
cbp_adapter.py against cbp_contract_v1.schema.json. Item B139 ran twice (2026-10-06, 2026-10-17) and consumed 0:
pending.json last changed 2026-09-30 and holds a rejected krown entry and a consumed handshake. A Claude scheduled task
cbp-daily-workflow (Haiku, 3x per day since 2026-10-15, cbp_v2/PIPELINE.md) runs the pipeline; PIPELINE.md Q3 says MTS
does not read the queue, contract only. So CBP produces, nothing consumes, and the producer runs on a schedule the MTS policy
forbids. The module boundary fixes all three.

## What MTS controls
1. Schedule: the CBP pipeline runs when the MTS coordinator runs it (or as the one named exception in q-v1-cbp-routine).
   No run outside the MTS dispatcher.
2. Config: analysts.json (who is tracked), the extraction prompt version, the schema version. A change to any of them is an
   MTS card and ships through the MTS gate, even though the files live in the CBP repo.
3. The contract: cbp_contract_v1.schema.json is owned by MTS. CBP conforms to it; MTS bumps it.
4. The consumer: MTS decides when to consume, writes the ack, and is the only writer of order_eligible.
5. The stop: a CBP row never reaches the trader unless a per-analyst backtest is registered (B139 CANDIDATE_UNTESTED rule).

## What CBP guarantees (the producer's side of the contract)
- Every row validates against the schema before it is written to pending.json (schema gate on the producer; today the
  check lives only on the consumer).
- Every extracted claim carries a verifiable quote: verify_extract_quotes.py passes on the extraction before a row is
  emitted (the MTS extraction gate, applied inside CBP).
- expires_at set on every row; stop_loss may be null (contract README); order_eligible is always false from CBP.
- source ids (video id, timestamp) on every row, so the analyst scorecard can score it later.
- Write scope: CBP writes inside mts_queue/ and, as the one named exception (DECISION, OURS), to
  raw_transcripts_canonical/ through the MTS fetcher (fetch_captions_timed), so the adapter and the quote gate read one
  transcript store. No other MTS path, no other MTS write. CBP sha at amendment: 152726bec1208c27115a4042d52d6c741699ff2a.
- Idempotent: the same video never produces two rows (dedupe on video id + analyst).

## How bad output is stopped before trading (five gates, in order)
| Gate | Where | Stops |
|---|---|---|
| 1 Schema | producer, then consumer again | malformed, missing fields, wrong types |
| 2 Quote | verify_extract_quotes.py in CBP | hallucinated claims (no quote in the transcript) |
| 3 Freshness | consumer: expires_at and transcript age | stale calls |
| 4 Scorecard | analysts/SCORECARD.md: 56 scored calls per analyst before any weight | analysts whose calls do not pay |
| 5 Promotion | B139: CANDIDATE_UNTESTED until a pre-registered backtest passes VALIDATION; the auto-trader reads only promoted_setups.json | untested ideas trading |

Nothing CBP emits can trade until gate 5, which is the same gate every layer faces (D2 module contract).

## Evaluation harness (the part that makes the module trustworthy)
A golden set in the CBP repo: 10-20 transcripts with the expected extraction written by hand, plus the known failure cases
(the 2026-10-18 analyst_feed rows, the rejected krown row). pytest runs extraction against the set on every prompt or model
change and fails on: a claim without a quote, a wrong direction, a missing expires_at, a duplicate row. This is also the
operator's portfolio piece 1b (teach-me-the-songs NOTES.md). Measure first: the harness runs on the cheapest model that
passes the set; a bigger model is used only when the set shows it is needed.

## Repo placement
CBP stays a separate repo (its own cookies, yt-dlp, transcripts). Governance is MTS: cards live in MTS, the schema lives in
MTS, the run is dispatched by MTS. A CBP change ships as two commits (CBP repo, then the MTS card closing commit that names
the CBP sha).

## Stage
S4 in D7. Entry: contract v1 promoted to the one Signal schema, scheduled task decided. Exit: one real analyst row flows
producer -> queue -> consumer -> CANDIDATE_UNTESTED with an ack, and the golden-set harness is green on CI.

## Status table (amended 2026-10-23; CBP sha 152726bec1208c27115a4042d52d6c741699ff2a)
Placeholders: agent V (independent verify) fills MET / PARTIAL / NOT MET with pasted command output. Until then PENDING.
| Item | Status | Evidence |
|---|---|---|
| Gate 1 Schema (producer side) | PENDING | |
| Gate 2 Quote (single checker in MTS) | PENDING | |
| Gate 3 Freshness (consumer) | PENDING | |
| Gate 4 Scorecard (56 scored calls) | PENDING | |
| Gate 5 Promotion (CANDIDATE_UNTESTED) | PENDING | |
| Golden-set harness green on CI | PENDING | |
| S4 exit: one real row producer -> queue -> consumer -> ack | PENDING | |
