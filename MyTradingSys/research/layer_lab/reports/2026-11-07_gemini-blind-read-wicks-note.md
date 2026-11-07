# Independent Gemini Blind Read: Wicks Research Note vs Wick Census Outputs

- **Card**: `gemini-blind-read-wicks-note-1107`
- **Date**: 2026-11-07 UTC
- **Reader**: Gemini (independent blind read worker, JIS-NUC)
- **Target Prose**: `MyTradingSys/research/wicks_2026-11/WICKS_NOTE_2026-11-07.md`
- **Data & Script Sources**:
  - `MyTradingSys/research/wicks_2026-11/wick_census.py`
  - `MyTradingSys/research/wicks_2026-11/CENSUS_15m_2026-10-03_11-07.md`
  - `MyTradingSys/research/wicks_2026-11/CENSUS_5m_2026-10-03_11-07.md`

---

## 1. Scope and Fee-Net Context

- **Folder Data Availability**:
  - Script `wick_census.py` and output reports `CENSUS_15m_2026-10-03_11-07.md` and `CENSUS_5m_2026-10-03_11-07.md` compute event counts, median wick percentages, relative volume, and gross target-first vs stop-first hit rates at R = 1 (OURS: `1` [SOURCED `wick_census.py:5`: `"outcome (R = 1)"`]).
  - **Fee-Net**: There are no fee calculations or fee parameters in the study folder. `WICKS_NOTE_2026-11-07.md:7` explicitly notes: SOURCED `"Status: PROPOSAL. Measurement below is descriptive (5 weeks, one venue, no fees)."`. Furthermore, `WICKS_NOTE_2026-11-07.md:38` notes SOURCED `"before fees"`, and `WICKS_NOTE_2026-11-07.md:92` defers fee-net metrics to plan step W2 (OURS: `2` [SOURCED `WICKS_NOTE_2026-11-07.md:92`: `"hit rate R = 1 and R = 2 fee-net per cell"`]). Thus, fee-net where folder has data is SOURCED `0` (absent / not computed in `wicks_2026-11`).

---

## 2. Table-by-Table Recomputation

### Table 1: Definitions (`WICKS_NOTE_2026-11-07.md:9-18`) vs `wick_census.py`

| Term | WICKS_NOTE Rule (Prose) | `wick_census.py` Parameter / Rule | Recomputed Status |
|---|---|---|---|
| single-bar wick | wick >= 60 % (SOURCED `WICKS_NOTE_2026-11-07.md:12`: `"60 %"`), range >= 1.5 x (SOURCED `WICKS_NOTE_2026-11-07.md:12`: `"1.5 x"`) median range of previous day | `wick < 0.6 * rng` (SOURCED `wick_census.py:54`: `"0.6"`), `rng < 1.5 * med` (SOURCED `wick_census.py:51`: `"1.5"`), `LOOK = 96` (15m = 24 h = 1 day) / `288` (5m = 24 h = 1 day) (SOURCED `wick_census.py:15`: `"LOOK = 96 if tf == \"15m\" else 288"`) | MATCH |
| sweep | bar low < lowest low of previous 20 bars (SOURCED `WICKS_NOTE_2026-11-07.md:13`: `"20 bars"`), close back above it | `prior = rows[i - 20:i]; sweep = l < plow and c > plow` (SOURCED `wick_census.py:55-57`: `"20"`) | MATCH |
| V-sweep (multi-bar) | low below 20-bar low (SOURCED `WICKS_NOTE_2026-11-07.md:14`: `"20-bar low"`), close back above within 3 bars (SOURCED `WICKS_NOTE_2026-11-07.md:14`: `"3 bars"`), 2-4 bars on 5m (SOURCED `WICKS_NOTE_2026-11-07.md:14`: `"2-4 bars"`), 1 bar on 15m (SOURCED `WICKS_NOTE_2026-11-07.md:14`: `"1 bar"`) | `for k in range(1, 4): if rows[i + k][4] > plow:` (SOURCED `wick_census.py:72-73`: `"range(1, 4)"`) | MATCH |
| outcome, R = 1 | enter at close, stop at wick extreme, target R = 1 (SOURCED `WICKS_NOTE_2026-11-07.md:15`: `"R = 1"`), 4 h (15m) / 2 h (5m) window (SOURCED `WICKS_NOTE_2026-11-07.md:15`: `"4 h (15m) / 2 h (5m)"`) | `H = {"15m": 16, "5m": 24}[tf]` (16 * 15m = 240 m = 4 h; 24 * 5m = 120 m = 2 h) (SOURCED `wick_census.py:14`: `"H = {\"15m\": 16, \"5m\": 24}[tf]"`) | MATCH |
| knife (context) | 12 bars (SOURCED `WICKS_NOTE_2026-11-07.md:16`: `"12 bars"`), fall >= 2 % (SOURCED `WICKS_NOTE_2026-11-07.md:16`: `"2 %"`), counter-move < 25 % (SOURCED `WICKS_NOTE_2026-11-07.md:16`: `"25 %"`) | `pre = rows[i - 12:i]; drop <= -2.0%; bounce < 0.25 * (top - o)` (SOURCED `wick_census.py:22-29`: `"12"`, `"-2.0"`, `"0.25"`) | MATCH |
| session (UTC) | ASIA 00-08, EU 08-13, US 13-21, LATE 21-24 (SOURCED `WICKS_NOTE_2026-11-07.md:17`: `"ASIA 00-08, EU 08-13, US 13-21, LATE 21-24"`) | `h < 8 -> ASIA, h < 13 -> EU, h < 21 -> US, else LATE` (SOURCED `wick_census.py:17-18`: `"8"`, `"13"`, `"21"`) | MATCH |

