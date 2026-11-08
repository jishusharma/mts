# Fable review: Argon's Tom/Fabio audit and the no-edge census (2026-11-09, login C, JIS-NB desktop)

**Verdict: the census is arithmetically right (re-run byte-for-byte: 2148 FAST_REJECTION events, 1871 gate-pass, -0.087 R; 50 of 50 sampled rows recomputed from raw klines match) and it proves one narrow thing: the classifier alone, as a 1R/1R fade on 1h bars, carries no directional information (gross -0.010 R at a median 96 bps stop, so fees are NOT the story on 1h). It does not test Argon's method (HTF ladder + session + node-to-node target on 5m/15m); that frame was never run. Argon's geometry diagnosis is right; his 77% acceptance claim misreads a descriptive study; the Java fix adds a direction nothing consumes.**

Re-run: `review_fable_run_census.py <auction_census.py> <cache>` wraps the unmodified `auction_census.py` with `api.binance.com` -> `data-api.binance.vision` (the main host is unreachable from JIS-NB; defect card). Recompute: `review_fable_recheck50.py <cache>` (own barrier/fee code, no import of the census or the classifier; fee per FORMULAS.md s17/s18.5 on entry and exit notional).

## a. Why no edge: real absence vs method fault

| Suspect | Evidence (recomputed) | Reading |
|---|---|---|
| Fee-to-stop geometry | 1h FAST stops: median 96 bps, p25 56, p75 162 -> fee 0.10 R median; 277/2148 (13%) fail the 0.25 R gate | NOT the cause on 1h. Gross is -0.010 R: coin flip before fees. On 5m it IS the cause (mean fee 0.925 R, 57/67 fail the gate) |
| Lookahead | `auction_census.py:111` levels from bars before day D; `:97` bias from the prior daily close; `:128` outcome from t+1; classifier window `bars[t-59..t]` | Clean. No lookahead found |
| Outcome window | H=24 bars both frames (`:276,:286`, OURS): 2 h on 5m, 24 h on 1h; 236/2148 (11%) still open at H | OURS and asymmetric across frames; open trades marked at last close. Minor |
| Stop definition | stop = sweep extreme, no buffer (`:140`); Tom: "below the last liquidity" (TOM-072); Fabio: "super small stop ... above the area" (Is1HvdfQm5c:144) | Matches both traders' words. Not a fault |
| Target definition | 1R fixed (`RR = 1.0`, `:34`, OURS). Tom: next high-volume node, NOT_SEEN fixed R (CONCEPTS.md:71,79); Fabio: 35-40% win at 1:4.5 (CONCEPTS.md:134-135) | Method fault, but recomputing with 2R and 3R targets gives -0.035 R (SE 0.029) and -0.023 R (SE 0.033): the Fabio shape does not rescue it either |
| Regime mix | 7y days bull 1032 / bear 830 / range 695; htf with -0.117 vs against -0.066 (gate-pass) | Mixed sample; no with-trend edge. Real |
| Session | none (`AUCTION_CENSUS_1108.md:10`). Recount by UTC 4h block, gate-pass net R: 00-04 n=622 -0.003; 04-08 n=139 -0.175; 08-12 n=146 -0.158; 12-16 n=526 -0.180; 16-20 n=261 -0.067; 20-24 n=177 -0.006 | Method gap: Fabio trades NY only (Pz8f0wWW12M:655), Tom the DAX cash session. The US-open block is the WORST cell for fades, consistent with Argon's own root cause 5 (fast approach = continuation) |
| Timeframe | 1h bars: 6-bar acceptance = 6 h; reclaim "<= 3 bars" = 3 h; rel_vol vs 48 h median | The classifier was designed for 5m/15m. On 1h its thresholds mean something else. Method fault |
| Sample | 1h n=1871 gate-pass, SE 0.022: decisive for the 1h/1R question. 5m: 5 weeks, n=10 gate-pass | 5m leg says nothing; 7y of 5m is fetchable from the public mirror (card) |

Net: **real absence** of information in the label at 1h/1R (every year 2019-2026 negative, n large); **method gap** on the frame the traders use (5m/15m, in session, HTF-gated, node target), which the census never ran.

## b. Is the census valid?

