# FlowHorse Positioning: Ledger Feasibility Audit (Gates 0c and 0d)

Date: 2026-10-18. Card: positioning-flowhorse-ledger-feasibility. Weight: ROUTINE.
Sources: extracts/processed/flowhorse/ (3 extracts), extracts/fresh/ (2 raw transcripts), MyTradingSys/research/fast_track_2026-09-27/CROSS_TRADER_RULEBOOK.md (rules FHR-19 to FHR-26), MyTradingSys/research/tom_transfer_2026-10-11/HOME_FIT_AUDIT_POSITIONING.md, MyTradingSys/backtest/PRE_REG_TEMPLATE.md.
Gate 0c mandate: "does the source have dated calls or trades we can score on BTC data? Score them first ... No record: hypothesis, never a core" [SOURCED: MyTradingSys/backtest/PRE_REG_TEMPLATE.md:14].
Gate 0d mandate: "does BTC history hold every input the source reads? A missing input is NOT_IN_DATA; nothing is built on it" [SOURCED: MyTradingSys/backtest/PRE_REG_TEMPLATE.md:15].
No backtest run; read-only scan and feasibility check.

## Summary Counts

- FlowHorse sources scanned: 5 sources [OURS: 3 processed extracts + 2 raw transcripts].
- Total rules extracted in processed files: 19 rules [SOURCED: extracts/processed/flowhorse/extract_Oy2Z-FQ77NM.md:11,110 (11 rules); extracts/processed/flowhorse/extract_UcPp0gFI5M8.md:13 (0 actionable rules); extracts/processed/flowhorse/extract_zMM9QgxfEFI.md:11,79 (8 rules); cross-check: MyTradingSys/research/fast_track_2026-09-27/CROSS_TRADER_RULEBOOK.md:121 "19 + 4 principles + 2 transcripts"].
- Dated BTC trades or calls found: 0 [OURS: zero dated trades or calls on BTC across all 5 sources].
- Undated BTC trade descriptions: 1 event [SOURCED: extracts/fresh/extract_UrnES-HzQ6w_the_flow_horse.txt:116, 578-583 (post-100k cascade trade described with relative timestamps "last night", no calendar date, no fill log)].
- Dated non-BTC trade executions: 7 intraday executions/scratches on ETH [SOURCED: extracts/fresh/extract_izZyd-HrTSE_the_flow_horse.txt:11, 16-20 (traded ETH on 2022-09-02; explicitly states "bitcoin sucks")].
- Total events listed: 8 event descriptions [OURS: 1 BTC cascade narrative + 7 ETH intraday trades/episodes].
- Total SCOREABLE events on BTC: 0 [OURS: zero events scoreable on BTC data].
- Total NOT_SCOREABLE events: 8 [OURS: 8 events marked NOT_SCOREABLE].
- Minute timestamps possible: NO [OURS: no trade ticket, fill log, or minute timestamp exists].
- Design/check split possible: NO [OURS: 0 scoreable records cannot be split into design and check sets].
- Verdict: HYPOTHESIS [OURS: FlowHorse positioning fails Gate 0c and Gate 0d, remains a hypothesis].

## Source Scan Breakdown

1. `extracts/processed/flowhorse/extract_Oy2Z-FQ77NM.md`
   - Title: "The Flow Horse — Most Traders Misread Volume Profile" [SOURCED: extracts/processed/flowhorse/extract_Oy2Z-FQ77NM.md:1].
   - Duration: 20:47 [SOURCED: extracts/processed/flowhorse/extract_Oy2Z-FQ77NM.md:4]. Extracted: 2026-08-29 [SOURCED: extracts/processed/flowhorse/extract_Oy2Z-FQ77NM.md:5].
   - Rules: 11 rules (Rules 1-11) [SOURCED: extracts/processed/flowhorse/extract_Oy2Z-FQ77NM.md:11, 110].
   - Mentions positioning decay: "If it took place 5, 15 minutes ago, a session ago even, it's probably still more relevant" [SOURCED: extracts/processed/flowhorse/extract_Oy2Z-FQ77NM.md:23].
   - Dated trades/calls: 0 [OURS: pure conceptual educational extract; zero trade executions or calls].

