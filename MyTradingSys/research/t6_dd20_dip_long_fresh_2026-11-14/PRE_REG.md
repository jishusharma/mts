# PRE_REG: T6 DD20 deep-drawdown weekly dip LONG on fresh coins (2026-11-14), frozen before any outcome

Source cell: edge9 `weekly_streak_bounce_2026-11-14` (branch `JIS-NB/edge9-weekly-streak-bounce-1114`, files PRE_REG.md and study.py), row "DD20 E1 X2". Design: `EDGE_WAVE2_DESIGN_1114.md` (notes folder), pick T6. Frozen BEFORE any signal, trade, return or placebo number is computed; only availability checks (file lists, meta sidecars, row counts) were looked at. Research, not advice; nothing is an edge until a fee-net out-of-sample result passes. SOURCED = named file; OURS = our choice, stated here.

## Context

Question: does the DD20 weekly dip long (buy the Monday open after a week that closes 20% under its 8-week high, hold 2 weeks) keep a fee-net edge on coins the rule was never seen on? The source row had a positive sign in both of its splits (DEV +3.0%, n 213; VAL +2.6%, n 391) and failed only on CI width (low -0.2%), placebo p 0.053 and multiplicity. The lever here is more independent coins, not a new rule.
Regime: none gated, because the source cell is ungated. Every event is tagged two ways and the mean per tag is a descriptive row only: (a) source BULL/BEAR tag = weekly close of the event week above/below the simple mean of the last 50 weekly closes including that week (SOURCED: source study.py `events()`, bull flag; None when fewer than 50 weeks, so those events are untagged); (b) MTS brain `cycle` BULL/BASE/BEAR of the entry day from `F:\MTS\data_cache\mts_brains\phase_daily.csv` (the brain builds the row of day d from closes through d-1, so the entry-day row uses no entry-day close; checked via `close_used` in the audit).
Phase: no phase gate. The brain 6-phase `label` is reported as a descriptive cut. Active today for BTC (descriptive, read from `phase_daily.csv` last rows): 2026-11-14 label MARKDOWN, cycle BEAR (row provisional), brain rsi14 25.5; 2026-11-13 MARKDOWN / BEAR; 2026-11-12 DISTRIBUTION / BASE. So the setup is live in a BEAR cycle today.
Session: none. Weekly bars, entry at Monday 00:00 UTC; 24/7 market, no session gate tested.
Entry: the Monday 00:00 UTC open right after a completed week whose close is at or below 0.80 x the highest weekly close of the 8 weeks before it.
Regime mix: filled in RESULT from the data (share of DEV and VAL fresh events in source BEAR, and in brain BULL / BASE / BEAR, and of calendar Mondays). Expected, from the source study, about 75% of VAL events in source BEAR (source RESULT.md "Regime mix": DD20 75% on 22 large coins); fresh coins will be reported as measured, and no result is generalised beyond the mix seen. VAL (2024+) holds the 2024 bull, 2025 and the 2026 slide.

## Rules (one frozen cell, no grid, no second pass)