---

### Table 2: Friday 2026-11-06 5m Bar Data (`WICKS_NOTE_2026-11-07.md:19-26`) vs `CENSUS_5m_2026-10-03_11-07.md:120-123`

| UTC | O (Prose) | H (Prose) | L (Prose) | C (Prose) | Vol (Prose) | Folder Source (`CENSUS_5m_2026-10-03_11-07.md`) | Recomputed Diff |
|---|---|---|---|---|---|---|---|
| 14:55 | 75,692 (SOURCED `WICKS_NOTE_2026-11-07.md:22`) | 75,704 (SOURCED `WICKS_NOTE_2026-11-07.md:22`) | 75,280 (SOURCED `WICKS_NOTE_2026-11-07.md:22`) | 75,511 (SOURCED `WICKS_NOTE_2026-11-07.md:22`) | 1,862 (SOURCED `WICKS_NOTE_2026-11-07.md:22`) | O 75692 H 75704 L 75280 C 75511 V 1862 (SOURCED `CENSUS_5m_2026-10-03_11-07.md:120`) | 0 (MATCH) |
| 15:00 | 75,511 (SOURCED `WICKS_NOTE_2026-11-07.md:23`) | 75,568 (SOURCED `WICKS_NOTE_2026-11-07.md:23`) | 74,929 (SOURCED `WICKS_NOTE_2026-11-07.md:23`) | 75,046 (SOURCED `WICKS_NOTE_2026-11-07.md:23`) | 2,702 (SOURCED `WICKS_NOTE_2026-11-07.md:23`) | O 75511 H 75568 L 74929 C 75046 V 2702 (SOURCED `CENSUS_5m_2026-10-03_11-07.md:121`) | 0 (MATCH) |
| 15:05 | 75,046 (SOURCED `WICKS_NOTE_2026-11-07.md:24`) | 75,378 (SOURCED `WICKS_NOTE_2026-11-07.md:24`) | 74,810 (SOURCED `WICKS_NOTE_2026-11-07.md:24`) | 75,290 (SOURCED `WICKS_NOTE_2026-11-07.md:24`) | 3,005 (SOURCED `WICKS_NOTE_2026-11-07.md:24`) | O 75046 H 75378 L 74810 C 75290 V 3005 (SOURCED `CENSUS_5m_2026-10-03_11-07.md:122`) | 0 (MATCH) |
| 15:10 | 75,290 (SOURCED `WICKS_NOTE_2026-11-07.md:25`) | 75,820 (SOURCED `WICKS_NOTE_2026-11-07.md:25`) | 75,194 (SOURCED `WICKS_NOTE_2026-11-07.md:25`) | 75,809 (SOURCED `WICKS_NOTE_2026-11-07.md:25`) | 1,654 (SOURCED `WICKS_NOTE_2026-11-07.md:25`) | O 75290 H 75820 L 75194 C 75809 V 1654 (SOURCED `CENSUS_5m_2026-10-03_11-07.md:123`) | 0 (MATCH) |

- **Section 2 Prose Verification**:
  - 15m 15:00 bar: low 74,810 (SOURCED `WICKS_NOTE_2026-11-07.md:27`), close 75,809 (SOURCED `WICKS_NOTE_2026-11-07.md:27`), wick 0.93 % (SOURCED `WICKS_NOTE_2026-11-07.md:27`), volume 12 x median (SOURCED `WICKS_NOTE_2026-11-07.md:27`). Matches `CENSUS_15m_2026-10-03_11-07.md:109`: SOURCED `low 74810 high 75820 close 75809 wick 0.93% relvol 12.0`.
  - 5m V-sweep: volume 15.7 x median (SOURCED `WICKS_NOTE_2026-11-07.md:28`), V close 75,290 (SOURCED `WICKS_NOTE_2026-11-07.md:29`), stop 74,810 (SOURCED `WICKS_NOTE_2026-11-07.md:29`). Matches `CENSUS_5m_2026-10-03_11-07.md:115`: SOURCED `15:00 LOW V2 low 74810 high 75568 close 75290 wick 0.64% relvol 15.7 sweep=True knife=False target_first=True`.