| Check | Result |
|---|---|
| Reproduce | Same tables to the last digit (bars fetched 14113 vs 14107 on Bybit; window identical at 10233 bars; 61789 vs 61788 1h bars; all event counts and R identical) |
| 50-row recompute | Every 43rd FAST_REJECTION event (50 rows, 2019-11-08 .. 2026-07-20): entry, stop, outcome, gross, fee, net recomputed from `binance_1h.json` with independent code: 50/50 match; all 2148 outcomes and gross R match, 0 mismatches |
| Fee math vs FORMULAS.md | s17: cost = 2 x 0.0005 x entry -> fee_r = 10 bps / stop bps (`auction_census.py:45`). Same. s18.5 (fee on exit notional too) differs by < 0.001 R at 1R. s13 slippage 2 bps RT and funding omitted: fee_r understated by ~20% (0.154 -> ~0.185 R mean). Direction of the error favours the strategy, so the no-edge finding stands |
| R math | gross R = +rr / -1 / mark-to-last-close; stop wins same-bar tie (`:49-53`): conservative, correct |
| Gate | fee_r <= 0.25 R from `DEFAULT_MAX_FRICTION_R` (`auction_context.py:48`), SOURCED to d-stops-follow-trade-1106: correct |
| Daily NOT RUN | The card title asked for "7y daily" (`auction-context-event-census-1108.json:73`). Daily bars cannot host a level-interaction classifier at prior-DAY levels; the request was ill-posed, the substitution to 1h was reasonable and declared (`AUCTION_CENSUS_1108.md:33`). But daily is not where Tom/Fabio trade either: they trade 5m/15m/footprint inside a session with daily/weekly levels as the map (CONCEPTS.md:34,103; SOURCED_RULES S8). The hidden frame is **5m/15m over years, in session**, not daily |
| Cooldown | `last_fire` reset per UTC day (`:112`): a level can fire at 23:xx and again at 00:xx. Minor double count, not a bias |
| Labels | Parameter table present (`AUCTION_CENSUS_1108.md:21-31`); one label wrong (see c, acceptance) |

Valid for the question it answers. Invalid as a test of the audit's method.

## c. Argon vs the sourced rules (SOURCED = trader's words with file:line; OURS = chosen here)

| Claim / parameter | Argon | Source check | Label | Verdict |
|---|---|---|---|---|
| 5-8 bps stops cost 1.2-2.8 R on 10 bps perps | root cause 1 | fees.py taker 0.0005/side; RESCORE.md median stop 5.3-8.4 bps | SOURCED (fee), measured (stops) | RIGHT, and it is exactly Fabio's "super small stop" (Is1HvdfQm5c:144) that breaks on BTC |
| Over-gating (S1 balance 3.1%) vs blind touching (0/48, 0/20) | root cause 2 | prior reports | measured | RIGHT |
| Missing 1M/1w/1d ladder | root cause 3 | Tom: "trend based only on the VPOC and the value areas" (TOM-053, Ld1dhjGdTCA:19); context first, flow for timing (S8, -dMWA_bbm3o:7) | SOURCED idea; every threshold (SMA20, +-2%, tau) OURS | RIGHT in kind; the census then gated on none of it |
| Java VAH/VAL asymmetry | root cause 4 | `SetupCandidatesBuilder.java:307,320,477-482` pre-fix | bug | RIGHT; fix landed 36513c888 but see defect J1 |
| Order flow without location = continuation | root cause 5 | `large_trade_absorption` 18% vs 27%; census 12-16 UTC fades -0.180 R | measured | RIGHT, and the census confirms it in the hour split |
| ACCEPTED = 6 consecutive 5m closes "SOURCED to accept80.py 2x30m" | `auction_context.py:544-545,668` | accept80.py:5 Event A = two consecutive **30m** closes = 60 min = **12** 5m bars; 6 bars = 30 min; on 1h bars 6 bars = 6 h | mislabelled: OURS, not SOURCED | WRONG label; threshold is half the sourced duration on 5m, 6x on 1h (card) |
| "77% continuation [72..81], n=300" as a trade statistic | AUDIT:10,104,142; testnet card title | `value_area_acceptance_2026-11-05/RESULT.md:10,13`: extends **half a VA width** same day, "Descriptive only, no fees, no trade rule ... part of the 77% is plain volatility; no placebo yet". Census ACCEPTED continuation at 1R, 7y 1h: -0.096 R gate-pass (n=2798) | measured, misread | WRONG as used: a half-width drift is not a 77% win rate; at 1R it loses |
| rel_vol >= 2.0 | `auction_context.py:540` | wick_census.py vol_rel (OURS); no Tom/Fabio number (SOURCED_RULES.md:48 "every numeric threshold NO-SOURCE") | OURS (labelled) | ok |
| knife 2% / <25% bounce / 12 bars | `auction_context.py:477-479` | wick_census.py:6-7 (OURS) | OURS (labelled) | ok |
| reclaim within 1-4 bars, fresh <= 3 bars | `:538-539,525` | Tom: "the speed with which it rejected" (TOM-010), no number | OURS | ok but unlabelled in the docstring |
| fee_r <= 0.25, net RR >= 1.20 | `:48-49` | d-stops-follow-trade-1106 (operator decision) | SOURCED (decision), OURS vs traders | ok |
| 1R target in the census | `auction_census.py:34` | Tom NOT_SEEN fixed R (CONCEPTS.md:79); Fabio 1:4.5 | OURS | fine for a count; not either trader's trade |
| Stop = sweep extreme, no buffer | `:140` | TOM-072, Is1HvdfQm5c:144 | SOURCED in kind | ok |
| Four Oct-Nov winners | AUDIT Part 3 | census: 67 FAST_REJECTION in the same window, 28 target / 38 stop | anecdote | Lead C was right: not evidence |
| Fabio v3 Model A confirm fix | `engine.py:89-92`, `models.py:310-311` | passes `touch_lvn` so confirm fills are managed | code | RIGHT, surgical; tests pass (18 passed in this folder) |

