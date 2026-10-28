# Audit of the three Fable 5.1 runs (2026-10-15/16): why each one stopped short of the edge question

Auditor: Opus 5.5, JIS-NUC worktree `jis-nuc/fable-runs-audit`, base origin/fast-track 00b20f21, zero operator input.
No VALIDATION or HOLDOUT bar read, no backtest run, no production code changed. Every number below is either re-derived
here from committed files (marked RE-DERIVED) or quoted from a committed file (file:line).

| Run | Prompt | Deliverable | Its verdict |
|---|---|---|---|
| R1 pilot | `layer_rebuild_2026-10-15/FABLE_PILOT_PROMPT.md` | `gross_effect_screen_2026-10-15/PRE_REG.md` (+ card Q72, run later by Sonnet: `RESULT.md`) | INCONCLUSIVE (n_T = 40) |
| R2 adversarial | (prompt not in repo; six questions restated in the review) | `fable_audit_2026-10-16/PROMOTION_REVIEW.md` | SAFE WITH FIXES, 3 HIGH |
| R3 A3 | `FABLE_PROMPT_PACK.md` section A3 (run 10-16, not 10-20) | `fable_audit_2026-10-16/CATALOGUE_AUDIT.md` | catalogue usable after a reader protocol |

## 0. Verdict (all three)

Each run did what its prompt asked, with good discipline: SOURCED/OURS labels, no holdout reads, quotes checked at source.
**Where they fell short was the prompts.** Each scope left out the one condition that decides whether the work can find a
fee-net edge:
- **R1 froze a test with no power check.** The pass rule needs a gross effect about 2.5x the cost before it can say PASS.
- **R2 checked that the promotion gate fails closed.** It did not check whether that gate can tell an edge from luck.
- **R3 checked that the catalogue matches the traders' words.** It did not check whether those setups can pay BTC fees at the stops the traders use.

The prompt pack's own edge question (A1/A2, "is MTS aimed at a real fee-net edge") was HELD. So the costly model ran three
narrow tasks and never got the question it was bought for (FABLE_PROMPT_PACK.md:4).

The common missing constraint is **economics before fidelity**: the cost is fixed per round trip. A candidate is worth
marking, coding or screening only if its *plausible* gross effect at its natural horizon and stop clears that cost with a
sample big enough to see it. Three numbers, cheap to compute before any outcome is read, would have changed what each run
did: the cost in R (cost / stop), the required per-trade signal-to-noise (cost / sigma at the horizon), and the MDE from a
count-only pass.

## 1. R1: gross-effect PRE_REG pilot

### 1.1 What it got right
Costs declared up front (14 bps all-taker, PRE_REG.md:32). A shared ledger before the flow split, which fixes study.py's
per-arm cooldown (PRE_REG.md:86). Day-clustered SE. Decay grid with d=0 as an upper bound. Gap-stop trap named. Loader guard
on 2024-07-01. The Codex re-count matches (card `gross-screen-gpt-audit` result: 40/1400/1440).

### 1.2 Lens: power. The screen could not pass, and a count-only pass would have shown that before freezing
- PRE_REG.md:76-80 sets N_min = 200 and says "n before outcomes", but the session froze the file without running the count.
  Counts need no outcome column, and `screen.py --count` was later run as step 2 of the card. The count came back n_T = 40
  (RESULT.md:45): the flow flag fires on 2.8 % of encounters, 40 in 912 DEV days.
- The pass bar is not mean >= C but mean - C >= 2 SE (PRE_REG.md:78). RE-DERIVED from RESULT.md:8: per-encounter sd at
  h=60 = 0.1304 x sqrt(40) = 0.82 %.
  - At n = 40, PASS needs mean >= 0.14 + 2 x 0.13 = 0.40 %. If the true effect equals the cost (0.14 %), the chance of PASS
    is about 2 %.
  - Even at the floor n = 200 (SE 0.058 %), 80 % power needs a true gross of 0.14 + 2.8 x 0.058 = **0.30 % per hour-long trade,
    i.e. 0.37 sd per trade**. No minute-scale flow signal in the repo or in the literature comes near that.
- **Missing constraint:** a PRE_REG must print n and the MDE from a count-only pass, then refuse to freeze when
  MDE + C exceeds a plausible effect. Without that gate a screen is INCONCLUSIVE by construction, and its "stop" outcome is
  decided by the design rather than by the market.