---

### Table 3: Five-Week Census (`WICKS_NOTE_2026-11-07.md:35-45`) vs Census Output Tables

| Kind | Prose n | Prose Hit Rate (R=1) | Folder Sourced Counts | Recomputed Hit Rate | Cell Diff | Status |
|---|---|---|---|---|---|---|
| 15m lower single-bar wick, all | 66 (SOURCED `WICKS_NOTE_2026-11-07.md:38`) | 38 % (SOURCED `WICKS_NOTE_2026-11-07.md:38`) | n = 66 (SOURCED `CENSUS_15m_2026-10-03_11-07.md:24`), target_first = 25 (SOURCED `CENSUS_15m_2026-10-03_11-07.md:24`) | OURS: 25 / 66 = 37.88% -> 38% | 0 | MATCH |
| 15m lower wick that is a sweep | 29 (SOURCED `WICKS_NOTE_2026-11-07.md:39`) | 45 % (SOURCED `WICKS_NOTE_2026-11-07.md:39`) | Sweep True: n = 29, target_first = 13 (SOURCED `CENSUS_15m_2026-10-03_11-07.md:30`) | OURS: 13 / 29 = 44.83% -> 45% | 0 | MATCH |
| *(non-sweep comparison in note)* | 37 (SOURCED `WICKS_NOTE_2026-11-07.md:39`) | 32 % (SOURCED `WICKS_NOTE_2026-11-07.md:39`) | Sweep False: n = 37, target_first = 12 (SOURCED `CENSUS_15m_2026-10-03_11-07.md:29`) | OURS: 12 / 37 = 32.43% -> 32% | 0 | MATCH |
| 15m lower V-sweep (multi-bar) | 62 (SOURCED `WICKS_NOTE_2026-11-07.md:40`) | 51 % (SOURCED `WICKS_NOTE_2026-11-07.md:40`) | knife False: n = 61, target_first = 31 (SOURCED `CENSUS_15m_2026-10-03_11-07.md:44`); knife True: n = 1, target_first = 0 (SOURCED `CENSUS_15m_2026-10-03_11-07.md:45`). Sum n = 61 + 1 = 62; sum target_first = 31 + 0 = 31 | OURS: 31 / 62 = 50.00% -> 50% | -1.0% (51% reported vs 50% recomputed) | **MISMATCH** |
| *(ASIA session breakdown in note)* | 19 (SOURCED `WICKS_NOTE_2026-11-07.md:40`) | 68 % (SOURCED `WICKS_NOTE_2026-11-07.md:40`) | ASIA: n = 19, target_first = 13 (SOURCED `CENSUS_15m_2026-10-03_11-07.md:50`) | OURS: 13 / 19 = 68.42% -> 68% | 0 | MATCH |
| *(US session breakdown in note)* | 20 (SOURCED `WICKS_NOTE_2026-11-07.md:40`) | 40 % (SOURCED `WICKS_NOTE_2026-11-07.md:40`) | US: n = 20, target_first = 8 (SOURCED `CENSUS_15m_2026-10-03_11-07.md:53`) | OURS: 8 / 20 = 40.00% -> 40% | 0 | MATCH |
| 15m upper wick, sweep / not | 24 / 42 (SOURCED `WICKS_NOTE_2026-11-07.md:41`) | 46 % / 48 % (SOURCED `WICKS_NOTE_2026-11-07.md:41`) | Sweep True: n = 24, target_first = 11 (SOURCED `CENSUS_15m_2026-10-03_11-07.md:83`); Sweep False: n = 42, target_first = 20 (SOURCED `CENSUS_15m_2026-10-03_11-07.md:82`) | OURS: 11 / 24 = 45.83% -> 46%; 20 / 42 = 47.62% -> 48% | 0 | MATCH |
| 5m lower V-sweep | 243 (SOURCED `WICKS_NOTE_2026-11-07.md:42`) | 47 % (SOURCED `WICKS_NOTE_2026-11-07.md:42`) | knife False: n = 241, target_first = 113 (SOURCED `CENSUS_5m_2026-10-03_11-07.md:45`); knife True: n = 2, target_first = 0 (SOURCED `CENSUS_5m_2026-10-03_11-07.md:46`). Sum n = 241 + 2 = 243; sum target_first = 113 | OURS: 113 / 243 = 46.50% -> 47% | 0 | MATCH |
| *(weekly range in note)* | - | 34-59 % (SOURCED `WICKS_NOTE_2026-11-07.md:42`) | Min week 2026-10-12: 20 / 58 = 34.48% -> 34% (SOURCED `CENSUS_5m_2026-10-03_11-07.md:37`); Max week 2026-10-26: 27 / 46 = 58.70% -> 59% (SOURCED `CENSUS_5m_2026-10-03_11-07.md:39`) | OURS: 34% to 59% | 0 | MATCH |
| 5m upper V-sweep | 230 (SOURCED `WICKS_NOTE_2026-11-07.md:43`) | 48 % (SOURCED `WICKS_NOTE_2026-11-07.md:43`) | knife False: n = 228, target_first = 110 (SOURCED `CENSUS_5m_2026-10-03_11-07.md:99`); knife True: n = 2, target_first = 1 (SOURCED `CENSUS_5m_2026-10-03_11-07.md:100`). Sum n = 228 + 2 = 230; sum target_first = 110 + 1 = 111 | OURS: 111 / 230 = 48.26% -> 48% | 0 | MATCH |
| knife-context wicks | 1-2 per table (SOURCED `WICKS_NOTE_2026-11-07.md:44`) | too rare to test | knife True counts per table: 15m LOW 1bar: 0 (SOURCED `CENSUS_15m_2026-10-03_11-07.md:24`); 15m LOW V: 1 (SOURCED `CENSUS_15m_2026-10-03_11-07.md:45`); 15m UP 1bar: 1 (SOURCED `CENSUS_15m_2026-10-03_11-07.md:77`); 15m UP V: 0 (SOURCED `CENSUS_15m_2026-10-03_11-07.md:98`); 5m LOW 1bar: 1 (SOURCED `CENSUS_5m_2026-10-03_11-07.md:25`); 5m LOW V: 2 (SOURCED `CENSUS_5m_2026-10-03_11-07.md:46`); 5m UP 1bar: 1 (SOURCED `CENSUS_5m_2026-10-03_11-07.md:78`); 5m UP V: 2 (SOURCED `CENSUS_5m_2026-10-03_11-07.md:100`) | OURS: 0 to 2 per table (non-zero tables have exactly 1 or 2 events) | 0 | MATCH |

