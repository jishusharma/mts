# Simulator desk and levels study: independent review (Fable, 2026-10-21)

Reviewed on trunk 08d6cbee9 in a fresh worktree on JIS-NB: read INPUTS.md, DESIGN.md, both cards, the hand-over, all desk and study code; ran the 22 desk tests (all pass, 27 s, after a 63 s one-time data cache build); started the desk, ran the frozen setup and two API probes in the browser, looked at the page and the six charts, stopped it; re-derived the frozen numbers from the stored per-idea CSV with my own bootstrap seed and through the study module; ran five extra settings (rows 4-8 under `sim-desk levels` in TRIALS.md). No code or card was changed.

## Verdict in one line

The desk does what the cards say and the numbers are reproduced exactly, but the headline it shows the operator is misleading on two points that matter more than any missing feature: two thirds of the "772 trades" never traded, and the orange "NOT ENOUGH DATA" rests on a power model that the zeros break. Fix what the verdict says before adding anything.

## A. Requirement check (operator's words, yardstick from INPUTS.md section 1)

| Requirement | Met | Evidence |
|---|---|---|
| One page, click / choose / run | yes | One local page, settings strip, one Run button, result on the same screen in 5-10 s. |
| Configure whatever layers to test | partly | Only the levels study exists. The module shape is there (`params/run/describe`); nothing else plugs in today, and the page always shows study one. |
| Free-form values, hit and try | yes | Stop distance, target multiple, both fees and the date range take any number inside DEV; I ran stop 1.3 % and zero fees from the API. |
| Room for more layers later | partly | Same as above: a shape, not a second study. Tom cannot fit (Java pipeline); Fabio is untested. |
| Results clearly visible, plain verdict | partly | Verdict bar, three numbers and a reason are there and readable. But "772 trades" counts 517 ideas that never filled (see B), so the first number on the screen is wrong for the operator's purpose. |
| Real example charts, where it passes and fails, light and precise | partly | Six SVGs of 1.4-2.6 KB each, candles, level, stop, target, entry dot, exit cross: light and uncluttered. Missing: the date and time of the trade (he cannot find it on a real chart), the entry level for "all in at the next level beyond" is not drawn so the entry dot floats off the only drawn line, and the commonest outcome (no fill, 67 %) is never shown. Winners are three near-identical +1.77 R pictures because the target is a fixed 2 R. |
| Critical things first, no clutter | yes | Verdict, three numbers, charts, one footnote. The page is spare. |
| Simple, economical, powerful | partly | Simple and economical, yes (one file each, stdlib server, seconds per run). Powerful only for this one study. |
| Plain words, no internal names | mostly | Settings and the description are plain. The verdict reason still talks of "an edge of +0.34 R" and "the rule needs 50 %", which he cannot act on. Two labels are confusing: "Take" is the entry filter and "Entry" is the scale-in. |

## B. Correctness and trust

Reproduced: frozen setup n 772, mean -0.039 R, 95 % range [-0.123, +0.048], gross +0.072, fee 0.111 R, power 31 %, verdict NOT ENOUGH DATA, both from the stored CSV (my own seed gives [-0.125, +0.043]) and from the desk's re-simulation (identical to 1e-9). Date lock refuses an end after 2024-06-30 in code and in the API, and the browser's date boxes are capped too. Ledger: one row per new setting, none for a cached repeat, written before the result shows. Chart stop and exit prices equal the simulator's (test). Trial counter and the "best of many tries" warning are on the verdict bar. All as claimed.

Three things are not right:

