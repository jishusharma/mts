# B139 - CBP adapter: register, run on the real queue, backtest analyst rules

Status: OPEN. Severity: MED. Opened 2026-10-06.
Session: MTS-2026-10-06-2122Z-APP-COO-registry-fix. Source: CLOUD_INBOX note 2026-10-06 14:50 UTC (CLD-BLD-cbp-trade-inputs).

## What exists

- MyTradingSys/queue/cbp_adapter.py, cbp_contract_v1.schema.json, tests/test_cbp_adapter.py (c12990d).
- CBP stays a separate producer (BUGS B112, 2026-09-30). Candidates are CANDIDATE_UNTESTED, order_eligible false.

## Run 2026-10-06T21:30Z

`python MyTradingSys/queue/cbp_adapter.py F:\CryptoScrapper\mts_queue`
consumed 0; rejected_expired 0; skipped_acked 1 (handshake_test_2026-09-30);
skipped_status 1 (krown_2026-09-25_OggsnATGbOg, status rejected).
MyTradingSys/queue/candidates/cbp_candidates.jsonl not produced (0 rows).

## Path

Run used F:\CryptoScrapper (consumer.py DEFAULT_QUEUE). Authoritative tree not settled: operator says
F:\CryptoScrapper is correct and CBP was restructured. DSA_SESSION_PROMPT.md section 8 left at F:.

## Done when

A live pending entry yields a candidate row, and each analyst rule has a registered backtest before
any candidate may become order-eligible.

## Run 2026-10-17 (NUC, mts-cbp-integration-land-one-cbp-candida)

Decision (default taken, not asked): authoritative CBP tree = F:\CryptoScrapper (operator 2026-10-14; the tree CBP writes mts_queue to).
consumer.py DEFAULT_QUEUE stays F:\CryptoScrapper\mts_queue and now honours MTS_CBP_QUEUE for hosts whose checkout is elsewhere;
tests/test_cbp_adapter.py::test_default_queue_is_f_tree_and_env_overrides pins both (fails on the old code: no override). Suite: 4 pass (3 existing, not 12).
NUC has no F:\CryptoScrapper; its copy is C:\Users\E-ngineers\IdeaProjects\CryptoScrapper\mts_queue (last commit 2026-09-30).
Run there: consumed 0; rejected_expired 0; skipped_acked 0; skipped_status 1 (krown_2026-09-25_OggsnATGbOg, rejected). No candidate row.
BLOCKED: no pending entry exists in any reachable queue, so the Done-when row is not met. Needs a fresh CBP routine entry with status pending;
then run `python MyTradingSys/queue/cbp_adapter.py` on the F: host. Step 4 (candidate count on STATUS) not done: no candidates yet.

## Receipt

-

# END
