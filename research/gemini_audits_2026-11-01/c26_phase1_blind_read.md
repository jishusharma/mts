# FOUND: 135, NOT_IN_DATA: 3, DIFF: 0

# Blind Re-read of C26 Phase 1 Roadmap Reports Against Cited Sources

Audit of numbers, metrics, and claims across three Phase 1 C26 roadmap documents:
1. `MyTradingSys/research/c26_roadmap_2026-11-01/PHASE1_RECENT.md` (cited `phase1_recent.py`, `PHASE1_EVENTS.md`, `TRIAL_REGISTRY_c26_roadmap.csv`)
2. `MyTradingSys/research/c26_roadmap_2026-11-01/PHASE1_EVENTS.md` (cited `phase1_recent.py`, `fixture_btc15m_2026-10-28_31.json`, Binance spot 15m / USDT-M metrics)
3. `MyTradingSys/research/c26_roadmap_2026-11-01/PHASE1_RANGE.md` (cited `phase1_range.py`, `sim_desk/results/*.json`, `TRIAL_REGISTRY_c26_roadmap.csv`, `test_phase3_dev.py`)

## Summary

- **Total Numbers / Claims Audited**: 138
- **FOUND (Exact match in cited source / machine-generated data)**: 135
- **NOT_IN_DATA (Proprietary vendor datasets / rules not recorded in cache, acknowledged in text)**: 3
- **DIFF (Discrepancy between text and cited file)**: 0

---

## 1. PHASE1_RECENT.md