---

### Section 3 Prose Metrics Recomputation

1. **Sweep edge on 15m**:
   - Prose: SOURCED `"adds about 13 points on 15m"` (`WICKS_NOTE_2026-11-07.md:46`).
   - Sourced: Sweep hit rate 45% (SOURCED `CENSUS_15m_2026-10-03_11-07.md:30`), non-sweep hit rate 32% (SOURCED `CENSUS_15m_2026-10-03_11-07.md:29`).
   - Recomputed: OURS: `44.83% - 32.43% = 12.40%` (or rounded: `45% - 32% = 13%`). MATCH.

2. **Weekly count and median progression**:
   - Prose: SOURCED `"lower wicks per week fell from 17 (10-05) to 8 (11-02) while the median wick grew (0.23 % to 0.28-0.35 %)"` (`WICKS_NOTE_2026-11-07.md:48-49`).
   - Sourced:
     - 2026-10-05: n = 17, median wick = 0.23% (SOURCED `CENSUS_15m_2026-10-03_11-07.md:7`).
     - 2026-10-12: n = 16, median wick = 0.23% (SOURCED `CENSUS_15m_2026-10-03_11-07.md:8`).
     - 2026-10-19: n = 14, median wick = 0.31% (SOURCED `CENSUS_15m_2026-10-03_11-07.md:9`).
     - 2026-10-26: n = 9, median wick = 0.35% (SOURCED `CENSUS_15m_2026-10-03_11-07.md:10`).
     - 2026-11-02: n = 8, median wick = 0.28% (SOURCED `CENSUS_15m_2026-10-03_11-07.md:11`).
   - Recomputed: Count fell from 17 to 8; median range across later weeks is 0.28% to 0.35%. MATCH.

---

## 3. Discrepancy Detail

- **Table 3, Row 3 Discrepancy**:
  - `WICKS_NOTE_2026-11-07.md:40` states: `| 15m lower V-sweep (multi-bar) | 62 | 51 % | ASIA 68 % (n 19), US 40 % (n 20) |`.
  - In `CENSUS_15m_2026-10-03_11-07.md:44-45`:
    - `knife=False`: n = 61, target_first = 31 -> rate is OURS `31 / 61 = 50.82% -> 51%`.
    - `knife=True`: n = 1, target_first = 0 -> rate is OURS `0 / 1 = 0%`.
    - Total events: n = 61 + 1 = 62. Total target_first = 31 + 0 = 31.
    - True overall rate across the stated n = 62 population is OURS `31 / 62 = 50.00% -> 50%`.
  - The prose took the 51% figure from the `knife=False` sub-row (where n = 61) but reported it in the row header alongside total n = 62. The diff is -1.0 percentage point (51% prose vs 50% data).

---

VERDICT: MISMATCH