2. `extracts/processed/flowhorse/extract_UcPp0gFI5M8.md`
   - Title: "The Flow Horse — Market Profile: Course Introduction" [SOURCED: extracts/processed/flowhorse/extract_UcPp0gFI5M8.md:1-2].
   - Duration: 5:18 [SOURCED: extracts/processed/flowhorse/extract_UcPp0gFI5M8.md:3]. Extracted: 2026-08-29 [SOURCED: extracts/processed/flowhorse/extract_UcPp0gFI5M8.md:5].
   - Rules: 0 actionable rules [SOURCED: extracts/processed/flowhorse/extract_UcPp0gFI5M8.md:13 "RULES EXTRACTED: 0 actionable rules"].
   - Dated trades/calls: 0 [OURS: syllabus overview; zero trade executions or calls].

3. `extracts/processed/flowhorse/extract_zMM9QgxfEFI.md`
   - Title: "The Flow Horse — The Bitcoin Setup Changed" [SOURCED: extracts/processed/flowhorse/extract_zMM9QgxfEFI.md:1-2].
   - Duration: 15:45 [SOURCED: extracts/processed/flowhorse/extract_zMM9QgxfEFI.md:4]. Extracted: 2026-08-29 [SOURCED: extracts/processed/flowhorse/extract_zMM9QgxfEFI.md:5].
   - Rules: 8 rules (Rules 1-8) [SOURCED: extracts/processed/flowhorse/extract_zMM9QgxfEFI.md:11, 79].
   - Mentions absorption of large seller ("Sailor was a massive seller... and yet Bitcoin able to hold") [SOURCED: extracts/processed/flowhorse/extract_zMM9QgxfEFI.md:80], but provides no trade execution date, fill price, or order record.
   - Dated trades/calls: 0 [OURS: high-level market commentary; zero trade executions or calls].

4. `extracts/fresh/extract_UrnES-HzQ6w_the_flow_horse.txt`
   - Title: "The Flow Horse — THE BEST TRADE SETUP IN CRYPTO: Liquidation Cascades" [SOURCED: extracts/fresh/extract_UrnES-HzQ6w_the_flow_horse.txt:1].
   - Duration: 22:00 [SOURCED: extracts/fresh/extract_UrnES-HzQ6w_the_flow_horse.txt:4]. Downloaded: 2026-08-29 [SOURCED: extracts/fresh/extract_UrnES-HzQ6w_the_flow_horse.txt:5].
   - Content: Retrospective narrative of a BTC liquidation cascade trade after breaking 100K down to 90k [SOURCED: extracts/fresh/extract_UrnES-HzQ6w_the_flow_horse.txt:122, 256, 541].
   - Mentions: "this is last night" [SOURCED: extracts/fresh/extract_UrnES-HzQ6w_the_flow_horse.txt:116] and "yesterday" [SOURCED: extracts/fresh/extract_UrnES-HzQ6w_the_flow_horse.txt:471]. No calendar date (year/month/day) and no minute timestamp are stated.
   - Stop and sizing: Missing / discretionary ("stink bids across exchanges that were filled ... add more in manually after") [SOURCED: extracts/fresh/extract_UrnES-HzQ6w_the_flow_horse.txt:657-660]. Confirmed by CROSS_TRADER_RULEBOOK: "no stop or invalidation is given ... size not given" [SOURCED: MyTradingSys/research/fast_track_2026-09-27/CROSS_TRADER_RULEBOOK.md:113].