### Java fix 36513c888 (card java-va-state-asymmetry-fix-1108), two findings
- J1 (defect): `determineDirections` now adds "short" below VAL (`:322`), but `determineSetupType` returns `null` for short at every val/swing_low zone (`:482`), POC only when `trend_unhealthy` (`:486`), VWAP only `scalp_*` in balance or `tc_long` (`:493-497`). `classifyState` makes every outside-VA snapshot `trend_healthy` unless CVD opposes VWAP (`:303-307`). So a breakdown-continuation short below VAL (Argon's TOM-3 / Event A) still cannot become a candidate. The RulesTest asserts the direction list only.
- J2 (decision, OURS): the fix removed the `trend_healthy` kill at VAH instead of making the health check symmetric. Tom's S7 (4VXpUjhKG2U:7: trade only where volume supports the direction) argues for a volume-support condition on both sides, not for none. Recorded as DECISION in the commit; flagged, not reverted.

## d. What runs next under phase-first, testnet-forward

| Item | Call |
|---|---|
| Card auction-plan-testnet-forward-1108 as written | Half right. CONTEXT-only wiring of `build_auction_trade_plan` (no gate, no order) is correct and cheap. Wrong: (1) the "77% acceptance" scenario_ledger row must be restated as accept80 measures it (half VA width, descriptive) or not filed; (2) "run until it fails" has no failure rule; (3) no session field, although session is the biggest unexplained split |
| Rewrite | Context strip for 2 setups + per-trade log (session block, level family, htf bias, fee_r) + pre-registered kill: after 30 gate-pass fades on Deribit test, net R <= 0 -> stop and report. Null from this census: -0.087 R at 1R |
| The run that is missing | 7y **5m/15m** census (public mirror has it), in session, with the HTF ladder as a gate and node-to-node targets: that is Argon's claim, untested. Report by session block and by htf bias. Card filed |
| Not next | Another 1h fade study; more hand-picked trades; any Java deploy of the VAL short until J1 is fixed |

## Defect cards filed (raw)
1. `census-acceptance-threshold-mislabel-1109`: 6x5m labelled SOURCED to accept80 2x30m; sourced duration is 12x5m; on 1h 6 bars = 6 h.
2. `java-below-val-short-no-setup-type-1109`: J1 above.
3. `census-fetch-binance-mirror-1109`: api.binance.com unreachable from JIS-NB; use data-api.binance.vision; also add slippage 2 bps RT (FORMULAS s13) to fee_r.
4. `audit-77pct-acceptance-misread-1109`: AUDIT and the testnet card quote 77% as continuation; RESULT.md says half-width drift, descriptive.
5. `census-5m-15m-7y-session-ladder-1109`: the missing frame.

Regime mix (this review's frame): 7y days bull 1032 / bear 830 / range 695 (census rule, OURS). Noticed: `tasks.py --help` output crashes a PowerShell reader on cp1251 (byte 0x98) - cosmetic, not filed.
