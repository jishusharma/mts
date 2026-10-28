# Lab_Guy spec detail for card indicator-values-multi-model-audit (2026-10-18, labguy-pass-b)

Full text of the items the card shortens (card item limit 400 chars). The card is the contract; this file is the detail.

## steps item 1

READ-ONLY on definitions: FORMULAS.md s1 (Wilder RSI), s22 (Bollinger, added 2026-10-17) and s23 (Stochastic RSI) already hold the canonical definitions with worked examples; do NOT add or edit a FORMULAS.md entry here. Sample only indicators that have an entry; an engine indicator without one is filed with tasks.py new (a definition entry is its own C2 card)

## steps item 2

script scripts/dev/indicator_audit_sample.py (new): seeded draw (seed OURS, recorded) of about 20 values, at least 6 each for RSI, Bollinger and StochRSI over at least 2 timeframes, from live snapshots/alerts; one packet per value = the full closes window the engine used (at least 500 closes; truncating Wilder's seed costs below 1e-9 at 500 bars) + the FORMULAS.md definition text + the question, never our value, never engine code; hash each packet window (sha256 into the AUDIT.md table); packets hold market data only, no balance, order or account fields (repo is public)

## steps item 3

state the tolerance BEFORE any reviewer replies (OURS): RSI/StochRSI K and D absolute 0.01 points; Bollinger mid/upper/lower relative 1e-6 (population sd, s22). scripts/dev/indicator_audit_compare.py (new) compares in code, never by asking a model

## steps item 4

Haiku and Sonnet Agents recompute each packet blind (packet only, no repo access); a mismatch above tolerance is triaged: reviewer error or definition ambiguity vs engine bug; a B-item only for an engine bug confirmed by a hand calculation

## steps item 5

lab side: post ONE desk row per external reviewer to the NUC with desk.py post --target DSA (GPT packet run, DSA run); never run GPT/Gemini here. Their columns stay PENDING(desk row id) until answered

## steps item 6

AUDIT.md: table value x reviewer, seed, tolerance, packets, B-items, and the stated limit: 20 clean values bound the engine mismatch rate only to about 14 percent at 95 percent (rule of three, 3/20), so a clean table is MACHINE-OK, not VERIFIED, until at least one non-Claude column is filled and matches

## tests

test_indicator_audit.py (new, scripts/dev/): sampler output is identical for the same seed and differs for another; comparator catches planted wrong values (Bollinger with sample sd n-1 is 2.6 percent wider at n=20: hand value for closes [10,12,14,12] n=4 mult=2 upper 14.828427 vs 15.265986; RSI off by 0.5); both fail before the scripts exist. Expected numbers are hand-computed from FORMULAS.md worked examples, not from the scripts

## done_when

research/indicator_audit_2026-10-14/AUDIT.md with: seed, tolerance (OURS, written before the replies), sample count by indicator x timeframe (about 20, at least 6 each RSI/BB/StochRSI), table value x reviewer with Haiku and Sonnet filled and GPT/DSA = PENDING(desk row id) or filled, a triage line per mismatch above tolerance, a B-item per confirmed engine bug, the 14 percent limit sentence, trust tag MACHINE-OK (VERIFIED-C1 only after a non-Claude column matches); both tests pass. Verify: content commit sha, git cherry origin/fast-track <sha> empty, git ls-tree shows the files.