5. `extracts/fresh/extract_izZyd-HrTSE_the_flow_horse.txt`
   - Title: "The Flow Horse — How I Trade News Catalysts in Crypto - Non Farm Payroll Big Profit Day (ACTUAL LIVE VIDEO)" [SOURCED: extracts/fresh/extract_izZyd-HrTSE_the_flow_horse.txt:1].
   - Duration: 47:51 [SOURCED: extracts/fresh/extract_izZyd-HrTSE_the_flow_horse.txt:4]. Downloaded: 2026-08-29 [SOURCED: extracts/fresh/extract_izZyd-HrTSE_the_flow_horse.txt:5].
   - Event date: "september 2nd non-farm payroll day ... labor day weekend here in the united states" [SOURCED: extracts/fresh/extract_izZyd-HrTSE_the_flow_horse.txt:11, 28-29]. Deductions: Non-Farm Payrolls Friday immediately preceding US Labor Day on September 2nd corresponds to 2022-09-02 [OURS: calendar alignment; consensus 295k vs actual 315k sourced at line :418]. Release timestamp is 08:30:00 AM EDT (12:30:00 UTC) [SOURCED: extracts/fresh/extract_izZyd-HrTSE_the_flow_horse.txt:812-814].
   - Asset traded: Explicitly ETH (Ethereum), NOT BTC ("i've kept it consistent i've been trading eth now for over a month primarily bitcoin sucks for now maybe or maybe forever who knows i don't really care") [SOURCED: extracts/fresh/extract_izZyd-HrTSE_the_flow_horse.txt:16-20]. "i'm trading eth i enter right here i exit right here" [SOURCED: extracts/fresh/extract_izZyd-HrTSE_the_flow_horse.txt:408]. "now mind you i was trading eth even though we have a btc chart here" [SOURCED: extracts/fresh/extract_izZyd-HrTSE_the_flow_horse.txt:728].
   - Executes 7 intraday discretionary scalps/episodes on ETH, none on BTC.

## Listed events

Every event described in the 5 sources is catalogued below:

| # | Source File:Line | Video Date / Stated Date | Stated Timestamp | Instrument | Side | Stated Details / Verbatim Quote | Feasibility Status |
|---|---|---|---|---|---|---|---|
| 1 | extracts/fresh/extract_UrnES-HzQ6w_the_flow_horse.txt:578-583 | Unstated ("last night" / "yesterday") | Unstated (relative: "after 3 minutes of movement", "first green candle") | BTC | LONG | "all you need to do is is see things temporarily pause and then the first green candle that I get I get long under the impression that this is going to move back to the point of origin" [SOURCED: extracts/fresh/extract_UrnES-HzQ6w_the_flow_horse.txt:578-583] | NOT_SCOREABLE |
| 2 | extracts/fresh/extract_izZyd-HrTSE_the_flow_horse.txt:809-814 | 2022-09-02 (deduced from NFP Sept 2 Friday before Labor Day) | 08:30:01 AM EDT (12:30:01 UTC) | ETH | LONG | "that's the release okay that's my entry right there now that is at this is 8 30 in the morning one second after just beyond one second" [SOURCED: extracts/fresh/extract_izZyd-HrTSE_the_flow_horse.txt:809-814]; "i'm trading eth" [SOURCED: extracts/fresh/extract_izZyd-HrTSE_the_flow_horse.txt:408] | NOT_SCOREABLE |
| 3 | extracts/fresh/extract_izZyd-HrTSE_the_flow_horse.txt:414-415 | 2022-09-02 | Unstated (~08:31-08:32 EDT) | ETH | LONG | "i let things play out i end up taking another long over here" [SOURCED: extracts/fresh/extract_izZyd-HrTSE_the_flow_horse.txt:414-415] | NOT_SCOREABLE |
| 4 | extracts/fresh/extract_izZyd-HrTSE_the_flow_horse.txt:450-451 | 2022-09-02 | Unstated (~08:33-08:35 EDT) | ETH | SHORT | "i think i got chopped up a little bit over here and ended up shorting this back down ... smaller short it's around half the size of this initial long" [SOURCED: extracts/fresh/extract_izZyd-HrTSE_the_flow_horse.txt:450-451, 1011-1012] | NOT_SCOREABLE |
| 5 | extracts/fresh/extract_izZyd-HrTSE_the_flow_horse.txt:470-472 | 2022-09-02 | Unstated (~08:35-08:40 EDT) | ETH | LONG | "reclaimed the the high of value ... i end up looking for the long right around here ... arrow is pointing up" [SOURCED: extracts/fresh/extract_izZyd-HrTSE_the_flow_horse.txt:464-472, 1152-1156] | NOT_SCOREABLE |
| 6 | extracts/fresh/extract_izZyd-HrTSE_the_flow_horse.txt:1200-1204 | 2022-09-02 | Unstated | ETH | SHORT | "first larger short so that's scratched out because you can see i went to short it scratched immediately when it doesn't work" [SOURCED: extracts/fresh/extract_izZyd-HrTSE_the_flow_horse.txt:1200-1204] | NOT_SCOREABLE |
| 7 | extracts/fresh/extract_izZyd-HrTSE_the_flow_horse.txt:1209-1212 | 2022-09-02 | Unstated | ETH | SHORT | "little consolidation volume is stuck above the highs ... and i'm short right there so you could see the last arrow pointing down" [SOURCED: extracts/fresh/extract_izZyd-HrTSE_the_flow_horse.txt:1207-1212] | NOT_SCOREABLE |
| 8 | extracts/fresh/extract_izZyd-HrTSE_the_flow_horse.txt:1301-1315 | 2022-09-02 | Unstated (post-NFP afternoon session) | ETH | SHORT | "this is where i hammered short we had a break of market structure ... gazprom news couldn't have came at a better time ... adding i'm covering i'm adding i'm covering on pops i'm adding into the break" [SOURCED: extracts/fresh/extract_izZyd-HrTSE_the_flow_horse.txt:1301-1315, 1343-1345] | NOT_SCOREABLE |

