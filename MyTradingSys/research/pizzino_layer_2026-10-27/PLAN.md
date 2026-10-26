# Pizzino layer (Jason + Michael Pizzino): plan, 2026-10-27

Operator order 2026-10-27: a small layer from the two brothers (Jason @JasonPizzinoOfficial, Michael @MichaelPizzino). Their 1-bar / 2-bar / 3-bar indicator, 50% corrections, retests off pivot points. Reuse what CBP already holds.

## What the repo already knows (read this turn)
- Both are T1 CBP analysts, pillar "Multi-asset macro", actionable "partial" (CryptoScrapper cbp_v2/analysts.json). Both are in the actionable-6 profile (research/cbp/CBP_STATUS_2026-10-25.md:7).
- Legacy CBP extracted only macro stances: Jason "overbalance in time and price", levels 87.5k up / 82-83k double-top invalidation (cbp_v2/consensus.md:18, daily_actionable.md:51). Michael was never read line by line (consensus.md:71). Nothing records the 1-2-3 bar method, pivots or retest rules: that is the gap.
- Roadmap already reserves this: "Jason+Michael layer reads cbp.query ... its own card", with targeted extraction (thinker/2026-10-23_cbp_roadmap_opus.md:44,60).
- No existing layer, card or claim names them (checked layer_index.json, LAYERS.md, tasks list, sync.py claims).
- Not known yet, so NOT assumed: the exact definition of the 1/2/3 bar indicator. It comes from their words (step 1), not from memory.

## Rules
- Parameters SOURCED (quote + file:line) or OURS (tuned on DEV, one VALIDATION check, holdout read once, variants in trial ledger). No verdict by doctrine; fee-net out-of-sample numbers decide (CLAUDE.md Hard rules).
- YouTube fetch: Gemini only, laptop and NUC accounts (operator 2026-10-27 widens the 10-25 NUC-only rule). Claude does not fetch captions (HTTP 429).
- Quotes short and verbatim, with video id and timestamp; the repo is public.

## Steps (cards, in order)
1. pz-1a-method-jason and pz-1b-method-michael (two [GEMINI] cards, one per channel, so the laptop Antigravity account and the NUC account each take one; claim is the lock; operator 2026-10-27 allows both accounts): reuse stored transcripts first (CBP store F:/CryptoScrapper on NB/NUC; none are in this repo, checked), fetch only missing videos, latest 30 each. pz-1c-method-merge (Sonnet) joins them.
2. pz-2-layer-spec (Sonnet): SPEC.md, every rule SOURCED or OURS, testable.
3. pz-3-indicators (Sonnet): module (pivots, 50% retracement, retest, 1-2-3 bar count), fail-first tests with hand-computed numbers.
4. pz-4-backtest (Sonnet): BTC DEV/VAL/holdout, fee-net, trial ledger, standalone and as a filter on existing layers.
5. pz-5-confluence-and-live (Sonnet): confluence table against other layers; cbp.query bias/levels as live input, behind B139 gate.