### 1.3 Lens: verdict precedence. The decisive number is hidden under "INCONCLUSIVE"
- The control arm was well powered: n_C = 1,439, SE 0.0246 %, MDE 0.069 %. It came back mean -0.008 %, t_cost -6.0
  (RESULT.md:10). That is a clear FAIL of the plain session-extreme fade.
- PRE_REG section 4 has no FAIL_CONTROL word. INCONCLUSIVE on T is tested first (RESULT.md:38), so the headline says
  INCONCLUSIVE and the one powered result reads like a footnote.
- RESULT.md:50 says "FAIL/INCONCLUSIVE: stop". That contradicts PRE_REG.md:80, which says INCONCLUSIVE is "never relabelled
  NEGATIVE".
- Fix: report one verdict per arm. Here: T INCONCLUSIVE, C FAIL.

### 1.4 Lens: the decay curve was printed but not read (RE-DERIVED from decay.csv, arm C, ALL)
| d | h=5 | h=15 | h=60 | h=240 |
|---|---|---|---|---|
| 1 | +0.019 (SE 0.011) | +0.015 (0.016) | -0.007 (0.025) | -0.076 (0.052) |
| 5 | -0.002 (0.010) | -0.009 (0.013) | -0.030 (0.023) | **-0.103 (0.051), t = -2.0** |

Fading a fresh session extreme gives a 2 bp reversal over 5 minutes. That turns into a continuation of about 10 bp by 4 hours.
The sign flips. So the opposite trade (follow the extreme) is the better-supported family, and even it is about 4 bp short
of 14 bp gross. Nothing in RESULT.md or the plan says so. Because it was seen on DEV, "follow the extreme at 240 min" is now
post hoc. It may become a new PRE_REG only if that PRE_REG reads VALIDATION once, with the DEV exposure logged.

### 1.5 Lens: economics. The horizon choice sets how hard the test is
RE-DERIVED per-encounter sd for arm C: h=60: 0.0246 x sqrt(1439) = 0.93 %; h=240: 0.0518 x sqrt(1439) = 1.97 %. To break
even at C = 0.14 % a signal needs mean/sd = 0.15 at 1 h, 0.07 at 4 h, and about 0.05 at a daily hold. A fixed cost is cheaper
to beat per trade at longer horizons. R1 fixed h = 60 for continuity with study.py (PRE_REG.md:68), not on cost grounds. The
`TOM_ON_BTC.md:24` floor (stops >= 0.40 % taker) says the same thing in stop terms. R1 did not cite it.

### 1.6 Lens: fidelity and kill scope
Location L and flag F are OURS proxies: 00:00 UTC anchor, top-quintile leg, sign of the 5-bar kline delta. Tom's "selling
surplus in delta" is a footprint reading at the extreme, not a 5-bar kline sum. Yet PRE_REG.md:81 lets a FAIL park "Tom T5"
and "Krown Q66-Q69". Krown is a daily/weekly family (CATALOGUE_AUDIT.md:138) that a 1-minute session-extreme screen cannot
speak to. The kill scope should be the tested rule family only. (Krown is parked anyway on G2-G3, OPERATOR_DECISIONS.md:826,
so no harm landed.)

### 1.7 Lens: process
The pilot spent an hour shipping, not thinking (PILOT_USAGE.md:14-16). The queue still points at the finished card:
NEXT_SESSION.md:3 says "Next unblocked: Q72 gross-effect-screen-dev" and :17 lists Q72 as to-do, while
`tasks/gross-effect-screen-dev.json` is `done` (closed 2026-10-15T19:08Z). A relay session that trusts the text could
re-run the screen, which would be a second outcome read on a one-run PRE_REG. Fixed in this commit (section 5).

## 2. R2: adversarial review of the testnet changes

### 2.1 What it got right
Six questions answered with file:line. Pre-change test runs done in a throwaway worktree. Three HIGHs, each carded and since
shipped: 8254ece6 (H1), 644ca8b6 (H2, M4, L7), 3c7dcf86 (H3).

