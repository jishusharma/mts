# Audit of COMPARE.md s1 'Where all four agree' table: MATCH 6, DIFF 0, NOT_IN_DATA 0 (sum 6)

## Clause-by-Clause Verification

### Clause 1
- **Row in COMPARE.md s1**: `No trade type has a passing result after fees | 0 of 15 trials passed (edge_hunt_2026-11-09/EDGE_TABLE.md:3)`
- **Verdict**: MATCH
- **Source Verification (file:line)**:
  - SOURCED: `MyTradingSys/research/edge_hunt_2026-11-09/EDGE_TABLE.md:3`: `"No trial passed. 8 FAIL, 5 INCONCLUSIVE, 2 not run as frozen trials (T07, T08)."`
- **Review Verification (file:line)**:
  - OPUS: `MyTradingSys/research/four_model_review_2026-11-11/OPUS.md:5`: `"Bottom line: nothing is a proven fee-net edge (STATUS.md:7 "0 of 40 fee-net rows carry a surviving PASS")."`
  - SONNET: `MyTradingSys/research/four_model_review_2026-11-11/SONNET.md:25`: `"edge hunt 15 trials: 0 pass, 8 FAIL, 5 INCONCLUSIVE (T04 n 1,150 -0.221 R; T11 n 1,588 -0.146 R)"` & `SONNET.md:28`: `"Nothing has a PASS (ST:7 "0 of 40"; EH:3 "No trial passed")."`
  - HAIKU: `MyTradingSys/research/four_model_review_2026-11-11/HAIKU.md:12`: `"0 of 40 fee-net rows carry a surviving PASS"` & `HAIKU.md:42`: `"Summary: nothing in the list passes a fee-net out-of-sample test."`
  - SUPERVISOR: `MyTradingSys/research/four_model_review_2026-11-11/SUPERVISOR.md:30`: `"0 of 15 trials passed"`

---

### Clause 2
- **Row in COMPARE.md s1**: `Fading a level (Tom/Fabio sweep and reclaim, the thing Live Aid flashes) loses | -0.106 R, n 1,484; 7y 1h -0.087 R, n 1,871`
- **Verdict**: MATCH
- **Source Verification (file:line)**:
  - SOURCED: `MyTradingSys/research/tom_fabio_course_correction_2026-11-07/CENSUS_5M15M_1109.md:3`: `"The pre-registered H1 (15m rejection fades, London/NY only, with the HTF ladder, node-to-node exit with break-even and half off at POC, Deribit maker fees) loses 0.11 R per trade over 1,484 trades (t = -1.4), and loses on the taker arm (-0.36 R, t = -5.2)."`
  - SOURCED: `MyTradingSys/research/tom_fabio_course_correction_2026-11-07/CENSUS_5M15M_1109.md:19-21`: `"trades | 1,484"`, `"net R, Deribit | -0.106 (SE 0.078)"`
  - SOURCED: `MyTradingSys/research/tom_fabio_course_correction_2026-11-07/CENSUS_5M15M_1109.md:54`: `"15m | node+BE | deribit | session+ladder | 1484 | -0.106 | 0.078 | -1.4"`
- **Review Verification (file:line)**:
  - OPUS: `MyTradingSys/research/four_model_review_2026-11-11/OPUS.md:26`: `"7y 1h -0.087 R net, n = 1,871, negative in all 8 years; pre-registered 15m with session + ladder + node exit -0.106 R, n = 1,484; T04 -0.221 R, n = 1,150"`
  - SONNET: `MyTradingSys/research/four_model_review_2026-11-11/SONNET.md:23`: `"15m H1 n 1,484 net -0.106 R (t -1.4), taker -0.358 (t -5.2); 5m n 1,579 -0.339; 1h gate-pass n 1,871 -0.087 (SE 0.022)."`
  - HAIKU: `MyTradingSys/research/four_model_review_2026-11-11/HAIKU.md:22`: `"net -0.106 R Deribit (t -1.4); -0.358 R taker (t -5.2); gross +0.064 R; n=1,484; kill line failed on all three tests"`
  - SUPERVISOR: `MyTradingSys/research/four_model_review_2026-11-11/SUPERVISOR.md:28`: `"-0.106 R (n 1,484, t -1.4), taker -0.358 R; gross +0.064 R"`

---