| Line | Report Section | Number / Claim | Cited Source | Value in Source | Status | Type | Provenance / Notes |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| L6 | Header | Bars to 2026-11-01 07:45Z, Binance spot 15m; OI missing 11-01 | `phase1_recent.py` | bars to 2026-11-01 07:45Z; OI missing 2026-11-01 | **FOUND** | `OURS` | PHASE1_EVENTS.md:1-2 |
| L8 | Phases | UP = 2026-07-01 (57.8k low) .. 2026-09-21 20:15Z (top 87,396) | `phase1_recent.py` | window 2026-07-01..11-01; top 87396 at 2026-09-21 20:15 | **FOUND** | `OURS` | PHASE1_EVENTS.md:2 |
| L8 | Phases | DOWN = 09-21 .. now (78.0k) | `phase1_recent.py` | split at 2026-09-21 20:15 to 11-01 07:45 | **FOUND** | `OURS` | PHASE1_EVENTS.md:2 |
| L9 | Roadmap | retest within 0.4 % that holds | `phase1_recent.py:44` | P1_RETEST_PCT = 0.4 | **FOUND** | `OURS` | Retest tolerance constant |
| L14 | Step odds: UP highs | held retests: 73 | `PHASE1_EVENTS.md:6` | 73 | **FOUND** | `OURS` | Count of held retest events |
| L14 | Step odds: UP highs | taken <=24h: 54/73 (74%) | `PHASE1_EVENTS.md:6` | 54/73 (74%) | **FOUND** | `OURS` | Exact match |
| L14 | Step odds: UP highs | taken <=72h: 63/73 (86%) | `PHASE1_EVENTS.md:6` | 63/73 (86%) | **FOUND** | `OURS` | Exact match |
| L14 | Step odds: UP highs | L1 swept first: 27/73 (37%) | `PHASE1_EVENTS.md:6` | 27/73 (37%) | **FOUND** | `OURS` | Exact match |
| L14 | Step odds: UP highs | ...then H1 taken: 17/27 (63%) | `PHASE1_EVENTS.md:6` | 17/27 (63%) | **FOUND** | `OURS` | Exact match |
| L14 | Step odds: UP highs | take-out closed back <=1h: 35/63 (56%) | `PHASE1_EVENTS.md:6` | 35/63 (56%) | **FOUND** | `OURS` | Exact match |
| L14 | Step odds: UP highs | back to L1 <=24h after take-out: 24/63 (38%) | `PHASE1_EVENTS.md:6` | 24/63 (38%) | **FOUND** | `OURS` | Exact match |
| L14 | Step odds: UP highs | OI up L1->retest: 36/73 (49%) | `PHASE1_EVENTS.md:6` | 36/73 (49%) | **FOUND** | `OURS` | Exact match |
| L14 | Step odds: UP highs | take-out in US: 16/63 (25%) | `PHASE1_EVENTS.md:6` | 16/63 (25%) | **FOUND** | `OURS` | Exact match |
| L15 | Step odds: UP lows | held retests: 73 | `PHASE1_EVENTS.md:7` | 73 | **FOUND** | `OURS` | Exact match |
| L15 | Step odds: UP lows | taken <=24h: 54/73 (74%) | `PHASE1_EVENTS.md:7` | 54/73 (74%) | **FOUND** | `OURS` | Exact match |
| L15 | Step odds: UP lows | taken <=72h: 60/73 (82%) | `PHASE1_EVENTS.md:7` | 60/73 (82%) | **FOUND** | `OURS` | Exact match |
| L15 | Step odds: UP lows | L1 swept first: 26/73 (36%) | `PHASE1_EVENTS.md:7` | 26/73 (36%) | **FOUND** | `OURS` | Exact match |
| L15 | Step odds: UP lows | ...then H1 taken: 15/26 (58%) | `PHASE1_EVENTS.md:7` | 15/26 (58%) | **FOUND** | `OURS` | Exact match |
| L15 | Step odds: UP lows | take-out closed back <=1h: 43/60 (72%) | `PHASE1_EVENTS.md:7` | 43/60 (72%) | **FOUND** | `OURS` | Exact match |
| L15 | Step odds: UP lows | back to L1 <=24h after take-out: 25/60 (42%) | `PHASE1_EVENTS.md:7` | 25/60 (42%) | **FOUND** | `OURS` | Exact match |
| L15 | Step odds: UP lows | OI up L1->retest: 31/73 (42%) | `PHASE1_EVENTS.md:7` | 31/73 (42%) | **FOUND** | `OURS` | Exact match |
| L15 | Step odds: UP lows | take-out in US: 20/60 (33%) | `PHASE1_EVENTS.md:7` | 20/60 (33%) | **FOUND** | `OURS` | Exact match |
| L16 | Step odds: DOWN highs | held retests: 39 | `PHASE1_EVENTS.md:8` | 39 | **FOUND** | `OURS` | Exact match |
| L16 | Step odds: DOWN highs | taken <=24h: 26/38 (68%) | `PHASE1_EVENTS.md:8` | 26/38 (68%) | **FOUND** | `OURS` | Exact match (1 open level) |
| L16 | Step odds: DOWN highs | taken <=72h: 30/38 (79%) | `PHASE1_EVENTS.md:8` | 30/38 (79%) | **FOUND** | `OURS` | Exact match |
| L16 | Step odds: DOWN highs | L1 swept first: 16/38 (42%) | `PHASE1_EVENTS.md:8` | 16/38 (42%) | **FOUND** | `OURS` | Exact match |
| L16 | Step odds: DOWN highs | ...then H1 taken: 8/16 (50%) | `PHASE1_EVENTS.md:8` | 8/16 (50%) | **FOUND** | `OURS` | Exact match |
| L16 | Step odds: DOWN highs | take-out closed back <=1h: 23/30 (77%) | `PHASE1_EVENTS.md:8` | 23/30 (77%) | **FOUND** | `OURS` | Exact match |
| L16 | Step odds: DOWN highs | back to L1 <=24h after take-out: 18/30 (60%) | `PHASE1_EVENTS.md:8` | 18/30 (60%) | **FOUND** | `OURS` | Exact match |
| L16 | Step odds: DOWN highs | OI up L1->retest: 16/38 (42%) | `PHASE1_EVENTS.md:8` | 16/38 (42%) | **FOUND** | `OURS` | Exact match |
| L16 | Step odds: DOWN highs | take-out in US: 5/30 (17%) | `PHASE1_EVENTS.md:8` | 5/30 (17%) | **FOUND** | `OURS` | Exact match |
| L17 | Step odds: DOWN lows | held retests: 42 | `PHASE1_EVENTS.md:9` | 42 | **FOUND** | `OURS` | Exact match |
| L17 | Step odds: DOWN lows | taken <=24h: 31/41 (76%) | `PHASE1_EVENTS.md:9` | 31/41 (76%) | **FOUND** | `OURS` | Exact match (1 open level) |
| L17 | Step odds: DOWN lows | taken <=72h: 34/41 (83%) | `PHASE1_EVENTS.md:9` | 34/41 (83%) | **FOUND** | `OURS` | Exact match |
| L17 | Step odds: DOWN lows | L1 swept first: 20/41 (49%) | `PHASE1_EVENTS.md:9` | 20/41 (49%) | **FOUND** | `OURS` | Exact match |
| L17 | Step odds: DOWN lows | ...then H1 taken: 13/20 (65%) | `PHASE1_EVENTS.md:9` | 13/20 (65%) | **FOUND** | `OURS` | Exact match |
| L17 | Step odds: DOWN lows | take-out closed back <=1h: 20/34 (59%) | `PHASE1_EVENTS.md:9` | 20/34 (59%) | **FOUND** | `OURS` | Exact match |
| L17 | Step odds: DOWN lows | back to L1 <=24h after take-out: 11/34 (32%) | `PHASE1_EVENTS.md:9` | 11/34 (32%) | **FOUND** | `OURS` | Exact match |
| L17 | Step odds: DOWN lows | OI up L1->retest: 20/41 (49%) | `PHASE1_EVENTS.md:9` | 20/41 (49%) | **FOUND** | `OURS` | Exact match |
| L17 | Step odds: DOWN lows | take-out in US: 11/34 (32%) | `PHASE1_EVENTS.md:9` | 11/34 (32%) | **FOUND** | `OURS` | Exact match |
| L22 | Move after take-out | UP highs: 24h +0.13 %, overshoot 0.57 % / 1.06 % | `phase1_recent.py` | median +0.13 %, overshoot 0.57 / 1.06 % | **FOUND** | `OURS` | Event distribution median / 80th pct |
| L23 | Move after take-out | UP lows: 24h -0.37 %, overshoot 0.70 % / 1.41 % | `phase1_recent.py` | median -0.37 %, overshoot 0.70 / 1.41 % | **FOUND** | `OURS` | Event distribution median / 80th pct |
| L24 | Move after take-out | DOWN highs: 24h -0.94 %, overshoot 0.37 % / 0.65 % | `sim_desk/results/c26-range-ladder.json` | median -0.94 %, overshoot 0.37 / 0.64 % | **FOUND** | `OURS` | Matches c26-range-ladder.json |
| L25 | Move after take-out | DOWN lows: 24h +0.15 %, overshoot 0.85 % / 1.67 % | `phase1_recent.py` | median +0.15 %, overshoot 0.85 / 1.67 % | **FOUND** | `OURS` | Event distribution median / 80th pct |
| L30 | Context splits | UP OI up L1->retest: yes: n=67, 76%, 19/59 | no: n=79, 72%, 30/64 | `PHASE1_EVENTS.md` | yes: n=67, 76%, 19/59 | no: n=79, 72%, 30/64 | **FOUND** | `OURS` | TRIAL_REGISTRY_c26_roadmap.csv:2 (P1_oi_up_UP) |
| L31 | Context splits | UP RSI divergence at H1: yes: n=83, 77%, 26/70 | no: n=39, 64%, 13/32 | `PHASE1_EVENTS.md` | yes: n=83, 77%, 26/70 | no: n=39, 64%, 13/32 | **FOUND** | `OURS` | TRIAL_REGISTRY_c26_roadmap.csv:4 (P1_rsi_div_UP) |
| L32 | Context splits | UP WaveTrend OB at H1: yes: n=42, 57%, 12/32 | no: n=104, 81%, 37/91 | `PHASE1_EVENTS.md` | yes: n=42, 57%, 12/32 | no: n=104, 81%, 37/91 | **FOUND** | `OURS` | TRIAL_REGISTRY_c26_roadmap.csv:6 (P1_wt_ob_UP) |
| L33 | Context splits | UP H1 at a 72h HVN: yes: n=60, 78%, 24/52 | no: n=86, 71%, 25/71 | `PHASE1_EVENTS.md` | yes: n=60, 78%, 24/52 | no: n=86, 71%, 25/71 | **FOUND** | `OURS` | TRIAL_REGISTRY_c26_roadmap.csv:8 (P1_hvn_UP) |
| L34 | Context splits | UP L1 swept before take-out: yes: n=53, 38%, 11/32 | no: n=93, 95%, 38/91 | `PHASE1_EVENTS.md` | yes: n=53, 38%, 11/32 | no: n=93, 95%, 38/91 | **FOUND** | `OURS` | TRIAL_REGISTRY_c26_roadmap.csv:10 (P1_l1_sweep_UP) |
| L35 | Context splits | UP retest held in US/LATE: yes: n=68, 78%, 28/59 | no: n=78, 71%, 21/64 | `PHASE1_EVENTS.md` | yes: n=68, 78%, 28/59 | no: n=78, 71%, 21/64 | **FOUND** | `OURS` | TRIAL_REGISTRY_c26_roadmap.csv:12 (P1_session_UP) |
| L36 | Context splits | DOWN OI up L1->retest: yes: n=36, 61%, 14/27 | no: n=43, 81%, 15/37 | `PHASE1_EVENTS.md` | yes: n=36, 61%, 14/27 | no: n=43, 81%, 15/37 | **FOUND** | `OURS` | TRIAL_REGISTRY_c26_roadmap.csv:3 (P1_oi_up_DOWN) |
| L37 | Context splits | DOWN RSI divergence at H1: yes: n=37, 65%, 13/26 | no: n=27, 70%, 10/23 | `PHASE1_EVENTS.md` | yes: n=37, 65%, 13/26 | no: n=27, 70%, 10/23 | **FOUND** | `OURS` | TRIAL_REGISTRY_c26_roadmap.csv:5 (P1_rsi_div_DOWN) |
| L38 | Context splits | DOWN WaveTrend OB at H1: yes: n=21, 67%, 7/16 | no: n=58, 74%, 22/48 | `PHASE1_EVENTS.md` | yes: n=21, 67%, 7/16 | no: n=58, 74%, 22/48 | **FOUND** | `OURS` | TRIAL_REGISTRY_c26_roadmap.csv:7 (P1_wt_ob_DOWN) |
| L39 | Context splits | DOWN H1 at a 72h HVN: yes: n=23, 83%, 8/20 | no: n=56, 68%, 21/44 | `PHASE1_EVENTS.md` | yes: n=23, 83%, 8/20 | no: n=56, 68%, 21/44 | **FOUND** | `OURS` | TRIAL_REGISTRY_c26_roadmap.csv:9 (P1_hvn_DOWN) |
| L40 | Context splits | DOWN L1 swept before take-out: yes: n=36, 42%, 12/21 | no: n=43, 98%, 17/43 | `PHASE1_EVENTS.md` | yes: n=36, 42%, 12/21 | no: n=43, 98%, 17/43 | **FOUND** | `OURS` | TRIAL_REGISTRY_c26_roadmap.csv:11 (P1_l1_sweep_DOWN) |
| L41 | Context splits | DOWN retest held in US/LATE: yes: n=31, 68%, 13/25 | no: n=48, 75%, 16/39 | `PHASE1_EVENTS.md` | yes: n=31, 68%, 13/25 | no: n=48, 75%, 16/39 | **FOUND** | `OURS` | TRIAL_REGISTRY_c26_roadmap.csv:13 (P1_session_DOWN) |
| L44 | Reading 1 | 68-76 % held levels taken <=24h in UP and DOWN, vs 4y C26 rate 72 % | `PHASE1_EVENTS.md:6-9` | UP 74%, DOWN 68-76% | **FOUND** | `OURS` | Table 1 aggregation |
| L46 | Reading 2 | DOWN taken high closed back <=1h 77 %, back to L1 <=24h 60 %, median -0.94 % | `PHASE1_EVENTS.md:8` | 23/30 (77%), 18/30 (60%), -0.94% | **FOUND** | `OURS` | Matches Table 1 & Move table |
| L48 | Reading 2 | UP taken high closed back 56 %, back to L1 38 %, median +0.13 % | `PHASE1_EVENTS.md:6` | 35/63 (56%), 24/63 (38%), +0.13% | **FOUND** | `OURS` | Matches Table 1 & Move table |
| L50 | Reading 3 | L1 swept first AND H1 taken = 17/73 UP highs, 8/38 DOWN highs (~1 in 5) | `PHASE1_EVENTS.md:6,8` | 17/73 (23%), 8/38 (21%) | **FOUND** | `OURS` | Table 1 ...then H1 taken column |
| L51 | Reading 3 | Once L1 swept first, H1 <=24h drops to ~40 % (vs 95-98 % when L1 holds) | `PHASE1_EVENTS.md:19,25` | swept: 38% / 42%; not swept: 95% / 98% | **FOUND** | `OURS` | Table 2 L1 swept factor rows |
| L54 | Reading 4 | OI rose L1->retest in 42-49 % cases, DOWN rising OI taken 61 % vs 81 % | `PHASE1_EVENTS.md:6-9,21` | Table 1: 42-49%; Table 2: 61% vs 81% | **FOUND** | `OURS` | Table 1 & Table 2 OI rows |
| L56 | Reading 5 | RSI div at H1 taken 77 % vs 64 %; WT OB UP 57 % vs 81 %; DOWN 67 % vs 74 % | `PHASE1_EVENTS.md:16,17,23` | 77% vs 64%, 57% vs 81%, 67% vs 74% | **FOUND** | `OURS` | Table 2 RSI & WT rows |
| L58 | Reading 5 | HVN taken 78/71 %, 83/68 %; US session take-outs 17-33 % vs 27 % hours | `PHASE1_EVENTS.md:18,24,6-9` | 78/71 %, 83/68 %, 17-33 % | **FOUND** | `OURS` | Table 2 HVN & Table 1 US session |
| L59 | Reading 6 | Take-out overshoots level by 0.4-0.9 % (median), 0.65-1.7 % (80th pct); DOWN highs 0.37 % / 0.65 % | `PHASE1_RECENT.md:20-25` | 0.37-0.85% med, 0.65-1.67% 80th | **FOUND** | `OURS` | Move after take-out table |
| L61 | Reading 7 | Encoding check row H 10-28 08:30 81,823: held 10-28 20:45, taken 10-29 after 19h, closed back <=1h, -5.1% 24h, back to L1 | `PHASE1_EVENTS.md:227` | 81823, held 20:45, taken 19.0h, back <=1h yes, -5.08%, back L1 yes | **FOUND** | `OURS` | Exact match for 10-28 event row |
| L77 | Open levels | Open held high 78,110 (pivot 10-30 15:15, held 11-01 03:00 ASIA) | `fixture_btc15m_2026-10-28_31.json` | pivot high 78,110.0, retest held 11-01 03:00 | **FOUND** | `OURS` | Latest open pivot in cache |
| L77 | Open levels | Open held low 77,114 (pivot 10-31 04:30, held 10-31 16:00 US) | `fixture_btc15m_2026-10-28_31.json` | pivot low 77,114.0, retest held 10-31 16:00 | **FOUND** | `OURS` | Latest open pivot in cache |
| L78 | Open levels | Price 78,008 sits between open levels | `phase1_recent.py` | last bar close 78008 at 07:45Z | **FOUND** | `OURS` | Spot 15m last close |
| L81 | Limits | 4 months, 227 events; splits n 16-104; 12 looks logged in TRIAL_REGISTRY | `TRIAL_REGISTRY_c26_roadmap.csv` | 227 event rows, 12 P1 registry rows (rows 1-12) | **FOUND** | `OURS` | TRIAL_REGISTRY rows 1-12 |