### 2.2 Lens: the gate checks shape, not statistics (missed)
`promote.py:185-192`: the OOS rule is net_r > 0 and ci_low > 0, with n_trades >= MIN_TRADES = 30
(`promote.py:36`, "OURS: sanity floor").
- The trial ledger is checked for *existence and a matching variant count* (`promote.py:194-211`), but the variant count
  never tightens the threshold. Ten variants each tested at a 95 % CI give a 1 - 0.975^10 = 22 % chance (about 1 in 5) that a no-edge setup is
  promoted. M5 caught that the numbers are self-declared, but the review did not ask whether a true number passing this gate
  would be evidence of an edge.
- Missing constraints:
  - CI level adjusted for the ledger's variant count (Holm or Bonferroni).
  - OOS = a VALIDATION read logged once in the exposure ledger (not DEV).
  - MIN_TRADES derived from the MDE (R1's numbers say 30 trades see only a very large effect).

### 2.3 Lens: what testnet evidence is for (missed)
- H1's own text says none of today's testnet trades can count toward GO_LIVE_BAR (PROMOTION_REVIEW.md:46-48). The fix kept
  them all trading: RE-DERIVED, `auto_trader_config.json` `pre_pipeline_sources` has 20 grandfathered entries, all
  "operator decision pending", review_by 2026-10-23. So 20 sources keep producing trades that, by the project's own rule,
  are not evidence.
- The one thing that stream *could* calibrate is the cost model every PRE_REG assumes: 2 bps slippage per taker leg, 60 s
  latency, maker filled only on trade-through (PRE_REG.md:31, :66, :108). But no execution module records the signal price
  at decision time. Grep under `execution/` for signal_price / decision_price / ref_price / entry_ref finds 0 non-test hits;
  fills are recorded (`executor.py`). So realised slippage and latency cannot be measured from the journals.
- Caveat: Deribit testnet liquidity is not production liquidity (PRE_REG.md:109), so testnet slippage is a lower bound at
  best. The review should have asked this, either to make testnet pay for itself or to say it cannot.

### 2.4 Lens: shadow data usable as forward OOS? (partly missed)
Shadow events carry t, entry_ref, stop and target (live_runner_cli.py:224-231). They do not carry the rule or code sha. A
forward shadow sample can therefore mix rule versions without anyone being able to tell later.

### 2.5 Lens: process
The three HIGH fixes shipped once each. Then four relay sessions (claim/release pairs 2026-10-16 01:23-02:44 IST, e.g.
9c34e5fa, d6e4f890, ae324fa6, 93c6860d) spent their boots discovering they were "already shipped". The cards were not
marked done when the fix landed.

## 3. R3: A3 catalogue + rebuild audit

### 3.1 What it got right
31 of 31 quotes opened at the source. Three wrong rows and two missing setups found with quotes. The OURS-definitions
protocol (P3) and the enriched G3 windows (P4) are sound. P6 (weekly-bar setups first, because fees are a small fraction of
their stops) is the right instinct, and it is the one place the edge question showed through.

### 3.2 Lens: cost in R per row (missed; this is the binding constraint)
The audit asked "can a person mark it on a BTC chart" (CATALOGUE_AUDIT.md:101), never "can it pay BTC fees at its stop".
RE-DERIVED with C = 0.14 % all-taker (0.09 % maker-in):
| row | trader's stop (his words) | as % of price | cost in R on Binance |
|---|---|---|---|
| TOM-3 | "risk of 12 ticks" (ES, target 6,768: CATALOGUE_AUDIT.md:34-35) | 3 pts / 6768 = 0.044 % | **3.2 R** (maker-in 2.0 R) |
| TOM-1 | "stop-loss of 20 points" (DAX; level 15,000-24,000) | 0.08-0.13 % | 1.1-1.7 R |
| T-3 claim | swing: 35 % win, 4 R (hQ8sOq67x5o, CATALOGUE_AUDIT.md:64) | | gross +0.75 R per trade |

Read together: even if Tom's own SOURCED swing numbers transfer to BTC exactly, the expectancy of +0.75 R pays for a
1.1-3.2 R cost only when the stop is at least 0.14 / 0.75 = 0.19 % (taker). That is before slippage, and `TOM_ON_BTC.md:24`
puts the working floor at 0.40 %. **Every intraday Tom/Fabio row at the stop he states loses on Binance by construction.**
Widening the stop to 0.40 % turns it into a different setup on a different timeframe, one he never stated.

So G3 kappa marking (P4: TOM-4, 6, 12, 15, FAB-1, 4, 5 first) would buy fidelity for rows that cannot clear cost as written.
The order the audit kept ("Nothing else in the plan is wrong in order; G0->G6 holds", :139) is missing a cheap gate before
G3: per row, record the stated stop, the timeframe, cost in R, and the trader's own SOURCED hit-rate/R:R (T-3 gives them per
family). Then send to G3 only rows where the stated (or naturally scaled) stop is >= 0.40 %, or where a maker entry is part
of the setup.

