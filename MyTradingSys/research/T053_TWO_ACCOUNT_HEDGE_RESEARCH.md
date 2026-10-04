# T053 - TWO-ACCOUNT HEDGE / LEVERAGED BTC SCALPING RESEARCH
Session: MTS-2026-10-04-1010Z-APP-ANA-t053-hedge-research
Row: BUILD_PIPELINE 6.1. Doc-only. No code, no backtest run. Date: 2026-10-04.
Item: items/T053_two_account_hedge_scalping.md (options a, b1, b2).

## 1. METHOD NOTE (before searching)
Question: does a two-account hedge loop (a: hedge after fee-cover threshold; b1: hedge on a condition such as
outside-Bollinger or divergence; b2: open a new opposite position on that condition) have positive expectancy
after costs on BTC perpetuals?
Evidence that would settle it: our own 1m backtest (verdict.py + PBO), walk-forward out-of-sample, at least
12 months spanning trend and range regimes, per-trade net of taker/maker fees, funding and slippage, with the
hedged and unhedged variants run on identical entries. External sources can only rank what to test first.
No accepted external method exists for "hedged scalping loop expectancy" -> that sub-question is an
unvalidated domain (see F5).

## 2. SOURCE TIERS (committed before searching; Playbook Part I table, unchanged)
T1 peer-reviewed / NBER / BIS; T2 exchange docs, SSRN/arXiv with method; T3 practitioner content;
REJECT marketing, no method, profit claims without costs, any citation that cannot be opened and matched.
Planned searches: Binance hedge-mode docs (T2), Deribit docs/fees (T2), perpetual pricing theory (T1),
crypto carry / funding (T1), technical-rule profitability in BTC after costs (T1/T2), practitioner hedge loops (T3).

## 3. FINDINGS (Tier | method quality | confidence)
F1. Binance USD-M supports hedge mode: long and short simultaneously on the same contract in ONE account;
    position mode cannot be switched while positions or orders are open.
    T2 (exchange docs) | docs, no fee detail in page | H.
    Source: https://www.binance.com/en/support/faq/what-is-hedge-mode-and-how-to-use-it-360041513552
    Title "What Is Hedge Mode and How to Use It?" - verified 2026-10-04 (opened, claim in page).
    Consequence: on Binance the "two accounts" requirement is not needed to hold both sides; it only matters
    for separate margin/liquidation isolation.
F2. Deribit: positions can be moved between subaccounts of one main account, no fee for moves, max 100
    move_positions calls per week, destination needs margin. T2 | docs | H.
    Source: https://docs.deribit.com/articles/moving-positions-api - "Moving Positions on Deribit" - verified 2026-10-04.
    Consequence: a subaccount hedge pair is feasible; the weekly move cap rules out move-based loops.
    NOT verified: the T053 note that Deribit holds one net position per instrument per account; no opened
    source stated it. Treat as unverified (Q3).
F3. Perpetual price is anchored to spot by funding payments from long to short (replicable by dynamic trading).
    T1 | theory, no trading test | H for mechanism, nothing for profitability.
    Ackerer, Hugonnier, Jermann, "Perpetual Futures Pricing", NBER WP 32936, Sept 2024; Mathematical Finance
    36(3) 481-499, 2026. Source: https://www.nber.org/papers/w32936 - verified 2026-10-04 (abstract only; the
    journal volume/pages are as stated on that NBER page; the Wiley page returned 403 and was not opened).
    Consequence: a long+short pair has funding that nets to about zero only if sizes and venue match;
    two venues or unequal sizes leave a funding residual to model.
F4. Crypto carry averages above 10% a year, driven by small trend-chasing leveraged investors and scarce
    arbitrage capital; high carry predicts crashes. T1 (BIS) | multi-year cross-exchange panel, not a
    scalping test | M.
    Schmeling, Schrimpf, Todorov, "Crypto Carry", BIS Working Paper 1087, 2023-04-04.
    Source: https://www.bis.org/publications/working-paper-1087-crypto-carry - verified 2026-10-04.
    Consequence: funding is a first-order cost on the crowded side; holding the long leg through high-carry
    periods pays it. Funding must be in the backtest, not an afterthought.
F5. Technical-rule / hedge-loop profitability on BTC after costs: No validated evidence found.
    One opened source (abstract only): Manahov, "The rapid growth of cryptocurrencies: How profitable is
    trading in digital money?", Int. J. Finance & Economics 29(2), Apr 2024, 2214-2229, reports profits after
    "reasonable" costs in high-frequency data but weaker persistence post-Covid. T1 venue | method detail not
    read, cost level not seen | L. Source: https://ideas.repec.org/a/wly/ijfiec/v29y2024i2p2214-2229.html
    - verified 2026-10-04 (abstract only). Not a hedge study; do not cite as support.
D1. Our own arithmetic (derivation, NOT evidence; needs a FORMULAS.md entry with source before any spec).
    Fee cover for option a: entry and exit on each leg = 4 sides. Using backtest/fees.py:
    Deribit taker 5 bps/side -> 20 bps for 4 taker sides; Deribit maker 0 -> 0.
    Binance taker 5 bps, maker 2 bps/side -> 20 bps taker, 8 bps maker for 4 sides.
    So the favourable move y must exceed roughly 8-20 bps of price (at 100k BTC, 80-200 USD) before
    slippage and funding, to be fee-neutral.
    Structural point: an equal-size long+short is delta-neutral. Hedging locks the open PnL; it does not add
    expectancy, and costs extra fees and funding for the lock. Profit comes only from WHEN the hedge leg is
    lifted, a directional timing decision (the b1/b2 conditions), not from the hedge itself.
    Proposed test order: (1) unhedged baseline on the same entries; (2) option a, threshold grid at
    fee-cover multiples; (3) b1 with Tom-sourced conditions only; (4) b2. Any threshold needs a trader-source
    quote or is flagged NO-SOURCE (provenance rule); fee-cover is exchange arithmetic, not a trader parameter.

## 4. REJECT LIST (do not research again)
- Froemmel and Deprez 2024 "Are Simple Technical Trading Rules Profitable in Bitcoin Markets?" - search
  snippet only; ScienceDirect and SSRN returned 403, could not be opened and matched.
- Medium/Coinrule/Cornix/Utrading/HafizeBot hedge-mode pages - vendor/blog content, no method or costs,
  seen only as search titles, not opened.
- Practitioner "two account hedge" profit claims in general - none found with costs and sample; none used.
- Deribit fee pages (milkroad, tradersunion, gncrypto) - affiliate/review sites. Fee numbers rest on
  backtest/fees.py (API check 2026-09-26); deribit.com/kb/fees fetch returned no amounts.

## 5. OPEN QUESTIONS FOR THE OPERATOR
Q1. Venue: Binance hedge mode (one account, both sides) or two Deribit test subaccounts? CLAUDE.md allows
    testnet only for live, so Binance would be backtest-only on Binance fees. Confirm.
Q2. Is the goal expectancy from the hedge, or margin isolation between two accounts? F1 and D1 say the
    hedge alone adds no expectancy.
Q3. Confirm Deribit net-position-per-instrument behaviour via a public docs page or API check (the T053
    note was not verified here).
Q4. Which Tom-sourced conditions may serve as b1/b2 triggers? Bollinger and DVD divergence are not Tom
    layers; they would be a separate layer with its own source.
Q5. Approve the test order in D1 and a 12-month 1m data window for the T053 backtest.