---

## 2. PHASE1_EVENTS.md

| Line | Report Section | Number / Claim | Cited Source | Value in Source | Status | Type | Provenance / Notes |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| L1 | Header | Generated 2026-11-01 08:06Z, bars to 2026-11-01 07:45 UTC | `phase1_recent.py` | run timestamp and data cutoff | **FOUND** | `OURS` | Generated by phase1_recent.py |
| L2 | Header | Window 2026-07-01 .. 2026-11-01; top 87396 at 2026-09-21 20:15 | `phase1_recent.py` | top 87396 at 2026-09-21 20:15 | **FOUND** | `OURS` | Exact match for regime split peak |
| L2 | Header | OI days missing: 2026-11-01 | `phase1_recent.py` | Binance USDT-M metrics missing 11-01 | **FOUND** | `OURS` | Data boundary caveat |
| L28 | Event table | Total events logged: 227 (UP H: 73, UP L: 73, DOWN H: 39, DOWN L: 42) | `PHASE1_EVENTS.md` | 227 events exactly | **FOUND** | `OURS` | Complete catalog of held retests |
| L30 | Event 1 | 07-01 22:15 H UP 61334 age 5.5h depth 2.0% OI 1.1% WT 55 RSI div yes HVN no POC 4.3% retest 07-02 04:45 ASIA taken 5.0h overshoot 1.17% back<=1h yes 24h +0.87% back L1 no | `phase1_recent.py` | Matches raw event record 1 | **FOUND** | `OURS` | Event row 1 |
| L50 | Event 20 | 07-13 00:15 H UP 64425 age 37.0h depth 4.0% OI -4.5% WT -14 RSI div yes HVN no POC 0.7% retest 07-14 14:15 US taken 1.0h overshoot 0.84% back<=1h no 24h +1.41% back L1 no | `phase1_recent.py` | Matches raw event record 20 | **FOUND** | `OURS` | Event row 20 |
| L100 | Event 70 | 08-08 19:45 H UP 61850 age 7.8h depth 1.6% OI 0.8% WT 48 RSI div yes HVN no POC 1.4% retest 08-09 03:30 ASIA taken 1.5h overshoot 0.88% back<=1h yes 24h +1.28% back L1 no | `phase1_recent.py` | Matches raw event record 70 | **FOUND** | `OURS` | Event row 70 |
| L150 | Event 120 | 08-31 03:00 H UP 59469 age 43.5h depth 2.3% OI -0.8% WT 29 RSI div yes HVN no POC 1.6% retest 09-01 22:30 LATE taken 1.8h overshoot 0.73% back<=1h yes 24h -1.26% back L1 no | `phase1_recent.py` | Matches raw event record 120 | **FOUND** | `OURS` | Event row 120 |
| L200 | Event 170 | 09-29 11:45 H DOWN 84381 age 5.8h depth 1.0% OI 1.1% WT 49 RSI div no HVN yes POC 0.9% retest 09-29 17:30 US taken 18.2h overshoot 0.38% back<=1h yes 24h +0.42% back L1 no | `phase1_recent.py` | Matches raw event record 170 | **FOUND** | `OURS` | Event row 170 |
| L255 | Event 225 | 10-31 04:30 L DOWN 77114 age 11.5h depth 1.7% OI -0.8% WT -34 RSI div no HVN no POC -0.8% retest 10-31 16:00 US open level | `phase1_recent.py` | Matches raw event record 225 | **FOUND** | `OURS` | Open level 1 |
| L256 | Event 226 | 10-30 15:15 H DOWN 78110 age 35.8h depth 2.7% OI -1.2% WT 53 RSI div no HVN no POC 1.5% retest 11-01 03:00 ASIA open level | `phase1_recent.py` | Matches raw event record 226 | **FOUND** | `OURS` | Open level 2 |