| Item | Rule | Label |
|---|---|---|
| Daily bars | Binance spot `<COIN>USDT` 1d, UTC. Per coin keep the longest contiguous run of days, start at its first Monday 00:00 UTC, keep whole 7-day weeks only (complete weeks) | SOURCED (source study.py `Coin.__init__`) |
| Weekly bar | week w = 7 daily bars Monday to Sunday; close = Sunday close, high/low over the 7 days | SOURCED (same) |
| Event DD20 | at week w >= 8: weekly close(w) <= 0.80 x max(weekly close(w-8 .. w-1)) | SOURCED (source PRE_REG "Events", study.py); 0.80 and 8 not tuned |
| Cooldown | per coin, a new event only if w - (week of the previous event) >= 8; the clock moves only when an event fires | SOURCED (source study.py `w - last >= 8`; PRE_REG text "within 8 weeks" read as gap >= 8 weeks) |
| Entry E1 | buy the open of d0 = the Monday after week w (first daily bar after the event week). The last coin week cannot fire (no Monday after) | SOURCED (source E1) |
| PRIMARY exit X2 | close of day (entry_day + 13), no stop; 14 days in market | SOURCED (source X2: e + 7k - 1, k = 2) |
| Gross return | close(exit day) / entry open - 1 | SOURCED |
| Fee | 12 bp round trip = 2 x BINANCE_TAKER + SLIPPAGE_RT_S13, both imported from `MyTradingSys/backtest/fees.py`; subtracted from the % return | SOURCED (fees.py) |
| Funding (new here) | spot stands in for a perp held 14 days, so charge funding paid by the long. Real rule: sum of the cached funding `rate` prints with entry_open < print_time <= end of the exit day (UTC midnight after the exit day), print times rounded to the second; positive rate = long pays, negative = credit; expressed on entry notional. Flat rule: used for the whole trade when the coin's funding cache does not cover the window (first print later than the entry, or last print earlier than the exit): 1 bp per 8 h slot paid by the long, 3 slots per day. The number of trades on each rule is reported | OURS (flat 1 bp / 8 h is conservative); cache `F:\MTS\data_cache\binance\wave2-1114\funding` (columns ts, rate) |
| Net % return (primary) | gross - fee - funding. Rows reported side by side: gross; net of fee only (the no-funding row); net of fee + funding (the verdict row) | OURS (row definition) |
| SECONDARY row STOP | same event and entry. stop = entry - 2.5 x ATR14(1d, Wilder, at the prior daily close, i.e. the day before entry; first TR uses its own close as previous close, ATR seeded by the simple mean of the first 14 TR, as the source). Checked on daily lows from the entry day through day entry+13; a day whose open is at or below the stop fills at the open, else at the stop; else time exit at the close of day entry+13. Skip if stop <= 0 or ATR undefined. R = net return (fee + funding, funding charged through the end of the exit day) / (2.5 x ATR14 / entry) | OURS (2.5 and the ATR period are new here; the recipe shape is copied from the source XS row, whose stop was base_low - 0.5 ATR, so this is not the source stop) |
| Primary row in R | primary net and gross return divided by the same risk unit (2.5 x ATR14 at the prior close / entry), so the table shows gross R and fee-net R for the primary row. Trades with undefined ATR are excluded from the R columns only (counted) | OURS |
| Data end | an event whose exit day is beyond the coin's last bar is skipped if the coin still trades (last bar within 30 days of the data pull); for a coin that ended earlier (delisted or renamed) the trade exits at its last available close and is flagged DELIST-EXIT, counted and listed. The source skipped all incomplete windows; this difference is OURS and chosen so collapses are not hidden | OURS |
| Observation | one trade = (coin, entry Monday) | SOURCED |
| Seed | 1114 | OURS |

## Data and fresh universe

