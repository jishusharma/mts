# Krown web app and public indicator definitions - audit 2026-10-22
Worker: Sonnet research. Scope: Krown web app, public TradingView scripts, BBWP origin, event-study method.
ACCESS LIMIT (read first): in this session WebFetch failed on EVERY host with `getaddrinfo ENOTFOUND` (krowntrading.net, app.krowntrading.net,
linktr.ee, x.com, youtube.com, tradingview.com and regional subdomains, teachable.com, pineify.app, cryptobassethound.com). Only WebSearch worked.
So NO page below was opened; every fact is a WebSearch result snippet (search-engine summary, not page text) and is labelled SNIPPET.
A proxy status check was blocked by the permission classifier and not retried. Nothing was invented. Re-run the NOT READ items from a machine where WebFetch resolves.

## 1. The web app
| Fact | Source | Status |
|---|---|---|
| App host is app.krowntrading.net; X account @KrownTradingApp ("Krown Trading App") bio links to it; described as a digital app venue with crypto metrics for "underlying market dynamics"; posts daily BTC updates, e.g. hourly leverage financing ("Shorts Pay Longs 12"), mostly 2022 and earlier | https://x.com/krowntradingapp (SNIPPET) | SNIPPET, page NOT READ |
| A route under the app: /desk/store lists product "Quant12" ("statistically driven, back-tested strategies for trend and range"), linked from a YouTube description | https://www.youtube.com/watch?v=vacro9FmdHE (SNIPPET) | SNIPPET, NOT READ |
| Route /desk/cryptos/dashboard ("Free Market Dynamics") is listed on his linktree per the repo note | https://linktr.ee/erickrown (repo KROWN_FREE_VS_PAID.md s1a; search lists the page) | NOT READ this session |
| Separate YouTube channel "Krown Trading App", plus video "KROWN TRADING APP 2.0 is **LIVE**" | https://www.youtube.com/@krowntradingapp2880 ; https://www.youtube.com/watch?v=teT4sWfQwiw (titles only) | NOT READ |
| Search snippet: his TradingView indicator description points to app.krowntrading.net for "Price Action" tooling (snippet cut off) | search result, no URL isolated | NOT READ |
| Free dashboard "centralcommand.io" mentioned in his bio per snippet (repo calls it the Central Command vault, /p/cpro, rejected for profit claims) | search snippet; https://krown-trading.teachable.com/p/cpro (repo) | NOT READ |
| krowntrading.net, www.krowntrading.net, krown.trading, krowntrading.com | WebFetch krowntrading.net: ENOTFOUND; others not tried (fetch dead) | NOT FOUND / NOT READ |
| Page list, indicator names inside the app, definitions, settings, series shown, update frequency, pricing tiers | - | NOT FOUND (app unreachable; JS bundle, route and API names NOT READ; no private API called) |
Search found no independent description of app contents. A search for "Krown Trading App 2.0 pricing" returned only unrelated tokens (KROWN/KRW) - ignore those.
Name collisions: KrownIQ at krown.network (https://krown.network/blog/krown-iq-a-smarter-way-to-trade) is a different company; "CROWN FX MARKETS" TradingView scripts are unrelated.
Inference (label): the leverage-financing post suggests the app shows funding-type data; whether it shows event-study tables, % green, BBWP etc. is UNKNOWN.
Operator claim ("app has the indicators and values he refers to, lots of data") is UNVERIFIED by me. Action: operator opens https://app.krowntrading.net/desk/cryptos/dashboard in a browser and screenshots the page list (no login) - screenshot intake.

## 2. Public TradingView scripts
Author on TradingView: displayed as "Crypto-Crown" (search snippet of the Krown RSI page). Profile URL tradingview.com/u/<user>/ : username NOT FOUND, profile NOT READ.
All found Krown scripts are INVITE-ONLY (TradingView notice: access by author permission, "usually granted after payment"):
| Script | URL | Description (SNIPPET) | Rating |
|---|---|---|---|
| Krown Trading RSI | https://cn.tradingview.com/script/RVesRm2s-Krown-Trading-RSI | oscillator timing entries/exits from a fast and slow signal; use with the Krown Fibonacci tool | PROPRIETARY |
| Krown Trading Fibonocci [sic] | https://cn.tradingview.com/script/qVeTCd63-Krown-Trading-Fibonocci | one of a "trifecta of oscillators" suggesting entries/exits from Fibonacci sequences | PROPRIETARY |
| Krown Trading - The Jewel | https://cn.tradingview.com/script/AbFkwV0T-Krown-Trading-The-Jewel | combines Krown RSI, Krown Stochastics, Krown Fibonacci and a "DMI proprietary signal" | PROPRIETARY |
| "Jewel Lite" (free and limited) | https://www.youtube.com/watch?v=imev_QEGPuA (title only) | free limited version; contents NOT READ | PROPRIETARY/PARTIAL (unknown) |
"Krown pivots": no TradingView page found by search (a search for it returned only an unrelated invite-only pivot script). Sold at $300 per repo notes (https://krown-trading.teachable.com/l/products, repo FREE_VS_PAID s2). Open-source Krown script: NOT FOUND.
Teachable indicator category (SNIPPET): https://krown-trading.teachable.com/courses/category/indicators lists "The Advanced Stochastic Package" (stochastic + DMI) with a 7-day free trial.

## 3. BBWP public definition (for FORMULAS.md s21.5)
Origin: The_Caretaker, "Bollinger Band Width Percentile", open source: https://www.tradingview.com/script/tqitSsyG-Bollinger-Band-Width-Percentile/
- SNIPPET (quote of description): shows "the percentage of bars over a specified lookback period that the Bollinger Band Width was less than the current Bollinger Band Width". Source code NOT READ.
- SNIPPET: has a "BBWP Length" input for the moving average forming the basis; a moving average of BBWP itself is plotted (upward cross = expanding vol); original supports basis types beyond SMA (per the simplified clone's note, https://il.tradingview.com/script/Rmw1hl3z-Simple-Bollinger-Band-Width-Percentile , which says the original ran past 100 lines and its clone is SMA-only).
- Third-party guide SNIPPET (unverified, secondary): defaults source close, basis SMA, basis length 7, compares to the prior 100 bars: https://pineify.app/pine-script/indicators/bbwp . A search with "252 / 13" returned no confirmation of those numbers; do not use them.
- Community thresholds SNIPPET: below 5% = possible consolidation end, above 95% = possible trend end (TradingView community write-up; URL not isolated).
- Other open-source variants (not the origin): https://vn.tradingview.com/script/uOPkVxXE-Bollinger-Band-Width-Percentile-Multi-Time-Frame ; https://il.tradingview.com/script/yaWmFuhO-BBWP-Boom-Doom ; descriptions only: "Bollinger Band Width Percentile" at https://www.deepalpha.one/indicator/bollinger-band-width-percentile/ (NOT READ).
Check against MTS (FORMULAS.md line 537, s21.5): MTS uses bbw=(upper-lower)/basis, SMA basis 7, lookback 100, close, percentile = 100 * count(previous 100 bbw strictly below current)/100, current excluded.
  - Basis 7 / lookback 100 / close / SMA: CONSISTENT with the secondary snippet (pineify) only; NOT confirmed against the Caretaker source.
  - Open points the source must settle: (a) is bbw divided by basis (MTS) or raw width; (b) is the current bar included in the window; (c) strict "<" (snippet description says "less than", matches MTS); (d) std multiplier default (MTS 2, OURS); (e) population vs sample std (MTS population). Items (a),(b),(d),(e) UNCONFIRMED.
Rating: BBWP = CAN REPLICATE (public concept, open script); exact defaults need the source read.

## 4. Event study / signal methodology (public descriptions)
No written public methodology page found. Only video titles and the repo's existing transcript work (not redone): format = trigger, n priors, % green at fixed horizons, median return, target; examples in repo INVENTORY.md s3 and FREE_VS_PAID s1d. Additional titles from search snippet: "Krown Quant Project - 12 Statistically Tested Bitcoin Trading Strategies" https://www.youtube.com/watch?v=vacro9FmdHE (description NOT READ; sells Quant12 in the app). Search for "10-day stochastic above 80 / Krown pivots / trending higher low" returned nothing on Krown (only unrelated academic event studies).
| Item | Public definition found | Rating |
|---|---|---|
| Event study (trigger, n, % green, median, window) | method is plain forward-return statistics; his raw event lists not public | CAN REPLICATE (method) ; his exact triggers PARTIAL; his numbers = claims only |
| 10-day / weekly stochastic > 80 | stochastic lengths NOT FOUND publicly (his Stochastic is inside paid Advanced Stochastic Package / Jewel) | PARTIAL (use standard 14,3,3 and sweep, OURS) |
| Krown pivots / trending higher low | no public script; repo has TA 101 definition of THL (INVENTORY s6) | PARTIAL (THL from TA 101 transcripts), indicator PROPRIETARY |
| Ribbon (Revin Ribbons $797), optimism index | closed, not found public | PROPRIETARY |
| 5/21/55 EMA corrective setup | numeric rules in repo FREE_VS_PAID s1d | CAN REPLICATE |
| BBWP | s3 above | CAN REPLICATE |
| Krown RSI / Fibonacci / DMI signal | invite-only | PROPRIETARY |
| Funding/OI series in app | app unreachable; X posts mention hourly leverage financing | UNKNOWN (MTS has own funding/OI feed) |
| On-chain, sentiment series in app | NOT FOUND | PROPRIETARY/UNKNOWN |

## 5. Next steps (operator or a machine with working WebFetch)
1. Open app.krowntrading.net/desk/cryptos/dashboard, /desk/store; list pages, tiers, series (screenshots; no login).
2. Open https://www.tradingview.com/script/tqitSsyG-Bollinger-Band-Width-Percentile/ and copy the Pine source and input defaults into this file; resolve s3 open points a-e.
3. Read https://linktr.ee/erickrown, the YouTube description of vacro9FmdHE and teT4sWfQwiw for the real app links and tier text.
4. Find his TradingView username from the Krown RSI page header.