## Why Each Event is NOT_SCOREABLE on BTC Data

1. Event 1 (UrnES-HzQ6w: BTC cascade trade):
   - Missing calendar date: The video states only "this is last night" [SOURCED: extracts/fresh/extract_UrnES-HzQ6w_the_flow_horse.txt:116]. No year, month, or day is provided in the file.
   - Missing minute timestamps: No execution timestamp, fill log, or order price is recorded.
   - Missing stop and sizing: The trader uses stink bids and manual additions [SOURCED: extracts/fresh/extract_UrnES-HzQ6w_the_flow_horse.txt:657-660; CROSS_TRADER_RULEBOOK.md:113].
   - Required inputs are NOT_IN_DATA: The cascade setup (FHR-19 to FHR-23) relies on liquidation wipe volume, tick/L2 footprint zero-prints, and multi-exchange basis dislocation [SOURCED: MyTradingSys/research/fast_track_2026-09-27/CROSS_TRADER_RULEBOOK.md:84-88]. The repo possesses no liquidation history (only a live socket keeping $100 price buckets), no tick feed, and no L2 orderbook history [SOURCED: src/main/java/datafeed/BinanceLiquidationAccumulator.java:14-15, 31; HOME_FIT_AUDIT_POSITIONING.md:47-48].

2. Events 2 to 8 (izZyd-HrTSE: NFP session trades):
   - Wrong instrument: FlowHorse explicitly and repeatedly states he traded ETH (Ethereum), NOT BTC [SOURCED: extracts/fresh/extract_izZyd-HrTSE_the_flow_horse.txt:16-20, 408, 728]. For BTC on this day he stated "bitcoin sucks" [SOURCED: extracts/fresh/extract_izZyd-HrTSE_the_flow_horse.txt:19] and "btc and ether still stuck within" [SOURCED: extracts/fresh/extract_izZyd-HrTSE_the_flow_horse.txt:825-826]. Gate 0c specifically asks whether dated trades can be scored on BTC data; an ETH discretionary tape-reading day cannot be scored as a BTC trade ledger.
   - Sub-minute execution speed: Event 2 was entered 1 second after release (08:30:01 EDT) and exited 15-30 seconds later into the ask [SOURCED: extracts/fresh/extract_izZyd-HrTSE_the_flow_horse.txt:812-814, 901-902, 964-966]. This intra-second execution cannot be scored on 1-minute BTC klines without orderbook depth and latency feeds.
   - Missing execution log: Events 3-8 have no minute timestamps, no exact fills, and constitute discretionary scalping/scratching with oatmeal breaks [SOURCED: extracts/fresh/extract_izZyd-HrTSE_the_flow_horse.txt:1198].
   - Required inputs NOT_IN_DATA for 2022-09-02:
     - Open interest (OI 5m) in the repo covers only 2025-09-01..2026-09-26 [SOURCED: MyTradingSys/research/PRE_REG_OI_DIVERGENCE_2026-10-10.md:10-11; HOME_FIT_AUDIT_POSITIONING.md:47]. On 2022-09-02, OI is completely NOT_IN_DATA.
     - Live S&P equity-index jump feed (SPX), tape speed, and L2 spreads are NOT_IN_DATA.