### 3.3 Lens: completeness was sampled, then not extrapolated
- 3 of 3 V1-only Tom videos held missing material: a setup (T-1), rules (T-2) and numbers (T-3).
- 0 of 3 "never extracted" videos did.
- DyS79Eb92Ug was read through 60 keyword windows, not in full (CATALOGUE_USAGE.md:14), and still gave 5 rule groups.

23 never-extracted Tom videos and the rest of the V1-only set remain unread. "Missing setups 2" is a floor, not an
estimate. The audit should have said so and costed a full Haiku sweep.

### 3.4 Lens: transfer conditions beyond fees
Tom and Fabio read a single central book with a cash session, an opening auction and a known contract size (Fabio's
"30 contracts", CATALOGUE_AUDIT.md:75). On BTC, volume is split across venues and there is no session (the anchor is OURS,
D1). The markability test checks "in the data we hold", not "does the concept exist on this market". Volume-profile and
big-trade rows need a stated venue-share assumption: Binance alone, labelled OURS.

## 4. What has to happen to find an edge (one list for all three)

| # | Constraint | Applies to | Who / cost |
|---|---|---|---|
| E1 | **Count before freeze**: every PRE_REG prints n and MDE from a count-only pass; it does not freeze if MDE + C exceeds a plausible gross effect at that horizon | R1, all screens | Sonnet: PRE_REG template + screen harness rule, S |
| E2 | **One verdict per arm** (T and control separately) and a decay-sign line in RESULT; the kill scope is only the tested rule family | R1 | Sonnet, S |
| E3 | **Cost-in-R gate before G3**: catalogue column `stop_pct, tf, cost_R_taker, cost_R_maker, sourced_hitrate_RR`; G3 only for rows that clear it | R3 | Sonnet catalogue session, S |
| E4 | **Promotion threshold uses the ledger's variant count** (Holm), OOS must be a logged VALIDATION read, MIN_TRADES from the MDE | R2 | Sonnet, live-path-adjacent tests, S |
| E5 | **Testnet records the decision price and the code sha** per alert/entry, so slippage and latency vs the PRE_REG assumptions can be measured (lower bound on testnet) | R2 | Sonnet, live-path rules apply, M |
| E6 | **Reusable screen harness**: event definition -> shared ledger -> decay grid -> count/MDE gate -> per-arm verdict, so the next candidate costs a config, not a Fable session. Start from R1's screen.py | all | Sonnet / Codex lab, M |
| E7 | **Full completeness sweep** of the 23 never-extracted Tom videos and the V1-only set, keyword-first with Haiku | R3 | Haiku, S |

Candidate order this implies (OURS):
1. Weekly/daily-stop families first (Krown KR-S1/S8, Malkan CLEAR-stop rows, TOM-1b swing), because cost is a small
   fraction of their stops.
2. The "follow the session extreme, 4 h" family only as a new PRE_REG read once on VALIDATION, because it was seen on DEV.
3. Intraday tape rows only with a maker entry in the setup and stops >= 0.40 %.

## 5. Done in this commit
- `system/NEXT_SESSION.md`: Q72 marked DONE (INCONCLUSIVE, b42cef1b), so no relay session re-runs a one-run PRE_REG.
- Cards raw (lane SONNET/HAIKU, this file as ref): `fable-audit-e1-count-before-freeze`, `fable-audit-e3-cost-in-r-gate`,
  `fable-audit-e4-promotion-variants`. E2, E5, E6 and E7 are listed above for the operator to card.

## 6. Operator decisions (defaults applied until overruled)
| # | Decision | Default |
|---|---|---|
| D1 | Keep the 20 grandfathered testnet sources trading past 2026-10-23? | Keep only if E5 lands by then (they then calibrate costs); else move to shadow |
| D2 | Put the cost-in-R gate (E3) before G3? | YES |
| D3 | Pre-register "follow the extreme, 240 min" for a single VALIDATION read? | NO until E1 and E6 exist; then yes, as the first harness run |