Public Binance spot klines, cache `F:\MTS\data_cache\binance\wave2-1114\` (`spot_1d`, `funding`, one CSV per symbol plus `.meta.json` sidecar; committed tests never read it). Availability checked on 2026-11-14 at freeze time: the `funding` folder holds 41 symbols with sidecars, including every fresh candidate below; the `spot_1d` folder was NOT yet present on disk at the freeze check (the fetch log `_fetch/log.txt` was still copying funding). Prices will be read at the code stage from that folder once present, or fetched with the same recipe (`_fetch/w2fetch.py`, Binance public data, no keys). This is an availability fact only; no price was opened.

Frozen candidate list (48): NEAR FIL ALGO MATIC SAND MANA AXS THETA EOS XTZ IOTA ONT QTUM ZIL ENJ BAT CHZ ICX WAVES KNC OMG RVN HBAR EGLD FTM GRT AAVE COMP SNX MKR CRV YFI SUSHI 1INCH RUNE KAVA ZRX IOST ONE CELR ANKR STORJ BAND LUNA FTT XMR DASH OCEAN.
Source universe (22): BTC ETH BNB XRP ADA DOGE SOL LTC LINK TRX AVAX BCH XLM NEAR UNI ZEC AAVE HBAR XMR QNT ICP SHIB. Verification: the source study files do not store a frozen list (fetch.py builds it live from CoinGecko on 2026-11-14); the 22 names were verified against the per-coin VAL event list printed in the source RESULT.md (S5 E1 row: ICP SHIB SOL BCH ADA AVAX DOGE HBAR LINK LTC XLM XRP BNB NEAR QNT ZEC AAVE ETH UNI BTC TRX XMR = 22), which equals the list supplied with the task.
Overlap removed: NEAR, AAVE, HBAR, XMR (four candidates are in the source universe). FRESH = 44 coins: FIL ALGO MATIC SAND MANA AXS THETA EOS XTZ IOTA ONT QTUM ZIL ENJ BAT CHZ ICX WAVES KNC OMG RVN EGLD FTM GRT COMP SNX MKR CRV YFI SUSHI 1INCH RUNE KAVA ZRX IOST ONE CELR ANKR STORJ BAND LUNA FTT DASH OCEAN. No coin is added, swapped or dropped for performance.
Drop rule: a coin stays if it has at least 60 complete weeks after the contiguous-run rule; fewer = dropped and listed with its week count in RESULT. Delisted or renamed coins (for example LUNA, FTT, OMG, MATIC data end) stay in until their last bar.
Survivorship note: the candidate list is a hindsight list of coins that existed in 2019-2021 and were large enough to be listed; coins that were listed and then delisted and are not in the list are absent, which biases results upward for longs. Coins in the list that collapsed (LUNA, FTT) are kept to their last bar and exit at the last close, but a real position could not always exit at that close, so collapse trades are optimistic. Pooled old + fresh is a descriptive row only, can only be built for source coins present in the cache, and is never a verdict.
Fresh-coin rule: every fresh-coin trade is out of sample by coin, not by calendar time (same weeks as the source coins), which is why the time split stays.

## Splits

DEV = entry Monday <= 2023-12-31; VAL = entry Monday >= 2024-01-01. The source used 2021/2022 (DEV <= 2021-12-31, VAL >= 2022-01-01); this wave uses the design-note standard and says so. The signal bar is the event week whose close is 00:00 UTC of the entry Monday, so entry date and signal-bar close time are the same instant and the two readings of the split coincide.

## Pass bars (all on the PRIMARY row X2, net of 12 bp + funding, fresh coins, unless stated)

Statistic: mean net % return per trade. Cluster unit = ISO entry week (all coins pooled; the bootstrap resamples ISO weeks with replacement, 2000 resamples, seed 1114; resampled mean = sum of trade returns in the drawn weeks / number of trades in the drawn weeks, as the source).
1. VAL: n >= 30 trades and >= 20 distinct ISO entry weeks, else UNDERPOWERED (bars 2-7 are reported but cannot give PASS). DEV with n < 10 also leaves bar 3 UNDERPOWERED.
2. VAL mean net > 0 and the week-cluster bootstrap 95% CI low (2.5th percentile) > 0. One-sided bootstrap p = (number of resampled means <= 0, plus 1) / 2001, used for Holm below.
3. DEV mean net > 0 (sign agreement).
4. Excess over random entries (placebo): for every real VAL trade draw one random Monday of the SAME coin, same split, same source BULL/BEAR tag (untagged matches untagged; if the bucket is empty fall back to same coin + split and count the fallbacks), with a complete 14-day window (or the same DELIST-EXIT rule), and apply the same exit (X2, 12 bp, same funding rule). One draw = the mean over the matched set of trades; 1000 draws, seed 1114. The real mean must be >= the 97.5th percentile of the draw means, and excess = real mean minus the mean of the draw means must be > 0. Placebo p = (draws >= real, plus 1) / 1001 is reported. The design wording "same phase flag" is read as the source BULL/BEAR tag, the only flag this cell has. For the STOP row the draws use the same stop recipe at the random Monday (reported, not a bar).
5. Ex-best-5 entry weeks: drop the 5 ISO weeks of VAL with the largest summed net return; the mean of the remaining trades must be > 0.
6. Buy-and-hold baseline: for each Monday of the same split (all weeks, every Monday open to the close of day +13) take the equal-weight mean of the 14-day forward return across the fresh coins that have a complete window that Monday, charged the same 12 bp + funding rule; baseline = mean of those weekly basket returns over the split (overlapping windows, stated). The event mean net must be >= that baseline mean. The gross comparison is reported next to it.
7. Top-coin removal: drop the single coin with the largest summed VAL net return; the mean of the rest must stay > 0, else FRAGILE (reported, blocks PASS). Removal of the top 3 coins one after another is reported as well.
Family: one cell per test, m = 3 across T4-T6. Holm over the three VAL one-sided p-values (this study contributes the bootstrap p from bar 2; the other two come from their RESULT files; the coordinator computes Holm). A PASS whose Holm-adjusted p exceeds 0.05 is labelled MULTIPLICITY-FLAGGED. If the other p-values are not yet known, this study reports its own p and the worst-case adjusted value min(1, 3 x p).

## Kill criteria (T6)

KILL the line if any of: (a) VAL mean net on the primary row <= 0; (b) the STOP row VAL mean R (fee + funding net) <= 0; (c) ex-best-5 weeks mean <= 0. Meaning: DD20 was drift plus survivorship. A killed line cannot be labelled PASS even if bars 1-7 would otherwise hold.

## Verdict vocabulary

PASS = bars 1-7 all hold and no kill criterion fires. FAIL = bar 1 holds and at least one of bars 2-7 or a kill criterion fails; the first failing bar is named, and KILL is added when a kill criterion fired. UNDERPOWERED = bar 1 fails (reads as UNTESTED, never as proof of no edge). Flags that can accompany: FRAGILE (bar 7), MULTIPLICITY-FLAGGED (Holm). Descriptive-only rows (the STOP row on its own, tag means, old + fresh pooled, funding-only and no-funding variants, per-coin, per-year, brain cycle and phase label) never give a verdict by themselves, except the STOP row inside kill criterion (b). Any PASS stops the line: a blind review and a testnet-forward card need the operator's go.

## Seen results on the source coins (do not tune against them)

Source 22 coins, 12 bp, spot, no funding: DEV +3.0% (n 213); VAL 2022+ +2.6% (n 391), week-cluster CI low -0.2%, placebo p 0.053, mean without best 3 weeks +1.3%; XS stop row +0.24 R (a different stop). Nothing in this PRE_REG was changed after reading them; the 8-week window, the 0.80 factor, the cooldown and the exit are copied.

## Known weaknesses (before the run)

- Weeks, not trades, are the sample: coins fall together, so one crash week fires many coins; expect few effective clusters and a wide CI.
- No stop on the primary row: a 14-day hold in a falling market can lose a lot; the secondary stop row is a different strategy (OURS), not the source row.
- Survivorship: hindsight candidate list, and collapsed coins exit at a close that may not have been tradable (see above).
- Fresh coins are out of sample by coin only; the calendar weeks are the same as the source coins, so a market-wide episode counts twice if both sets are pooled.
- Spot price stands in for a perp; the funding charge is real where cached and a flat OURS assumption elsewhere; no fill model, no borrow, no liquidity limit for small coins.
- The 60-week keep rule, the 2.5 ATR stop, the flat funding and the DELIST-EXIT handling are OURS.
- Underpowered by the gate below when counted in independent weeks.

## Power gate

Inputs and where they come from:
- n 60 = expected number of independent units, i.e. VAL ISO entry weeks with a fresh event (OURS estimate, not measured: the source had 391 VAL trades but only a few dozen independent calendar weeks, source RESULT.md "effective sample is a few dozen independent weeks"; the fresh basket has about twice the coins and the same calendar, so 60 is a generous count of weeks).
- sd 1.2 R = two-point estimate of the sd of one week-unit in R (OURS, unmeasured): the source VAL mean +2.6% with CI low -0.2% gives a standard error of about 1.4% (half-width 2.8% / 1.96); in R units with a risk unit of about 12% (2.5 ATR14 on a coin, design note "typically 10-15%") that is 0.12 R, times sqrt(about 70 week clusters) is about 1.0 to 1.2 R. Reference: edge9 RESULT.md table row "DD20 E1 X2" (notes folder). The sd is measured for real in RESULT.
- cost 0.01 R = 12 bp / about 12% risk unit (design note: "0.01 R"); funding adds up to 42 bp on the flat rule, about 0.035 R, not in the gate cost.
- m 3 = the wave family.

Command and output (run in the worktree, exit code 1):

    python scripts/dev/prereg_gate.py --n 60 --sd 1.2 --cost 0.01 --m 3 --sd-source "EDGE_WAVE2_DESIGN_1114.md T6 column; edge9 RESULT.md DD20 E1 X2 row"
    n 60 sd 1.2 m 3 z_holm 2.394 MDE 0.501 R + cost 0.01 = 0.511 vs max plausible gross 0.3; n needed 179
    BLOCK: do not freeze (write BLOCKED.md with these numbers)

For information, the same sd with n 391 (raw trades, which are NOT independent) gives "MDE 0.196 R + cost 0.01 = 0.206 ... PASS: may freeze"; that count is the wrong unit and is not used for the decision.
Decision (OURS): BLOCK stated. The run goes ahead because the operator ordered the wave on 2026-11-14 (no BLOCKED.md is written for that reason). A FAIL or UNDERPOWERED result is read as UNTESTED at this power, never as proof of no edge. A PASS would still need the blind review.

## Protocol

1. This PRE_REG is committed alone before any code or outcome.
2. Code stage: `t6_lib.py`, `t6_trades.py`, `t6_stats.py` (unique `t6_` prefix) and synthetic-bar tests `test_t6_*.py` (look-ahead, cooldown, funding window and flat fallback, stop-wins-ties, fee arithmetic from `fees.py`, planted edge) are committed; tests never read the data cache. A mutation check shows the tests fail on a planted bug.
3. Step A: `t6_trades.py` writes the trade list (coin, event week, entry, exit, gross, fee, funding, tags) with NO pooled statistic.
4. Step B: an independent recompute of 3 dated trades from raw klines and FORMULAS.md (ATR Wilder), plus an adversarial look-ahead / fee / funding audit, on that list.
5. Step C: only if both are clean, `t6_stats.py` computes the pass bars, RESULT.md, and the notes file T6_RESULT_1114.md. A final checker re-derives the verdict from the summary numbers against these bars.
6. A found mechanical bug is fixed and logged in RESULT; rules and parameters are never changed after step A.

## Ambiguities in the source text and the reading frozen

- "Within 8 weeks" cooldown: study.py allows a new event at a gap of exactly 8 weeks (`>= 8`); frozen as in the code.
- BULL/BEAR "prior completed week": the source code compares the event week's own close with the mean of the 50 weekly closes ending at that week; frozen as in the code (that week is the last completed week before entry).
- Split "by signal bar" vs source "entry date": the same instant here, so no difference.
- Funding window boundary and flat rule: new here, frozen above (entry-instant print excluded, exit-day-end print included).
- Data-end handling for delisted coins: new here (DELIST-EXIT).