## Data Feasibility Check (Step 2)

| Data Type | Repo Coverage | FlowHorse Setup Requirement | Feasibility Verdict |
|---|---|---|---|
| BTC 1m klines | 2022-01..2026-09 [SOURCED: MyTradingSys/backtest/vp_pivot_probe.py:46; HOME_FIT_AUDIT_POSITIONING.md:87] | FHR-20, FHR-23, FHR-29 | Present for BTC, but FlowHorse traded ETH on 2022-09-02 and gave no dates for BTC cascade |
| BTC OI 5m | 2025-09-01..2026-09-26 [SOURCED: MyTradingSys/research/PRE_REG_OI_DIVERGENCE_2026-10-10.md:10-11; HOME_FIT_AUDIT_POSITIONING.md:47] | FHR-19, FHR-21 ("sharp OI jump in a short time") | NOT_IN_DATA for 2022-09-02 (zero coverage before 2025-09) |
| Liquidation history | None (live forceOrder socket only with $100 price buckets) [SOURCED: src/main/java/datafeed/BinanceLiquidationAccumulator.java:14-15, 31; HOME_FIT_AUDIT_POSITIONING.md:47-48] | FHR-19 ("record liquidation/OI wipe with a blown-out low") | NOT_IN_DATA |
| Tick & L2 orderbook | None (repo has klines and live feeds, no historic L2/tick) [SOURCED: HOME_FIT_AUDIT_POSITIONING.md:47-48; CROSS_TRADER_RULEBOOK.md:115] | FHR-22 ("spreads blown out, basis dislocated"), FHR-24, FHR-31 | NOT_IN_DATA |
| Real-time SPX feed | None [SOURCED: CROSS_TRADER_RULEBOOK.md:89] | FHR-24 ("market in on the direction of equity-index jump") | NOT_IN_DATA |
| ETH 1m klines | None (repo backtest data is BTCUSDT only) [SOURCED: MyTradingSys/backtest/vp_pivot_probe.py:46] | Required for the 2022-09-02 live video trades | NOT_IN_DATA |

## Answers to Card Questions (Step 3)

1. N found:
   - 0 dated BTC trades or calls found [OURS].
   - 1 undated BTC retrospective cascade description [SOURCED: extracts/fresh/extract_UrnES-HzQ6w_the_flow_horse.txt:116, 578-583].
   - 7 dated non-BTC (ETH) discretionary intraday trades/scratches [SOURCED: extracts/fresh/extract_izZyd-HrTSE_the_flow_horse.txt:11, 16-20].
   - 0 scoreable events on BTC data [OURS].

2. Minute timestamps possible or not:
   - **NO**. Neither transcript contains an execution ticket log or minute-stamped trade record. The NFP video names only 08:30:01 AM EDT for an ETH trade, and the cascade video provides only relative elapsed minutes ("3 minutes of movement", "first green candle") with no calendar date.

3. Design/check split possible or not:
   - **NO**. Zero scoreable events cannot be divided into design and check sets. Gate 0c requires a split ground-truth trade ledger before any rule encoding is tested.

4. Ledger CSV:
   - **NOT WRITTEN**. Because 0 scoreable BTC events exist, no ledger CSV can be constructed.

## Consequence for Positioning Layer

FlowHorse positioning (FHR-19 to FHR-26: liquidation cascade, OI sharp pickup, news event second move) cannot be tested against a trader ground truth. It fails Gate 0c (no scorable trade/call record) and Gate 0d (liquidation history, tick/L2, and historical OI are NOT_IN_DATA).

Per Gate 0c of PRE_REG_TEMPLATE.md:14:
> "No record: hypothesis, never a core."

Therefore, FlowHorse positioning stays a **HYPOTHESIS**.
It must not be promoted or treated as a core layer.
Any future work on FlowHorse positioning rules would require:
1. Operator provision of dated BTC trade calls with timestamped entries and exits.
2. Sourcing of historical liquidation and orderflow/tick datasets not currently present in the MTS repository.

Verdict: HYPOTHESIS
