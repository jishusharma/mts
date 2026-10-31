# Fractals + BTC phase context: synthesis of reviews R1-R4 (2026-10-31, Lead, desktop login C)

Inputs: `reviews/R1_LITERATURE_TECHNIQUES.md`, `reviews/R2_BTC_PHASES.md`, `reviews/R3_JALA_FRACTALS.md`, `reviews/R4_MULTI_LLM_PLAN.md`.
Status: VALIDATED WITH FIXES by Fable (`VALIDATION.md`); all 18 fixes from its section 3 applied here. No code built, no backtest run.

## 1. Verdict
- No published study shows a fractal method earning fee-net, out of sample, on BTC (R1 s1-4). Hudson and Urquhart (Ann. Oper. Res. 297, 2021): almost 15,000 technical rules on BTC/ETH/LTC/XRP; profitable after data-snooping controls except BTC out of sample, where predictability does not hold (R1 s3; abstract confirmed via indexes, full text not read).
- So a fractal layer starts as **context** (a tag that splits results of layers we already have), never a trigger, until our own DEV test says otherwise.
- BTC phase context is the same kind of object and is built first: it serves every layer, and the structural-break gap R02 in `T10_missing_aspects.md` is open.

## 2. What the operator asked, answered
| Ask | Answer |
|---|---|
| Deep research status | Card `opus-fractals-btc-deep-research-1031` never started on login A; reviews R1-R4 done on login C 2026-10-31, Fable-validated |
| Jala's way of choosing fractals | Unknown from data: 3 fractal quotes, no selection rule (R3 s1). Card `gemini-jala-fractal-method` extracts it from captions |
| Jala keeps the 4-year cycle in mind? | One quote says yes (p9KajODtBsU: 'every four years we get this three'); he times it off the cycle low and uses STH NUPL turning yellow as his own confirmation; no halving reference in any quote; 18 of 30 videos unread, coverage partial (R3 s2-3) |
| All LLMs detect fractals | Only behind gates: coded detector is ground truth; LLM labels must reach kappa >= 0.60 and add fee-net lift on DEV (R4) |
| Phases inside phases, Cowen | 4-level taxonomy, 25 rows (R2 s1); macro phases have 2-3 instances, so they are display/context only, not tested as edge |

## 3. Point-in-time rules (all phase and fractal work)
- Never align on a peak or bottom date: unknown at the time. Allowed anchors: halving dates, running ATH, running drawdown, completed weekly/daily bars (R1 s5).
- The tag or gate value used at bar t is computed from bars closing at or before t-1; every step's shift test asserts this.
- Halving date = block 840,000 timestamp 2024-04-20 00:09 UTC (FORMULAS.md entry); day counts from it (peak close 2025-10-06 = day 534).
- Matches must beat random paths with BTC's volatility, not zero (R1 s5).
- Every parameter labelled SOURCED (link/quote) or OURS; FORMULAS.md entries for halving clock, Hurst/DFA, DTW written first (R1 Noticed).

## 4. Build order
P0 -> P1 -> F1 -> L1 gated in order; F2, F3, J1 may run in parallel after P0.

