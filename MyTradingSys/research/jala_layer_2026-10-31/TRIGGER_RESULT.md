# TRIGGER_RESULT - Jala 400D close trigger study (DEV 2022-01-01..2024-07-01 only)

Verdict: **no cell passes.** Nothing in Jala's 400D trigger (close under/over, 200/400 cross) shows a fee-net edge over random days on DEV; 0 of 12 alt cells reach Holm p < 0.05 (smallest Holm p = 1.000 at m=24). HOLDOUT and VALIDATION unread. Run exactly as in PRE_REG.md (frozen commit f1a6ae169); side: under/death short, over/golden long; cost 0.20 % round trip (OURS).

## Events and results (Verdict arms)
Alts pooled = 20 coins; BTC = n 1-2 per cell, descriptive only (INCONCLUSIVE, no inference).

| trigger | h | universe | n | mean fee-net % | 95% week-block CI % | null mean % | p | p Holm(24) | verdict |
|---|---|---|---|---|---|---|---|---|---|
| under | 10 | BTC | 2 | 4.81 | - .. - | - | - | - | INCONCLUSIVE |
| under | 10 | alts | 155 | -1.02 | -4.29 .. 1.99 | -0.37 | 0.555 | 1.000 | FAIL |
| under | 30 | BTC | 2 | 10.96 | - .. - | - | - | - | INCONCLUSIVE |
| under | 30 | alts | 146 | -1.06 | -8.52 .. 5.91 | -1.56 | 0.813 | 1.000 | FAIL |
| under | 60 | BTC | 2 | 24.29 | - .. - | - | - | - | INCONCLUSIVE |
| under | 60 | alts | 146 | -0.14 | -9.60 .. 8.62 | -3.54 | 0.243 | 1.000 | FAIL |
| over | 10 | BTC | 2 | -4.60 | - .. - | - | - | - | INCONCLUSIVE |
| over | 10 | alts | 158 | 0.19 | -2.95 .. 3.35 | 0.01 | 0.870 | 1.000 | INCONCLUSIVE |
| over | 30 | BTC | 2 | -3.26 | - .. - | - | - | - | INCONCLUSIVE |
| over | 30 | alts | 155 | 3.79 | -3.02 .. 10.70 | 1.22 | 0.176 | 1.000 | INCONCLUSIVE |
| over | 60 | BTC | 2 | -20.48 | - .. - | - | - | - | INCONCLUSIVE |
| over | 60 | alts | 155 | 1.16 | -6.90 .. 8.99 | 3.21 | 0.464 | 1.000 | INCONCLUSIVE |
| golden | 10 | BTC | 1 | -5.11 | - .. - | - | - | - | INCONCLUSIVE |
| golden | 10 | alts | 25 | 1.50 | -6.52 .. 9.69 | -0.23 | 0.514 | 1.000 | INCONCLUSIVE |
| golden | 30 | BTC | 1 | 12.19 | - .. - | - | - | - | INCONCLUSIVE |
| golden | 30 | alts | 24 | 3.28 | -7.53 .. 14.91 | 0.73 | 0.632 | 1.000 | INCONCLUSIVE |
| golden | 60 | BTC | 1 | 8.84 | - .. - | - | - | - | INCONCLUSIVE |
| golden | 60 | alts | 24 | 4.89 | -14.01 .. 35.22 | 2.42 | 0.746 | 1.000 | INCONCLUSIVE |
| death | 10 | BTC | 1 | 2.05 | - .. - | - | - | - | INCONCLUSIVE |
| death | 10 | alts | 20 | 1.48 | -9.91 .. 10.48 | -0.19 | 0.605 | 1.000 | INCONCLUSIVE |
| death | 30 | BTC | 1 | 24.20 | - .. - | - | - | - | INCONCLUSIVE |
| death | 30 | alts | 20 | -2.48 | -19.28 .. 13.42 | -1.17 | 0.804 | 1.000 | FAIL |
| death | 60 | BTC | 1 | 30.07 | - .. - | - | - | - | INCONCLUSIVE |
| death | 60 | alts | 20 | 7.43 | -10.07 .. 24.77 | -2.96 | 0.227 | 1.000 | INCONCLUSIVE |

## Reading
- n events per universe: close-under 155/146/146 (alts, h10/30/60), close-over 158/155/155, golden cross 25/24/24, death cross 20/20/20; BTC 1-2 (BTC crossed the 400D only twice in DEV).
- Close-under then short: mean fee-net is slightly negative at every horizon (-1.0 %, -1.1 %, -0.1 %) and not better than random days (null means are as negative or more because DEV was a bear market). The "failed cup and handle" signal does not add short edge beyond the market drift here. FAIL on the three horizons means: this definition (first close under SMA400, short, spot cost 0.20 %) on these 20 alts in DEV shows no edge; it says nothing about BTC (n=2), other sides, Jala's discretionary reading, or 2025+ data.
- Close-over then long: +0.2 %, +3.8 %, +1.2 % fee-net, all CI straddling zero, p 0.18-0.87: INCONCLUSIVE, not a signal.
- Iron Dome crosses: n 20-25, CIs +-10-25 %; nothing resolvable.
- As a context gate for fractals F1-F4: no evidence in DEV that "under 400D" vs "over 400D" changes forward returns beyond the null; it should not be used to gate F1-F4 on this evidence.

## Caveats
- Events cluster in a few 2022 and 2023 weeks (alts cross together), so the effective independent n is far below the raw counts; the week-block CI is the honest width and is wide.
- Universe picked with hindsight (survivors, no delisted coins): bias favours longs, so the null result on longs is not flattered by this.
- DEV is 2.5 years with one bear and one recovery; a single regime sample.
- sd in the PRE_REG gate was an assumption (0.27, OURS); realised event sd is larger for 60d.
- Files: trigger_study/{{fetch_daily,count_events,trigger_study,run_trigger}}.py, results.csv; data in Dumps/jala_trigger (not committed).
