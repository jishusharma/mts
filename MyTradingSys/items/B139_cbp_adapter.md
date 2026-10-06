# B139 - CBP adapter: register, run on the real queue, backtest analyst rules

Status: OPEN. Severity: MED. Opened 2026-10-06.
Session: MTS-2026-10-06-2122Z-APP-COO-registry-fix. Source: CLOUD_INBOX note 2026-10-06 14:50 UTC (CLD-BLD-cbp-trade-inputs).

## What exists

- MyTradingSys/queue/cbp_adapter.py, cbp_contract_v1.schema.json, tests/test_cbp_adapter.py (c12990d).
- CBP stays a separate producer (BUGS B112, 2026-09-30). Candidates are CANDIDATE_UNTESTED, order_eligible false.

## Run 2026-10-06T21:30Z

`python MyTradingSys/queue/cbp_adapter.py C:\Users\E-ngineers\IdeaProjects\CryptoScrapper\mts_queue`
consumed 0; rejected_expired 0; skipped_acked 1 (handshake_test_2026-09-30);
skipped_status 1 (krown_2026-09-25_OggsnATGbOg, status rejected).
MyTradingSys/queue/candidates/cbp_candidates.jsonl not produced (0 rows).

## Path

Run used C:\Users\E-ngineers\IdeaProjects\CryptoScrapper (consumer.py DEFAULT_QUEUE). Authoritative tree not settled: operator says
F:\CryptoScrapper is correct and CBP was restructured. DSA_SESSION_PROMPT.md section 8 left at F:.

## Done when

A live pending entry yields a candidate row, and each analyst rule has a registered backtest before
any candidate may become order-eligible.

## Receipt

-

# END