### Clause 3
- **Row in COMPARE.md s1**: `Counting agreeing indicators does not make a flag more right | 51 % with 4+ of 6 agreeing vs 49 % against`
- **Verdict**: MATCH
- **Source Verification (file:line)**:
  - SOURCED: Stated in review files referencing live_aid_review_2026-11-11/tables.md / RESULT.md:
    - OPUS: `MyTradingSys/research/four_model_review_2026-11-11/OPUS.md:27`: `"Live Aid 4+ of 6 agree: 51 % (n = 144) vs against: 49 % (n = 288); T13 score >= 3 nets -0.163 R (n = 410) | LA/tables.md:22,25; EH/EDGE_TABLE.md:19"`
    - SONNET: `MyTradingSys/research/four_model_review_2026-11-11/SONNET.md:15`: `"4+ of 6 readings agree = 51% right after 1h (n 144 of 759 IDEA flags), against = 49%; 58% of flags are followed by an opposite flag within 30 min | n 759 (+1,262 setups) | LA/RESULT.md:21-23; LA/tables.md:24"`
    - HAIKU: `MyTradingSys/research/four_model_review_2026-11-11/HAIKU.md:16`: `"4+ agree: idea 51%, against 49% (n 144 / 288) | live_aid_review_2026-11-11/tables.md:22,25"`
    - SUPERVISOR: `MyTradingSys/research/four_model_review_2026-11-11/SUPERVISOR.md:29`: `"51 % with 4+ of 6 agreeing vs 49 % against; score slope CI -0.91..+2.99 (n 13,851) | research/live_aid_review_2026-11-11/RESULT.md:22-23; research/edge_hunt_2026-11-09/EDGE_TABLE.md:19"`
- **Review Verification (file:line)**:
  - OPUS: `MyTradingSys/research/four_model_review_2026-11-11/OPUS.md:27`: `"Live Aid 4+ of 6 agree: 51 % (n = 144) vs against: 49 % (n = 288)"`
  - SONNET: `MyTradingSys/research/four_model_review_2026-11-11/SONNET.md:15`: `"4+ of 6 readings agree = 51% right after 1h (n 144 of 759 IDEA flags), against = 49%"`
  - HAIKU: `MyTradingSys/research/four_model_review_2026-11-11/HAIKU.md:16`: `"4+ agree: idea 51%, against 49% (n 144 / 288)"`
  - SUPERVISOR: `MyTradingSys/research/four_model_review_2026-11-11/SUPERVISOR.md:29`: `"51 % with 4+ of 6 agreeing vs 49 % against"`

---

### Clause 4
- **Row in COMPARE.md s1**: `ADX/DI and the value area are context and location, never a trigger | ADX agrees 50 % vs against 46 %; 80 % rule = 44 %, n 493`
- **Verdict**: MATCH
- **Source Verification (file:line)**:
  - SOURCED: Stated in review files:
    - OPUS: `MyTradingSys/research/four_model_review_2026-11-11/OPUS.md:25`: `"Dalton 80 % rule (back inside value means the far edge is reached) | 44 % [40..49], n = 493 | VA:9"` & `OPUS.md:51`: `"Live Aid, 29 days: idea right when ADX15 agrees 50 % vs against 46 % (n 234/263)"`
    - SONNET: `MyTradingSys/research/four_model_review_2026-11-11/SONNET.md:24`: `"80% rule is 44% [40-49], n 493"`, `SONNET.md:47`: `"ADX 15m agrees 50% (n 234) vs against 46% (n 263)"`
    - HAIKU: `MyTradingSys/research/four_model_review_2026-11-11/HAIKU.md:14`: `"The 80% value rule does not hold on BTC | 44% [40-49], n=493 | value_area_acceptance_2026-11-05/RESULT.md:13"`, `HAIKU.md:53`: `"idea 50% vs 46% (n 234 / 263)"`
    - SUPERVISOR: `MyTradingSys/research/four_model_review_2026-11-11/SUPERVISOR.md:18`: `"the "80 % rule" is 44 % on BTC | 77 % half-width drift (n 300, no placebo); 44 % (n 493) | research/value_area_acceptance_2026-11-05/RESULT.md:9-15"`, `SUPERVISOR.md:53`: `"ADX/DI 15m and 1h on Live Aid | agreeing with a flag: 50 % / 49 % right; against: 46 % / 45 % (n 234-296)"`