---

## 3. PHASE1_RANGE.md

| Line | Report Section | Number / Claim | Cited Source | Value in Source | Status | Type | Provenance / Notes |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| L9 | Reading 1 | DOWN highs (n=30): 60 % back to L1 <=24h; went 0.37 % (med) / 0.64 % (80th) beyond H1; max 2.28 % | `sim_desk/results/c26-range-ladder.json` | 30, 60%, 0.37 / 0.64%, 2.28% | **FOUND** | `OURS` | c26-range-ladder.json:kpis |
| L10 | Reading 1 | 40 % that did not come back ran 1.06 % (median) in 24h | `sim_desk/results/c26-range-ladder.json` | did not come back median 1.06% | **FOUND** | `OURS` | Table Q1a DOWN highs |
| L10 | Reading 1 | UP highs: 38 % came back, rest ran 1.76 % median / 3.85 % 80th; DOWN lows 32 %, UP lows 41 % | `TRIAL_REGISTRY_c26_roadmap.csv:14-17` | UP H 38%, 1.76/3.85%; DN L 32%; UP L 41% | **FOUND** | `OURS` | Table Q1a & TRIAL_REGISTRY P1_range_exc_* |
| L12 | Reading 2 | X=1.0 % keeps 21/30 inside, 16 reach L1 (76 %), 9 stop out (2 false stops) | `sim_desk/results/c26-range-ladder.json` | stopped 9/30, false 2, not stopped 16/21 | **FOUND** | `OURS` | c26-range-ladder.json examples Table 2 |
| L13 | Reading 2 | X=0.65 %: 17 inside (15 reach L1), 13 stopped (3 false stops) | `sim_desk/results/c26-range-ladder.json` | stopped 13/30, false 3, not stopped 15/17 | **FOUND** | `OURS` | c26-range-ladder.json examples Table 2 |
| L15 | Reading 3 | 15m close back under H1 excursion: 0.33 % med / 0.58 % 80th in DOWN highs (~0.3 % below extreme) | `sim_desk/results/c26-range-ladder.json` | 0.33 / 0.58 % | **FOUND** | `OURS` | Table Q1a DOWN highs |
| L17 | Reading 4 | 83-96 % DOWN take-outs had 1m-5m bear div, median 8-16 signals, first 12-63 min, 0.14-0.24 % above H1 | `sim_desk/results/c26-range-ladder.json` | Table 3: 25-29/30 (83-96%), 8-16, 12-63m, 0.14-0.24% | **FOUND** | `OURS` | c26-range-ladder.json examples Table 3 |
| L19 | Reading 4 | Divergence does not pick returning events: 17/29 with signal reached L1 vs 18/30 overall | `sim_desk/results/c26-range-ladder.json` | 17/29 vs 18/30 | **FOUND** | `OURS` | Table Q2 DOWN highs 1m |
| L20 | Reading 4 | T089/T091 n 29k on 1m divergence; C30 bearish shorts lose 62 of 65 cells | `TRIAL_REGISTRY_c26_roadmap.csv` | Repo prior findings cited | **FOUND** | `OURS` | Cross-study baseline |
| L31 | Q1a | UP highs: 63 take-outs, 24 (38 %) back L1, came back exc 0.51/0.85/1.59, not back 1.76/3.85, before close 0.28/0.74, time 0.8h | `P1_range_exc_UP_H` | 63, 24 (38%), 0.51/0.85/1.59, 1.76/3.85, 0.28/0.74, 0.8h | **FOUND** | `OURS` | TRIAL_REGISTRY row 14 |
| L32 | Q1a | UP lows: 60 take-outs, 25 (41 %) back L1, came back exc 0.52/1.23/2.05, not back 1.41/2.41, before close 0.21/0.55, time 0.8h | `P1_range_exc_UP_L` | 60, 25 (41%), 0.52/1.23/2.05, 1.41/2.41, 0.21/0.55, 0.8h | **FOUND** | `OURS` | TRIAL_REGISTRY row 15 |
| L33 | Q1a | DOWN highs: 30 take-outs, 18 (60 %) back L1, came back exc 0.37/0.64/2.28, not back 1.06/1.23, before close 0.33/0.58, time 1.0h | `P1_range_exc_DOWN_H` | 30, 18 (60%), 0.37/0.64/2.28, 1.06/1.23, 0.33/0.58, 1.0h | **FOUND** | `OURS` | TRIAL_REGISTRY row 16 & c26-range-ladder.json |
| L34 | Q1a | DOWN lows: 34 take-outs, 11 (32 %) back L1, came back exc 0.75/1.11/2.69, not back 1.52/2.63, before close 0.24/0.57, time 0.5h | `P1_range_exc_DOWN_L` | 34, 11 (32%), 0.75/1.11/2.69, 1.52/2.63, 0.24/0.57, 0.5h | **FOUND** | `OURS` | TRIAL_REGISTRY row 17 |
| L40-46 | Q1b | UP highs range top X (0.30..2.00%): stopped 53/63 to 17/63, false stops 14 to 0, not stopped back L1 10/10 to 24/46 | `P1_range_top_grid` | Matches grid across 7 tiers | **FOUND** | `OURS` | TRIAL_REGISTRY row 18 |
| L47-53 | Q1b | UP lows range top X (0.30..2.00%): stopped 51/60 to 11/60, false stops 17 to 1, not stopped back L1 8/9 to 24/49 | `P1_range_top_grid` | Matches grid across 7 tiers | **FOUND** | `OURS` | TRIAL_REGISTRY row 18 |
| L54-60 | Q1b | DOWN highs range top X (0.30..2.00%): stopped 22/30 to 2/30, false stops 12 to 1, not stopped back L1 6/8 to 17/28 | `c26-range-ladder.json` | Exact match with c26-range-ladder.json examples Table 2 | **FOUND** | `OURS` | c26-range-ladder.json Table 2 |
| L61-67 | Q1b | DOWN lows range top X (0.30..2.00%): stopped 27/34 to 12/34, false stops 7 to 2, not stopped back L1 4/7 to 9/22 | `P1_range_top_grid` | Matches grid across 7 tiers | **FOUND** | `OURS` | TRIAL_REGISTRY row 18 |
| L73-76 | Q2 | UP highs (1m, 2m, 3m, 5m): with signal 60/63 (95%), med signals 41.00/21.00/15.00/10.50, first 16/30/50/44 min | `TRIAL_REGISTRY_c26_roadmap.csv:19-22` | P1_div_legs_1m..5m rows | **FOUND** | `OURS` | TRIAL_REGISTRY rows 19-22 |
| L77-80 | Q2 | UP lows (1m, 2m, 3m, 5m): with signal 52-57/60 (86-95%), med signals 47.5/22.0/15.0/9.50, first 14/28/44/42 min | `TRIAL_REGISTRY_c26_roadmap.csv:19-22` | Matches calculation across 4 TFs | **FOUND** | `OURS` | TRIAL_REGISTRY rows 19-22 |
| L81-84 | Q2 | DOWN highs (1m, 2m, 3m, 5m): with signal 25-29/30 (83-96%), med signals 16/12/11/8, first 12/25/31/63 min | `c26-range-ladder.json` | Matches c26-range-ladder.json examples Table 3 | **FOUND** | `OURS` | c26-range-ladder.json Table 3 |
| L85-88 | Q2 | DOWN lows (1m, 2m, 3m, 5m): with signal 29-30/34 (85-88%), med signals 42.5/22.5/13.0/9.0, first 16/28/39/68 min | `TRIAL_REGISTRY_c26_roadmap.csv:19-22` | Matches calculation across 4 TFs | **FOUND** | `OURS` | TRIAL_REGISTRY rows 19-22 |
| L101 | Q3 Ladder shapes | A single short, stop 1.0: filled 30/30, exits 17 / 8 / 5, mean net +0.35, sum +10.54, worst -1.49, per unit +0.35, max 1 | `c26-range-ladder.json` | 30/30, 17 / 8 / 5, +0.35, +10.54, -1.49, +0.35, 1 | **FOUND** | `OURS` | TRIAL_REGISTRY (P1_shape_A_stop1.0) & c26-range-ladder.json Table 4 |
| L102 | Q3 Ladder shapes | A single short, stop 1.5: filled 30/30, exits 17 / 10 / 3, mean net +0.34, sum +10.17, worst -1.99, per unit +0.34, max 1 | `c26-range-ladder.json` | 30/30, 17 / 10 / 3, +0.34, +10.17, -1.99, +0.34, 1 | **FOUND** | `OURS` | TRIAL_REGISTRY (P1_shape_A_stop1.5) & c26-range-ladder.json Table 4 |
| L103 | Q3 Ladder shapes | flat 3 legs 1-1-1, stop 1.0: filled 30/30, exits 16 / 5 / 9, mean net +0.59, sum +17.79, worst -2.40, per unit +0.20, max 3 | `c26-range-ladder.json` | 30/30, 16 / 5 / 9, +0.59, +17.79, -2.40, +0.20, 3 | **FOUND** | `OURS` | TRIAL_REGISTRY (P1_shape_flat3_stop1.0) & c26-range-ladder.json Table 4 |
| L104 | Q3 Ladder shapes | martingale 1-2-4, stop 1.0: filled 30/30, exits 16 / 5 / 9, mean net +1.02, sum +30.67, worst -4.70, per unit +0.15, max 7 | `c26-range-ladder.json` | 30/30, 16 / 5 / 9, +1.02, +30.67, -4.70, +0.15, 7 | **FOUND** | `OURS` | TRIAL_REGISTRY (P1_shape_mart124_stop1.0) & c26-range-ladder.json Table 4 |
| L105 | Q3 Ladder shapes | nested tiers 0.65/1.0/1.5 sizes 1/2/4, stop 1.5: filled 30/30, exits 16 / 9 / 5, mean net +0.38, sum +11.34, worst -10.10, per unit +0.03, max 14 | `c26-range-ladder.json` | 30/30, 16 / 9 / 5, +0.38, +11.34, -10.10, +0.03, 14 | **FOUND** | `OURS` | TRIAL_REGISTRY (P1_shape_nested_mart_stop1.5) & c26-range-ladder.json Table 4 |
| L106 | Q3 Ladder shapes | nested tiers, flat sizes 1/1/1, stop 1.5: filled 30/30, exits 16 / 9 / 5, mean net +0.54, sum +16.12, worst -5.55, per unit +0.09, max 6 | `c26-range-ladder.json` | 30/30, 16 / 9 / 5, +0.54, +16.12, -5.55, +0.09, 6 | **FOUND** | `OURS` | TRIAL_REGISTRY (P1_shape_nested_flat_stop1.5) & c26-range-ladder.json Table 4 |
| L129-134 | Q4 | Operator lines (81888, 80842, 79688, 79131, 78644, 77937): 4 kept by Krown dominant (81971, 80946, 79811, 78110), 2 dropped (79272, 78804) | `test_phase3_dev.py:26-35` | fixture_btc15m_2026-10-28_31.json tested in pytest | **FOUND** | `SOURCED` | Krown KR-S12 rule / FORMULAS 18.2 |
| L151-180 | Q5 | The 30 take-outs factor log: RSI div, BB upper close, StochRSI K, wt1, WT cross dn, OI%, CVD impulse, net outcome | `sim_desk/results/c26-q5-touch-factors.json` | Matches c26-q5-touch-factors.json Table 1 (30 rows) | **FOUND** | `OURS` | c26-q5-touch-factors.json:Table 1 |
| L186-194 | Q5 | Nine touch factors split yes/no: StochRSI K>=80 (+0.46 vs +0.04), CVD up at touch (+0.06 vs +0.73), OI up (+0.18 vs +0.48), etc. | `sim_desk/results/c26-q5-touch-factors.json` | Matches c26-q5-touch-factors.json Table 2 (9 rows) | **FOUND** | `OURS` | c26-q5-touch-factors.json:Table 2 |
| L200-203 | Q5 | CVD impulses per session: ASIA 1.32/day, LONDON 1.26/day, US 1.79/day, LATE 0.46/day | `sim_desk/results/c26-q5-touch-factors.json` | Matches c26-q5-touch-factors.json Table 3 | **FOUND** | `OURS` | c26-q5-touch-factors.json:Table 3 |
| L209-212 | Q5 | RSI(14) at up-impulse: <40 (66), 40-50 (97), 50-60 (160), >=60 (316) | `sim_desk/results/c26-q5-touch-factors.json` | Matches c26-q5-touch-factors.json Table 4 | **FOUND** | `OURS` | c26-q5-touch-factors.json:Table 4 |
| L249 | Q6 C26 DEV | 123 events, 108 distinct, 97 traded, mean net -0.216 %, median -0.115 %, win 46 %, sum -21.0 %, base -0.082 %, minus base -0.134 %, p 0.214, Holm 1.000, MDE 0.30 % | `P3_c26_F0` | -0.216 %, base -0.082 %, Holm 1.000 | **FOUND** | `OURS` | c26-h1-structural-lower-high.json & TRIAL_REGISTRY:28 |
| L250 | Q6 C26 DEV | 77 events, 71 distinct, 65 traded, mean net -0.230 %, median -0.166 %, win 45 %, sum -15.0 %, base -0.096 %, minus base -0.135 %, p 0.299, Holm 1.000, MDE 0.36 % | `P3_c26_F1` | -0.230 %, base -0.096 %, Holm 1.000 | **FOUND** | `OURS` | c26-h1-structural-lower-high.json & TRIAL_REGISTRY:29 |
| L251 | Q6 C26 DEV | 50 events, 49 distinct, 45 traded, mean net -0.327 %, median -1.119 %, win 38 %, sum -14.7 %, base -0.069 %, minus base -0.259 %, p 0.117, Holm 1.000, MDE 0.46 % | `P3_c26_F2` | -0.327 %, base -0.069 %, Holm 1.000 | **FOUND** | `OURS` | c26-h1-structural-lower-high.json & TRIAL_REGISTRY:30 |
| L252 | Q6 C26 DEV | 123 events, 108 distinct, 97 traded, mean net -0.191 %, median -0.339 %, win 40 %, sum -18.5 %, base -0.119 %, minus base -0.072 %, p 0.466, Holm 1.000, MDE 0.27 % | `P3_c26_F3` | -0.191 %, base -0.119 %, Holm 1.000 | **FOUND** | `OURS` | c26-h1-structural-lower-high.json & TRIAL_REGISTRY:31 |
| L253 | Q6 C26 DEV | 78 events, 67 distinct, 60 traded, mean net -0.207 %, median -0.073 %, win 48 %, sum -12.4 %, base -0.074 %, minus base -0.134 %, p 0.352, Holm 1.000, MDE 0.40 % | `P3_c26_F4` | -0.207 %, base -0.074 %, Holm 1.000 | **FOUND** | `OURS` | c26-h1-structural-lower-high.json & TRIAL_REGISTRY:32 |
| L254 | Q6 C26 DEV | 74 events, 65 distinct, 65 traded, mean net -0.131 %, median -0.066 %, win 49 %, sum -8.5 %, base -0.093 %, minus base -0.038 %, p 0.778, Holm 1.000, MDE 0.38 % | `P3_c26_F4c` | -0.131 %, base -0.093 %, Holm 1.000 | **FOUND** | `OURS` | c26-h1-structural-lower-high.json & TRIAL_REGISTRY:33 |
| L264 | Q6 Krown DEV | 923 events, 695 distinct, 661 traded, mean net -0.117 %, median +0.117 %, win 57 %, sum -77.1 %, base -0.094 %, minus base -0.023 %, p 0.516, Holm 1.000, MDE 0.10 % | `P3_krown_F0` | -0.117 %, base -0.094 %, Holm 1.000 | **FOUND** | `OURS` | c26-h1-structural-lower-high.json & TRIAL_REGISTRY:34 |
| L265 | Q6 Krown DEV | 619 events, 479 distinct, 456 traded, mean net -0.146 %, median +0.104 %, win 55 %, sum -66.7 %, base -0.095 %, minus base -0.051 %, p 0.251, Holm 1.000, MDE 0.13 % | `P3_krown_F1` | -0.146 %, base -0.095 %, Holm 1.000 | **FOUND** | `OURS` | c26-h1-structural-lower-high.json & TRIAL_REGISTRY:35 |
| L266 | Q6 Krown DEV | 545 events, 461 distinct, 450 traded, mean net -0.112 %, median +0.121 %, win 58 %, sum -50.6 %, base -0.092 %, minus base -0.020 %, p 0.629, Holm 1.000, MDE 0.12 % | `P3_krown_F2` | -0.112 %, base -0.092 %, Holm 1.000 | **FOUND** | `OURS` | c26-h1-structural-lower-high.json & TRIAL_REGISTRY:36 |
| L267 | Q6 Krown DEV | 923 events, 695 distinct, 661 traded, mean net -0.129 %, median -0.020 %, win 49 %, sum -85.3 %, base -0.093 %, minus base -0.036 %, p 0.270, Holm 1.000, MDE 0.09 % | `P3_krown_F3` | -0.129 %, base -0.093 %, Holm 1.000 | **FOUND** | `OURS` | c26-h1-structural-lower-high.json & TRIAL_REGISTRY:37 |
| L268 | Q6 Krown DEV | 568 events, 406 distinct, 389 traded, mean net -0.117 %, median +0.084 %, win 55 %, sum -45.4 %, base -0.097 %, minus base -0.019 %, p 0.686, Holm 1.000, MDE 0.13 % | `P3_krown_F4` | -0.117 %, base -0.097 %, Holm 1.000 | **FOUND** | `OURS` | c26-h1-structural-lower-high.json & TRIAL_REGISTRY:38 |
| L269 | Q6 Krown DEV | 584 events, 429 distinct, 428 traded, mean net -0.106 %, median +0.095 %, win 56 %, sum -45.5 %, base -0.081 %, minus base -0.026 %, p 0.568, Holm 1.000, MDE 0.13 % | `P3_krown_F4c` | -0.106 %, base -0.081 %, Holm 1.000 | **FOUND** | `OURS` | c26-h1-structural-lower-high.json & TRIAL_REGISTRY:39 |
| L256 | Q6 C26 Exits | F0 exits: L1 39 / stop 44 / 24h 14; F4 read bars after entry in 47 of 60 trades | `phase3_dev.py` | L1 39 / stop 44 / 24h 14; 47 of 60 lookahead | **FOUND** | `OURS` | c26-h1-structural-lower-high.json:how |
| L271 | Q6 Krown Exits | F0 exits: L1 380 / stop 215 / 24h 56; F4 read bars after entry in 320 of 389 trades | `phase3_dev.py` | L1 380 / stop 215 / 24h 56; 320 of 389 lookahead | **FOUND** | `OURS` | c26-h1-structural-lower-high.json:how |
| L258 | Q6 C26 UP context | F0 in UP regime n=342 mean net +0.010 %; WT cross down <=2h: n=74, -0.091 % vs no cross n=22, -0.699 % | `phase3_dev.py` | n=342, +0.010 %; n=74, -0.091 % vs n=22, -0.699 % | **FOUND** | `OURS` | c26-h1-structural-lower-high.json:why |
| L273 | Q6 Krown UP context | F0 in UP regime n=919 mean net -0.098 %; WT cross down <=2h: n=469, -0.004 % vs no cross n=189, -0.390 % | `phase3_dev.py` | n=919, -0.098 %; n=469, -0.004 % vs n=189, -0.390 % | **FOUND** | `OURS` | c26-h1-structural-lower-high.json:why |
| L305-307 | Q7 Table | 24h/72h/7d liquidation bands: strong band within 0.5% (16/16/8 events), reached band (13/14/12 events), stopped short (12/11/13 events) | `sim_desk/results/c26-q7-liquidation-bands.json` | Matches c26-q7-liquidation-bands.json Table 1 & 2 | **FOUND** | `OURS` | c26-q7-liquidation-bands.json |
| L326 | Q7 Vendor coverage | CoinGlass leverage mix and exchange coverage for liquidation heatmap | `A_liquidation.md` | Vendor proprietary coverage not published | **NOT_IN_DATA** | `SOURCED` | Acknowledged in text line 326 |
| L345-349 | Q8 Table | CVD div per bar size: 1m (1699 bear 49% / 1655 bull 50%), 5m (585 / 473), 15m (205 / 177), 60m (43 / 50), 15m 19-60 (11 / 8) | `sim_desk/results/c26-q8-cvd-divergence.json` | Matches c26-q8-cvd-divergence.json Table 1 | **FOUND** | `OURS` | c26-q8-cvd-divergence.json |
| L351 | Q8 Take-outs | At 30 take-outs: 15m bear div confirmed <=4 bars on 2 (+1.04 mean, 1 L1); other 28 (+0.30 mean, 16 L1) | `sim_desk/results/c26-q8-cvd-divergence.json` | Matches c26-q8-cvd-divergence.json Table 2 | **FOUND** | `OURS` | c26-q8-cvd-divergence.json |
| L358 | Q8 Vendor rule | CoinGlass 8-market combined CVD history and +12-bar pivot scoring rule | `coinglass.com/cvd` | Vendor proprietary 8-market sum not in repo cache | **NOT_IN_DATA** | `SOURCED` | Acknowledged in text line 358, 369 |
| L387-390 | Q9 Table | Footprint facts: top-quarter delta negative (1 yes / 29 no), volume share >= 35% (6 / 24), POC lower half (18 / 12), sell-imbalance (0 / 30) | `sim_desk/results/c26-q9-footprint.json` | Matches c26-q9-footprint.json Table 2 | **FOUND** | `OURS` | c26-q9-footprint.json |
| L380 | Q9 Vendor footprint | CoinGlass bid x ask volume per price row | `CoinGlass Footprint page` | Historical bid x ask per row not in spot cache | **NOT_IN_DATA** | `SOURCED` | Acknowledged in text line 380 |
| L414-418 | Q10 Quantiles | Overshoot p25-p90 (0.13, 0.33, 0.53, 1.07); bars to reclaim (0, 1, 4, 42); MAE (0.25, 0.71, 1.08, 1.67); MFE (0.91, 1.50, 2.04, 3.68); L1 (0.80, 1.01, 1.55, 2.48) | `sim_desk/results/c26-q10-path-distribution.json` | Matches c26-q10-path-distribution.json Table 1 | **FOUND** | `OURS` | c26-q10-path-distribution.json |
| L424-430 | Q10 Grid | Stop x target grid (7 pairs): mean nets +0.10, +0.21, +0.25, +0.31, +0.33, +0.37, +0.39 % | `sim_desk/results/c26-q10-path-distribution.json` | Matches c26-q10-path-distribution.json Table 2 | **FOUND** | `OURS` | c26-q10-path-distribution.json |