| Step | What | Data | Gate to go on | Lane |
|---|---|---|---|---|
| P-1 | Power and planted-edge harness: for each step, the n at which a 0.10% effect is detected at 80% power; synthetic edge injection and removal | synthetic on DEV event lists | harness detects the planted cell and only it | Sonnet Builder |
| P0 | Phase tag v1: days since halving, drawdown from running ATH, side of Cowen band (20W SMA/21W EMA, completed weeks), side of 200D and 400D SMA, weekly SMA10 phase | F:/MTS/data/krown_daily/BTCUSDT_1d.csv (Binance spot, 2017-08-17..2026-09-30, 3,332 rows) as the single daily source; pitchfork CSV not used | look-ahead shift test passes; tags reproduce by hand on 5 dates; planted-edge test: +0.3% injected into a random 20% of events of one cell is detected at the stated n and nowhere else; false-positive run with no injection stays null | Sonnet Builder |
| P1 | Split frozen DEV results of RSI-DIV-MTF and Krown events by fast-cycling tags only (Cowen band side, 200D side, weekly SMA10 phase); halving bin x drawdown bin reported but not judged until DEV covers 2017-2021 (decision D3) | existing frozen event lists | >= 30 trades per cell to report, >= 200 to decide; placebo tag; same sign as the pooled effect in every year and in >= 2 of 3 tag episodes, each with a block-bootstrap 95% CI not crossing the opposite sign; cell passes only beyond the 95th percentile of the max between-cell gap over 1,000 circular-shifted label sets (family-wise) | Sonnet |
| F1 | Multi-timeframe swing confluence: 1h Williams pivots that line up with 4h/daily pivots, vs random levels (R1 rank 3) | 1m DEV 2022-01-01..2025-06-30; HOLDOUT 2025-07+ never loaded | beats random levels fee-net, n >= 200 | Sonnet |
| F2 | Rolling 1h Hurst (DFA) as a regime gate on existing layers, vs shuffled and random gates (R1 rank 2) | 1m DEV 2022-01-01..2025-06-30; HOLDOUT 2025-07+ never loaded | >= 10 regime switches per split, lift CI excludes 0; 2 thresholds x k layers logged as 2k trials in TRIALS.md | Sonnet |
| F3 | Phase-matched analog (nearest past windows) forecast vs random-path windows (R1 rank 4) | 1h DEV 2022-01..2025-06 (R1 rank 4: 48-bar paths, 24-bar outcome, expanding library); daily version descriptive only | beats surrogate random-walk library and block-shuffled outcomes, Holm over horizons, >= 500 non-overlapping forecasts per split | Opus or Sonnet |
| L1 | Multi-LLM blind labelling (R4 S1-S4) | rendered DEV windows | only if F1 gives a coded detector with DEV edge; cap 10% of one login's week | Gemini/GPT/Sonnet |
| J1 | Jala fractal method extract, then code a Jala-style rule set (13 params: 6 SOURCED, 6 OURS, entry NOT_IN_DATA) | captions | >= 5 fractal videos with verified quotes | Gemini (NUC); parallel from day one (own quota pool, no dependency on P0-F3) |

Every cell, threshold, horizon and label variant across P1, F1-F3 and L1 is one row in research/layer_lab/TRIALS.md before its outcome is read.

## 5. Forward log only (untestable, n = 1 per cycle)
- Molnar preprint (arXiv 2607.26188, not peer reviewed) bottom window 2026-10-05 to 2026-11-16 = peak 2025-10-06 + 364..406 days; his own block-bootstrap null reproduces the bottom cluster in 31-43% of paths, so this is a weak call even by the paper. Loukas low window Nov 2026 to early 2027, Cowen final low after the midterms (R2 s7). Logged as dated predictions, never a layer.
- "This cycle repeats 2017/2021": context line on Eagle_Eyes only.

## 6. Open risks
- Daily bars before 2017-08 are not on Binance; earlier cycles need Bitstamp/CoinMetrics (R1 Noticed).
- Two existing context engines agree on phase only 39-46% (R2 Noticed): P0 replaces neither until compared.
- A phase filter was tried once with no edge (composite -0.137 R/trade, R2 s5); phase is confounded with year.
- Daily feeds disagree by ~30 USD on the peak close (124,658.54 Binance vs 124,628.5 pitchfork CSV); one source per study.

## 7. Results so far (2026-10-31)
| Step | Verdict | Numbers |
|---|---|---|
| P-1/P0 phase tag + harness | BUILT | 15 tests; planted edge found 72-100% of runs at stated n; tags.csv 3,332 days |
| P1 phase split | BLOCKED, then run via P1b | no frozen per-event fee-net list existed for RSI-DIV-MTF or Krown |
| P1b RSI-DIV-MTF by phase | NEGATIVE | n=640, net -0.229 R/trade; every phase cell negative; shift null flags nothing; 4h only +0.042 R (n=138, under the decide bar) |
| F1 multi-TF swing confluence | FAIL | confluence n=2556 net -0.267 R, worse than matched random levels by -0.106 R (CI -0.143..-0.070); n far above the power need, not a thin-data null |
| F2 rolling 1h DFA Hurst gate | NEGATIVE | RSI-DIV-MTF and F1 fade, 2 thresholds (H<0.45, H<=0.55): no test passes; best lift +0.123 R [-0.109, +0.358] (RSI), fade gate A -0.062 R (wrong way, borderline); every kept side still negative fee-net; pre-registered RSI plant (+0.25 R) not flagged (kept n 119), see f2/RESULT.md |
| L1 multi-LLM labelling | GATED OFF | needs a coded detector with DEV edge; F1 gave none |

Reading: fading 1h fractal levels loses after fees, and confluence makes it worse, so price respects those levels less than random ones (it tends to run through them). Testing the opposite trade is a NEW trial with its own pre-reg; rough arithmetic says the gross gap (~0.1 R) is below the ~0.17 R taker fee, so expect it to fail too.
Next by expected value: F2 rolling Hurst regime gate, F3 phase-matched analogs (both parallel, own pre-regs), J1 Jala extract on Gemini; Krown has no DEV event list (needs its own study before any phase split).

