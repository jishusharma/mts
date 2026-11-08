# Layer Lab Report: `gemini-argon-krown-lows-break-check-1109` (2026-11-08 UTC)

**Card:** `gemini-argon-krown-lows-break-check-1109`
**Engine:** `gemini-4-argon-medium` (`JIS-NUC`)
**Deliverables:**
- `MyTradingSys/research/monday_open_2026-11-09/ARGON_CHECK.md:1-126`
- `MyTradingSys/research/monday_open_2026-11-09/krown_lows_break_check.py:1-326`

## 1. Reproduction & Verification Commands

```bash
python MyTradingSys/research/monday_open_2026-11-09/krown_lows_break_check.py --offline
python scripts/dev/verify_extract_quotes.py MyTradingSys/research/monday_open_2026-11-09/ARGON_CHECK.md
```

- **Fail-First Test:** On the pre-change worktree, `python scripts/dev/verify_extract_quotes.py MyTradingSys/research/monday_open_2026-11-09/ARGON_CHECK.md` exited `1` (`FileNotFoundError`). After writing `ARGON_CHECK.md` (`MyTradingSys/research/monday_open_2026-11-09/ARGON_CHECK.md:1-126`), it exits `0` (`PASS: 0 problem(s)`, `31` cited lines verified).

## 2. Key Empirical Numbers (`SOURCED` vs `OURS`)

1. **Current Market Context (`MyTradingSys/research/monday_open_2026-11-09/krown_lows_break_check.py:254-287`):**
   - `2026-11-08` `4h` close at `18:15Z`: `75,892` USD (**SOURCED**, `MyTradingSys/system/PLAN_5H_2026-11-08.md:10`, `"BTC close 4h | 75,892"`).
   - `2026-11-08` `1d` spot snapshot: `75,888.00` USD (**OURS**, `MyTradingSys/research/monday_open_2026-11-09/krown_lows_break_check.py:273`).
   - October 2026 monthly low: `76,325.98` USD on `2026-10-30` (**OURS**, `MyTradingSys/research/btc_cycles_2026-11/btc_daily.csv:5920`).
   - September 2026 swing low (`Sep-15`): `74,967.97` USD Binance / `74,961` USD Bybit (**OURS**, `MyTradingSys/research/btc_cycles_2026-11/btc_daily.csv:5875`; **SOURCED**, `MyTradingSys/research/cbp/PLAN_ADX_DI_VOLUME_2026-11-07.md:18`, `"Sep-15 low | 74,961 (74,968)"`).
   - November 2026 swing low (`Nov-6`): `74,888.00` USD Binance / `74,871` USD Bybit, closing back above at `75,844.00` USD (`75,771.76` CSV / `75,848` Bybit) (**OURS**, `MyTradingSys/research/btc_cycles_2026-11/btc_daily.csv:5927`; **SOURCED**, `MyTradingSys/system/PLAN_5H_2026-11-08.md:12`, `"Last swing low | 74,888 (11-06)"`).
   - `200-day SMA`: `73,228.74` USD on `2026-11-08` / `73,242` USD on `2026-11-06` (**OURS**, `MyTradingSys/research/monday_open_2026-11-09/krown_lows_break_check.py:281`; **SOURCED**, `MyTradingSys/research/mts_bible/BIBLE.md:60`, `"200d = 73,242"`).
   - `200-week SMA`: `67,765.66` USD on `2026-11-08` / `67,765` USD on `2026-11-06` (**OURS**, `MyTradingSys/research/monday_open_2026-11-09/krown_lows_break_check.py:282`; **SOURCED**, `MyTradingSys/research/mts_bible/BIBLE.md:60`, `"200w = 67,765"`).
   - `-10.0%` / `-10.6%` target from `74,888.00`: `67,399.20` USD / `66,949.87` USD (**OURS**, `MyTradingSys/research/monday_open_2026-11-09/krown_lows_break_check.py:283-284`).