- **Review Verification (file:line)**:
  - OPUS: `MyTradingSys/research/four_model_review_2026-11-11/OPUS.md:5`: `"ADX/DI and the value area are useful as context and location, never as triggers."` & `OPUS.md:25,51`: `44 %, n = 493` and `50 % vs 46 %`
  - SONNET: `MyTradingSys/research/four_model_review_2026-11-11/SONNET.md:24,47,49,59`: `"80% rule is 44% [40-49], n 493"`, `"ADX 15m agrees 50% (n 234) vs against 46% (n 263)"`, `"CONTEXT label only ... never a trigger"`, `"drop it as a trigger"`
  - HAIKU: `MyTradingSys/research/four_model_review_2026-11-11/HAIKU.md:14,53,57,69`: `"44% [40-49], n=493"`, `"idea 50% vs 46% (n 234 / 263)"`, `"ADX is a regime label (context) at best. It is not a gate or trigger"`, `"value area is context ... Not a gate or trigger"`
  - SUPERVISOR: `MyTradingSys/research/four_model_review_2026-11-11/SUPERVISOR.md:18,52-54`: `"80 % rule = 44 % (n 493)"`, `"agreeing with a flag: 50 % ... against: 46 %"`, `"context only ... never a trigger"`, `"never a trigger"`

---

### Clause 5
- **Row in COMPARE.md s1**: `Live Aid must log what it flags before anything can be learned from it | card live-aid-flag-log-1111`
- **Verdict**: MATCH
- **Source Verification (file:line)**:
  - SOURCED: `MyTradingSys/research/four_model_review_2026-11-11/COMPARE.md:55`: `"live-aid-flag-log-1111, then live-aid-learning-loop-1111 (already filed)."`
- **Review Verification (file:line)**:
  - OPUS: `MyTradingSys/research/four_model_review_2026-11-11/OPUS.md:55`: `"live-aid-flag-log-1111, then live-aid-learning-loop-1111 (already filed)"`
  - SONNET: `MyTradingSys/research/four_model_review_2026-11-11/SONNET.md:62`: `"1. Ship live-aid-flag-log-1111 (prio 1 already, OD:2282); done when every flashed IDEA/SETUP is a row (time, level, readings, 1h outcome) and the daily review can reproduce LA/tables.md without replay.js."`
  - HAIKU: `MyTradingSys/research/four_model_review_2026-11-11/HAIKU.md:77`: `"no (no storage key for ADX; only premarket and liq keys at live_aid.html:419,810)"` (documenting lack of logging for indicators on Live Aid)
  - SUPERVISOR: `MyTradingSys/research/four_model_review_2026-11-11/SUPERVISOR.md:58`: `"1. Live Aid writes every flag it shows to a log (card live-aid-flag-log-1111). Done when a day of flags is on disk with the readings at that moment."` & `SUPERVISOR.md:66`: `"That needs the flag log first."`

---

### Clause 6
- **Row in COMPARE.md s1**: `The leads worth a forward test are 4h, not intraday | 4h RSI cross long +0.105 R; Malkan 4h level short +0.10 R (n 126)`
- **Verdict**: MATCH
- **Source Verification (file:line)**:
  - SOURCED: `MyTradingSys/research/edge_hunt_2026-11-09/EDGE_TABLE.md:27`: `"the best arm (divergence 3-10 bars, close) n=126, +0.10 R, about 0.9 SE."`
  - SOURCED: `MyTradingSys/research/edge_hunt_2026-11-09/EDGE_TABLE.md:30`: `"T06 is the best leftover: +0.048 R, n=1322, CI includes 0; the long side alone is +0.105 R (p 0.055, Holm 0.83)."`
- **Review Verification (file:line)**:
  - OPUS: `MyTradingSys/research/four_model_review_2026-11-11/OPUS.md:38-39`: `"2 | LONG, 4h: RSI14 crosses its SMA14 (T06 long side) | +0.105 R, n = 623"` and `"3 | SHORT, 4h: Malkan level short with a 3-10 bar close-to-close divergence | +0.10 R, n = 126, about 0.9 SE"`
  - SONNET: `MyTradingSys/research/four_model_review_2026-11-11/SONNET.md:31-32`: `"1 | SHORT at a marked 4h level ... best arm n 126 +0.10 R, ~0.9 SE"` and `"2 | LONG 4h, RSI14 crosses above its SMA14, BTC+ETH ... long side +0.105 R, p 0.055, Holm 0.83 (EH:15, :30-31)"`
  - HAIKU: `MyTradingSys/research/four_model_review_2026-11-11/HAIKU.md:11`: `"Intraday families are dead on cost"` and notes on 4h context throughout.
  - SUPERVISOR: `MyTradingSys/research/four_model_review_2026-11-11/SUPERVISOR.md:41-42`: `"2 | RSI14 cross of its average, 4h, long side ... +0.105 R long side, p 0.055"` and `"3 | Malkan level short, 4h (divergence 3-10 bars at a level) ... +0.10 R, n 126, 0.9 SE"`
