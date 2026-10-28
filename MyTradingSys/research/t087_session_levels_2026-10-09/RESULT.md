# T087 failed first break: base rates, BTCUSDT 1m 2022-01-01 .. 2026-10-07

Event: first touch of the previous UTC day high (side high) / low (side low) before 14:00 UTC, close back through the level within 60 min. Entry at that close, stop = spike extreme, target = Asia or EU session extreme on the other side, time exit 14:00 UTC (US-open placeholder). Net = minus 2 x taker 0.05%. Same-bar target+stop counts as stop. All clocks/thresholds NO-SOURCE. Verdict: n >= 300 and t >= 2.0.

Events found: high side 466, low side 447 (days with a failed first break).

- asia_target|touch_asia|high: n=345 target 27% / stop 67% / neither 6%, net -0.044% t -1.36 win 30% -> no edge
- asia_target|touch_asia|low: n=301 target 34% / stop 60% / neither 6%, net -0.025% t -0.66 win 36% -> no edge
- asia_target|touch_asia|both: n=646 target 30% / stop 64% / neither 6%, net -0.035% t -1.43 win 33% -> no edge
- asia_target|touch_eu|high: n=121 target 13% / stop 57% / neither 30%, net 0.037% t 0.61 win 33% -> insufficient n
- asia_target|touch_eu|low: n=144 target 5% / stop 63% / neither 32%, net -0.101% t -1.95 win 25% -> insufficient n
- asia_target|touch_eu|both: n=265 target 9% / stop 60% / neither 31%, net -0.038% t -0.96 win 29% -> insufficient n
- asia_target|touch_all|high: n=466 target 23% / stop 65% / neither 12%, net -0.023% t -0.80 win 30% -> no edge
- asia_target|touch_all|low: n=445 target 25% / stop 61% / neither 14%, net -0.049% t -1.64 win 32% -> no edge
- asia_target|touch_all|both: n=911 target 24% / stop 63% / neither 13%, net -0.036% t -1.72 win 31% -> no edge
- eu_target|touch_asia|high: n=2 target 100% / stop 0% / neither 0%, net -0.093% t -71.80 win 0% -> insufficient n
- eu_target|touch_asia|low: n=2 target 100% / stop 0% / neither 0%, net -0.080% t -6.28 win 0% -> insufficient n
- eu_target|touch_asia|both: n=4 target 100% / stop 0% / neither 0%, net -0.087% t -13.49 win 0% -> insufficient n
- eu_target|touch_eu|high: n=121 target 24% / stop 54% / neither 22%, net 0.028% t 0.56 win 36% -> insufficient n
- eu_target|touch_eu|low: n=144 target 14% / stop 62% / neither 24%, net -0.112% t -2.28 win 26% -> insufficient n
- eu_target|touch_eu|both: n=265 target 18% / stop 58% / neither 23%, net -0.048% t -1.35 win 31% -> insufficient n
- eu_target|touch_all|high: n=123 target 25% / stop 53% / neither 22%, net 0.026% t 0.53 win 36% -> insufficient n
- eu_target|touch_all|low: n=146 target 15% / stop 61% / neither 24%, net -0.112% t -2.31 win 25% -> insufficient n
- eu_target|touch_all|both: n=269 target 20% / stop 57% / neither 23%, net -0.049% t -1.39 win 30% -> insufficient n

## By year (both sides, touch session all)

- asia_target 2022: n=188 target 26% / stop 59% / neither 15%, net 0.001% t 0.02 win 35% -> insufficient n
- asia_target 2023: n=164 target 27% / stop 52% / neither 21%, net 0.014% t 0.32 win 41% -> insufficient n
- asia_target 2024: n=193 target 22% / stop 68% / neither 10%, net -0.027% t -0.61 win 28% -> insufficient n
- asia_target 2025: n=212 target 26% / stop 65% / neither 9%, net -0.077% t -2.45 win 28% -> insufficient n
- asia_target 2026: n=154 target 18% / stop 71% / neither 12%, net -0.087% t -1.93 win 25% -> insufficient n
- eu_target 2022: n=58 target 19% / stop 53% / neither 28%, net -0.002% t -0.02 win 38% -> insufficient n
- eu_target 2023: n=48 target 23% / stop 46% / neither 31%, net 0.015% t 0.20 win 44% -> insufficient n
- eu_target 2024: n=54 target 15% / stop 63% / neither 22%, net -0.061% t -0.86 win 24% -> insufficient n
- eu_target 2025: n=63 target 19% / stop 63% / neither 17%, net -0.123% t -2.77 win 22% -> insufficient n
- eu_target 2026: n=46 target 24% / stop 59% / neither 17%, net -0.058% t -0.80 win 24% -> insufficient n

## Reading (T087 session, 2026-10-09)
- The 1m-only data answers Jis's question as a base rate: after a failed first break of the prior-day high, price retakes the local (spike) high before the Asia low in 57-67% of events and reaches the Asia low first in 24% (EU low first in 20%); the rest do neither before 14:00 UTC. Mirror (prior-day low) is similar.
- The "retake" share is geometric: the stop sits a few ticks above the entry, the targets are far below it. It is a base rate, not an edge. The short entered at the fail close and held to the Asia/EU low, net of taker x2, is negative in every cell with n >= 300 (no edge); EU-target cells have n < 300 (insufficient n).
- 2025 and 2026 are the weakest years (net -0.08% to -0.12%); 2022-2023 are flat. No session-stratified edge to carry forward.
- All session clocks, the 60 min fail window and the 14:00 UTC US open are NO-SOURCE placeholders; the 2026-10-09 day in the item is one event, not evidence.
