# RESULT: Test 2, multi-timeframe context rule, both sides (2026-11-14)

**Verdict (PRIMARY, RSI context, both sides pooled, 20 coins): KILL.** VAL fee-net 12 bp mean R = -0.075 per trade (n=91, block-bootstrap 95% CI -0.269..+0.145), placebo percentile 55 (needs >= 97.5), DEV +0.230 (n=130, CI -0.013..+0.484). Pre-registered as written in `PRE_REG.md` (committed with the code before any outcome); full tables in `RESULT_tables.md`, raw numbers in `RESULT_raw.json`.

| Cell (12 bp fee-net mean R) | n | DEV | VAL (CI) | VAL placebo pct | Verdict |
|---|---|---|---|---|---|
| PRIMARY both sides | 221 | +0.230 | -0.075 (-0.269..+0.145) | 55 | KILL |
| PRIMARY long (UP+BASE) | 69 | +0.278 | -0.413 (-0.654..-0.142), n=32 | 12 | KILL (VAL negative) |
| PRIMARY short (DOWN+BEAR) | 152 | +0.210 | +0.109 (-0.174..+0.405), n=59 | 80 | KILL (CI spans 0, inside band) |
| SEC_WT both sides | 151 | +0.178 | -0.021 (-0.385..+0.459), n=59 | 67 | KILL |
| CONTROL (no context) both | 2673 | +0.121 | -0.058 (-0.179..+0.078), n=1068 | 70 | KILL (descriptive) |

6 bp sensitivity row (PRIMARY both): DEV +0.240, VAL -0.064: same sign, same KILL. RECENT (subset of VAL, report only): PRIMARY both +0.109 (n=40, CI -0.289..+0.509, placebo pct 74); short +0.453 (n=25, CI -0.042..+0.943, pct 89), not used to pick anything.

What the tables say
- DEV looked positive (+0.23 R, pct 89) and did not carry into VAL (-0.08, pct 55). Edge in DEV came from DOWN (+0.85, n=13) and BASE (+0.46, n=11), both tiny; in VAL BASE longs lost (-0.66, n=9).
- The context filter adds nothing measurable: CONTROL without context is the same sign and the same size in VAL (-0.058 vs -0.075), with 12x the trades.
- Long side is the weak half: VAL -0.41 R (CI excludes 0 on the negative side), also without the top coin (-0.55). Short side VAL +0.11 is inside the placebo band (pct 80); BEAR shorts +0.17 VAL (n=43, CI -0.15..+0.48, pct 82), same direction as the earlier BTC +1.03 R hint but about a sixth of the size and not significant.
- One coin cannot carry the pool: VAL both sides, top coin is BTC (sum +3.8 R of 91 trades); with BTC removed VAL is -0.126 (n=84, CI -0.321..+0.080). 7 of 20 coins carry positive VAL sums, 13 negative (BCH, TRX, XRP, QTUM, ETH worst).
- Power: VAL both n=91 (above the 30 floor); long VAL n=32; WT variant long VAL n=15 UNDERPOWERED.

Caveats: one parameter set (OURS phase/pivot/divergence definitions, none tuned); 20 coins still listed on Binance (survivorship); cross-coin correlation only partly handled by the 10-day block bootstrap; spot only, no funding. Data: public Binance klines fetched by `fetch.py` into a local cache outside the repo (no F: drive on this machine); nothing committed. A KILL is a complete answer: do not retune this rule on VAL.

Next: a pooled short-only test is already queued as Test 3 (bear 4H divergence short, 20 coins, funding); the short rows above (BEAR, RECENT +0.39, pct 86) are a lead only, no claim.