1. **No-fill ideas are counted as trades.** With "all in at the next level beyond", the order sits at a deeper level and often never fills. In the frozen setup 517 of 772 ideas have net exactly 0 (no fill, no fee); only 255 traded, and those average -0.119 R with a 41 % win rate. The screen says 772 trades, 13.5 % win rate behind the scenes, worst streak 7 (zeros reset the streak). This is also why the study's "best" variant is best: ranking 240 variants by mean net R where zeros count as trades favours the variant that fills least (the same setup with the first-level target fills 419 times and averages -0.381 R on the filled ones). The frozen rule was selected by an artifact of counting.
2. **The headline verdict rests on a model that the zeros break.** The card power rule feeds the two-point payoff model with win rate 13.5 % and reward/risk 8.8 (the zeros are in the "losses", so the mean loss is tiny and the ratio huge). That model's own mean is -0.176 R against an actual -0.039 R, and its "power 31 %" is the chance of calling a negative edge significant, not of seeing a positive one. The sample-spread rule, which uses the real trades, says FAILED with 87 % power against a +0.10 R edge. The screen puts the weak rule in the orange bar and the sound one in a grey footnote. For the operator the honest reading is: this setup failed on development data.
3. **Hit-and-try has no brake except a number.** Any value runs in seconds, every run is one DEV trial, and the only guard is "try #N" on the bar plus the off-desk validation run. That is the right design (no new gate), but the counter undercounts: each worktree has its own cache, so the same setting run in two trees logs twice (trunk already holds a duplicate of the frozen row from the lead's tree and mine), and runs through the study module directly (as I did at first) log nothing. The brake that actually works is social: the validation window is read once, off this desk. Say that in the PASSED text and leave it.

Smaller: a non-numeric input returns a raw Python error ("could not convert string to float"); the entry-filter choice E1/E4 was picked on validation-window data (known, carried over from the study); the chart's exit time is located by price search, not by the simulator's bar index, so a long trade can show the cross on the wrong candle.

## C. Top improvements, ranked (benefit, effort, what to cut)

1. **Count only filled trades. Do this first.** Show "255 trades (517 ideas never filled)", compute mean, range, streak and power on the filled ones. Benefit: the first number he reads becomes true, and the "best" variant stops looking best for the wrong reason. Effort: half a day, one test on the frozen CSV (255 filled, -0.119). Cut: nothing; this is a correction, not a feature.
2. **Put the sample-spread rule in the verdict bar; drop the two-point model from the screen.** Benefit: the frozen setup reads FAILED with a reason he can act on ("even a +0.10 R edge is ruled out") instead of an orange "not enough data" that invites more tries. Effort: an hour plus the card's wording (the card rule stays in the study report). Cut: the footnote, the "+0.34 R" sentence and the "rule needs 50 %" sentence.
3. **Date and time on every chart, and draw the fill level.** Caption "2023-03-14 09:35 UTC, +1.77 R long, hit target"; add a thin line for the level the entry actually filled at. Benefit: he can open a real chart and find the trade, and the entry dot sits on a line. Effort: two hours. Cut: nothing.
4. **Show one "typical no-fill" and one "day-end close" example when they are common.** Six pictures of the two most alike outcomes hide where the setup fails. Pick by outcome kind, not by median R, when one kind is over a third of ideas. Effort: half a day. Cut: one of the three near-identical winners.
5. **Second study only after he has used v1.** Fabio (order-flow bars on disk?) is the candidate; Tom does not fit a seconds-scale module. Effort: one card, about two days. Cut: the "layer-pluggable" promise in the page title until a second study exists; say "levels study" plainly.

## D. The levels strategy: park it

The numbers say no edge at the first touch with these exits, and the desk's own probes confirm it: with zero fees the frozen rule makes +0.072 R but its range still touches zero (lower end -0.007); the filled trades alone lose -0.119 R; the one unexplored direction from the study (a wide 1.3 % stop so winners are not cut) turns gross negative (-0.006 R at the frozen filter, -0.017 R on all touches) because a wide stop costs more per loss than it saves in cut winners. Fees are not the problem; the entry is. Cheapest next experiment, if the operator wants one more: none on this setup. If he insists, the only cheap untried thing is a different exit class (time or order-flow exit without a fixed target) on the filled-trade count, one trial, pre-written expectation of +0.10 R net, and stop if it misses. Default: park, do not run validation.

## E. What to remove

- The two-point power model from the desk (keep it in the study report where the card asked for it).
- The "Target, x risk" box when the exit is not "chosen multiple" (grey it out) and the raw Python error text.
- The duplicate ledger row per worktree: key the "already tried" check on TRIALS.md content, not on a per-tree cache file.
- The phrase "layer-pluggable" from DESIGN and the hand-over until study two exists; one study is what is shipped.
- The three near-identical winner charts: two examples per outcome kind is enough.

Nothing in this review needs the operator except the decision to park the levels layer (default given above: park).
