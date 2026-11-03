# S1 sign draft 2026-11-04 (coordinator Unblock MTS, login C)

Three yes/no lines. Silent 4 h after send (sent 2026-11-04 20:30Z) = defaults taken, recorded as d-s1-defaults-1104.

## q-v1-bar: revise GO_LIVE_BAR.md with D3?
Default YES. Add M1-M7, rolling 30-day window (max 1 failed uptime day), time-outs become a per-layer promotion
condition, 200 trades or 60 days with >= 30 per promoted config. Source: `research/v1_plan_2026-10-20/DECISIONS_PROPOSED.md:25-29`,
`D3_GO_LIVE_BAR_REVIEW.md:27-50`. Effect: S2 cards are M1-M4 (state-code backfill, settlement, stop parity, heartbeat).
OPERATOR: yes / no

## q-v1-layers: which two layers hold the S3 slots?
Default: slot 1 LC4 Levels Confluence validation read, slot 2 RSI deep-buy (CryptoCred BLOCKED on power, Tom v2 FAIL,
meta-label FAIL; from the S3 run list `D7_ROADMAP.md:29-48`, d-s3-run-list 10-31). WIP = 2 stays. Original proposal
(`DECISIONS_PROPOSED.md:10-12`) named CryptoCred in slot 2; its DEV run is now BLOCKED, so RSI deep-buy moves up.
OPERATOR: yes / no

## q-v1-spec: sign D2 as the v1 spec?
Default YES as written (`research/v1_plan_2026-10-20/D2_V1_SPEC.md`, 50 lines: one instrument BTC perp, two layers in
flight, CBP as a module, promotion only on fee-net OOS pass with CI > 0, mainnet a separate signed decision).
Until signed the roadmap says S2-S4 do not start (`DECISIONS_PROPOSED.md:36-38`); S0 exit was waived 11-03 so this is the last gate.
OPERATOR: yes / no