2. **Calendar Monthly Low Breaks (`MyTradingSys/research/monday_open_2026-11-09/krown_lows_break_check.py:89-158`):**
   - Full History (`2011-02..2026-10`, `189` months [**OURS**]): `64` breaks (`33.9%` [**OURS**]); `35 / 64` (`54.7%` [**OURS**]) reached `>= 10.0%` below the prior month's low (median `-12.01%`, `75th` `-4.08%`, `25th` `-20.82%` [**OURS**]). On `2011-05..2026-09` (`185` months [**OURS**]), `n = 63` breaks (`35 / 63 = 55.6%` `>= 10%` down, median `-12.32%` [**OURS**]).
   - Modern Binance Spot Era (`2017-09..2026-10`, `110` months [**OURS**]): `40` breaks (`36.4%` [**OURS**]); only **`18 / 40` (`45.0%` [OURS])** reached `>= 10.0%` below the prior month's low, with a **median drop of `-8.43%` [OURS]**.
   - Day-1 Sweep & Reclaim (`close > prior_low`, `n = 22` in Binance era [**OURS**]): `>= 10%` monthly drop occurs in **`8 / 22` (`36.4%`, median `-4.55%` [OURS])** vs Day-1 Close Below (`close <= prior_low`, `n = 18` [**OURS**]) in **`10 / 18` (`55.6%`, median `-11.54%` [OURS])** (`27 / 42 = 64.3%`, median `-13.47%` in full history [**OURS**]).

3. **Rolling N-Day & Fractal Swing-Low Breaks (`2017-08-17..2026-11-08`, `3,371` Binance `1d` bars, `MyTradingSys/research/monday_open_2026-11-09/krown_lows_break_check.py:161-227`):**
   - **`50`-day rolling low first-break (`n = 67` [OURS], matching `52-day` gap from `2026-09-15` low `74,967.97` to `2026-11-06` low `74,888.00` [OURS]):**
     - Unconditional `>= 10%` drop: `43.3%` (`29 / 67`, med `-5.32%` [**OURS**]) in `7d`; `49.3%` (`33 / 67`, med `-8.42%` [**OURS**]) in `14d`; `52.2%` (`35 / 67`, med `-11.13%` [**OURS**]) in `30d`.
     - **Sweep & Reclaim (`close > prior_low`, `n = 40` [OURS]):** `32.5%` (`13 / 40`, med `-3.09%` [**OURS**]) in `7d`; `37.5%` (`15 / 40`, med `-4.02%` [**OURS**]) in `14d`; `40.0%` (`16 / 40`, med `-6.11%` [**OURS**]) in `30d`.
     - **Close Below (`close <= prior_low`, `n = 27` [OURS]):** `59.3%` (`16 / 27`, med `-11.79%` [**OURS**]) in `7d`; `66.7%` (`18 / 27`, med `-12.50%` [**OURS**]) in `14d`; `70.4%` (`19 / 27`, med `-13.59%` [**OURS**]) in `30d`.
   - **Confirmed `k = 7` fractal swing-low break (`n = 63` [OURS]):**
     - **Sweep & Reclaim (`n = 31` [OURS]):** `19.4%` (`6 / 31`, med `-3.24%` [**OURS**]) in `7d`; `22.6%` (`7 / 31`, med `-4.17%` [**OURS**]) in `14d`; `26.7%` (`8 / 30`, med `-5.17%` [**OURS**]) in `30d`.
     - **Close Below (`n = 32` [OURS]):** `56.2%` (`18 / 32`, med `-11.19%` [**OURS**]) in `7d`; `59.4%` (`19 / 32`, med `-12.07%` [**OURS**]) in `14d`; `75.0%` (`24 / 32`, med `-15.36%` [**OURS**]) in `30d`.

4. **Weekend Calls Table (`MyTradingSys/research/monday_open_2026-11-09/ARGON_CHECK.md:108-115`):**
   - Compiled `6` other analysts' calls for this week (Michael Pizzino `WHH4qSfCCyM` `2026-11-06`, Benjamin Cowen `2026-11-06`, CCU Steve `AnAx1PanZm4` `2026-11-05`, Qriptal/Habib `2026-11-05`, Jala `2026-11-06`, Jason Pizzino `2026-11-04` [**SOURCED** from `MyTradingSys/research/cbp/CBP_ALT_UPDATE_2026-11-07.md:9-16` and `MyTradingSys/research/cbp/PLAN_ADX_DI_VOLUME_2026-11-07.md:8-12`]), with raw video captions explicitly marked `UNVERIFIED` on `JIS-NUC` (`yt_guard` blocked until `2026-11-09T01:54:07Z`) and repo CBP quotes verified via `verify_extract_quotes.py`.