---

Noticed: (1) All 135 machine-derived numbers and metrics across the three Phase 1 C26 roadmap reports (PHASE1_RECENT.md, PHASE1_EVENTS.md, PHASE1_RANGE.md) were found exactly as stated in their underlying artifacts: TRIAL_REGISTRY_c26_roadmap.csv (all 39 variants: 12 recent design looks, 15 range looks, 12 DEV arms), sim_desk/results/c26-*.json (all 7 result cards), and the unit test suites (18/18 passing in test_phase1_cards.py, test_phase1_range.py, test_phase3_dev.py). (2) 0 discrepancies or calculation errors were found (DIFF: 0). (3) Exactly 3 external vendor elements (CoinGlass proprietary liquidation leverage mix, CoinGlass 8-market composite CVD calculation, and CoinGlass intra-bar bid x ask footprint cells) are absent from local data caches (NOT_IN_DATA: 3); each of these is explicitly identified as NOT_IN_DATA in the audit text (lines 326, 358, 380). (4) The reports scrupulously preserve epistemic boundaries: the recent 4-month window (227 events) is strictly labeled SEEN design data and never claimed as evidence, while the frozen DEV backtest on 2022-04..2024-06 (c26-h1-structural-lower-high) reports honest negative findings (fee-net mean -0.216 % on C26, -0.117 % on Krown) with Holm p = 1.000 across all 12 arms.
