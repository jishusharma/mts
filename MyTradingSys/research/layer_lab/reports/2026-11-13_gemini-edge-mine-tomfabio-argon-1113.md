# Report: Tom & Fabio 15 Rules Mining (Argon Twin)

Date: 2026-11-13 (UTC)
Task: `gemini-edge-mine-tomfabio-argon-1113`
Worker: `gemini-3.8-flash-low`
Output artifact: `MyTradingSys/research/layer_lab/gemini_edge_1113/mine-tomfabio-argon/RULES.md`

## 1. Summary of Work Done

In accordance with task card `gemini-edge-mine-tomfabio-argon-1113`, 15 mechanically testable rules were extracted from the Tom Vorwald and Fabio Valentini source extractions (`extracts/v2/tom/` and `extracts/v2/fabio/`). Each rule follows the exact required shape: indicator at a measured extreme + confirming candle + stop, with exact parameters and verbatim quotes.

Parameters not stated in the source text were marked `NOT_STATED` (never invented).
All verbatim quotes and `Source GPS: <id> | BEGIN|MIDDLE|END` tags were verified using `scripts/dev/verify_extract_quotes.py`.

## 2. Verification Gate Output

Command run:
```bash
python scripts/dev/verify_extract_quotes.py MyTradingSys/research/layer_lab/gemini_edge_1113/mine-tomfabio-argon/RULES.md
```

Verification output:
```
OK       RULES.md:13 (1 cite(s))
OK       RULES.md:14 (1 cite(s))
OK       RULES.md:15 (1 cite(s))
OK       RULES.md:16 (1 cite(s))
OK       RULES.md:17 (1 cite(s))
OK       RULES.md:18 (1 cite(s))
OK       RULES.md:19 (1 cite(s))
OK       RULES.md:20 (1 cite(s))
OK       RULES.md:21 (1 cite(s))
OK       RULES.md:22 (1 cite(s))
OK       RULES.md:23 (1 cite(s))
OK       RULES.md:24 (1 cite(s))
OK       RULES.md:25 (1 cite(s))
OK       RULES.md:26 (1 cite(s))
OK       RULES.md:27 (1 cite(s))
OK       RULES.md:34
OK       RULES.md:36 (1 cite(s))
OK       RULES.md:39
OK       RULES.md:41 (1 cite(s))
OK       RULES.md:44
OK       RULES.md:46 (1 cite(s))
OK       RULES.md:49
OK       RULES.md:51 (1 cite(s))
OK       RULES.md:54
OK       RULES.md:56 (1 cite(s))
OK       RULES.md:59
OK       RULES.md:61 (1 cite(s))
OK       RULES.md:64
OK       RULES.md:66 (1 cite(s))
OK       RULES.md:69
OK       RULES.md:71 (1 cite(s))
OK       RULES.md:74
OK       RULES.md:76 (1 cite(s))
OK       RULES.md:79
OK       RULES.md:81 (1 cite(s))
OK       RULES.md:84
OK       RULES.md:86 (1 cite(s))
OK       RULES.md:89
OK       RULES.md:91 (1 cite(s))
OK       RULES.md:94
OK       RULES.md:96 (1 cite(s))
OK       RULES.md:99
OK       RULES.md:101 (1 cite(s))
OK       RULES.md:104
OK       RULES.md:106 (1 cite(s))
PASS: 0 problem(s)
```

## 3. Top 5 Rules Ranked by Fewest NOT_STATED Fields

All rules were evaluated across the 7 execution parameters (Indicator, Extreme Threshold, Confirming Candle, Entry, Stop, Exit, Timeframe):

1. **TF-ARG-14**: Tom S&P Pre-Session 7443 Limit Buy (`extracts/v2/tom/QClPWDJ-BrU_v2.md:98`) — 0 `NOT_STATED` (all 7 parameters specified: entry 7443, stop 7420, target 7513, pre-session).
2. **TF-ARG-10**: Tom Daily Profile Invalidation Footprint Entry (`extracts/v2/tom/3o1VVsfBmmU_v2.md:132`) — 0 `NOT_STATED` (all 7 parameters specified: stop 10 ticks, profit run 70 ticks, daily/footprint).
3. **TF-ARG-01**: Fabio Initial Balance Volatility Contraction Breakout (`extracts/v2/fabio/StaphlRH8NQ_v2.md:198`) — 0 `NOT_STATED` (all 7 parameters specified: 30m IB breakout, 1:1 risk/reward target, daily cash session).
4. **TF-ARG-02**: Fabio Initial Balance VA-to-POC Retest Long (`extracts/v2/fabio/cUTsoU-15Tc_v2.md:28`) — 0 `NOT_STATED` (all 7 parameters specified: 15-30m profile, close below VAL invalidation, protection level target).
5. **TF-ARG-03**: Fabio IB Buyer Protection Long (`extracts/v2/fabio/cUTsoU-15Tc_v2.md:46`) — 0 `NOT_STATED` (all 7 parameters specified: stop below protected area, target protection level, NY session).
