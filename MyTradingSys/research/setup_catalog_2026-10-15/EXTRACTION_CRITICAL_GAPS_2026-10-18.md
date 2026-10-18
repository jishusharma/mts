# Critical Gaps in Tom & Fabio Layer Extractions and Setup Catalogue (2026-10-18)

**Session:** `MTS-20261018-1635Z-GEM-BLD-gemini-layer-gaps`
**Scope:** Full cross-audit of `MyTradingSys/research/setup_catalog_2026-10-15/SETUP_CATALOG.md`, `MyTradingSys/research/fable_audit_2026-10-16/CATALOGUE_AUDIT.md`, `MyTradingSys/research/layer_rebuild_2026-10-15/LAYER_REBUILD_PLAN_2026-10-15.md`, `extracts/v2/tom/`, `extracts/v2/fabio/`, `extracts/processed/tom/`, and `extracts/_staged_2026-09-27/` against `raw_transcripts_canonical/`.
**Verdict:** `FIX-FIRST` — **3 major extraction/catalogue gaps** found (5 "missing" Fabio transcripts + 4 Phase-1 extracts overlooked on disk, 1 unmerged Fabio V2 delta, and 28 Tom speaker videos + 1 V2 batch delta unmerged into `SETUP_CATALOG.md`). All 5 missing Fabio transcripts have now been promoted to `raw_transcripts_canonical/`.

---

## Executive Summary of Critical Gaps

| Gap ID | Severity | Layer | Finding Summary | Action Taken / Follow-up |
|---|---|---|---|---|
| **G-FAB-1** | **CRITICAL** | Fabio | **5 staged Fabio raw transcripts (`o-w5Gxss6T0`, `cUTsoU-15Tc`, `Khgj5q1-ln8`, `Pz8f0wWW12M`, `06R-ebyOhDI`) + 4 Phase-1 extracts** were sitting in `extracts/_staged_2026-09-27/` while `SETUP_CATALOG.md` (lines 835, 984), `CATALOGUE_AUDIT.md` (s3.4, line 82), and `LAYER_REBUILD_PLAN_2026-10-15.md` (s3, line 33) declared *"no source on disk / no quote can be verified"*. They directly supply the missing verbatim rules for **FAB-6 (IVB entry/stop/target)**, **FAB-8 (volume-defined FVG)**, **V3 Model A (LVN rebalance pivot)**, **U2 (delta absorption continuation vs exhaustion reversal)**, **daily bias hard filter**, **mandatory retest filter**, and **Delta Print / Volume Ledge** entry zones. | All 5 raw transcripts promoted to `raw_transcripts_canonical/<id>_raw.txt` in this commit; verbatim quotes verified below; follow-up card `fabio-catalogue-merge-5-recovered-canoni` filed. |
| **G-FAB-2** | **HIGH** | Fabio | **`extracts/v2/fabio/CATALOG_DELTA.md` (2026-10-15 V2 re-extraction of 8 canonical Fabio videos) was never merged into `SETUP_CATALOG.md`**: misses **FAB-7b** retest entry (`FawPrRUGNpk`), verbatim **FAB-6** source (`StaphlRH8NQ` verifying FR-81), **1% daily drawdown stop** (`0KyIEdvVKMQ`), and **Rulebook Error C5** (`FABIO_RULEBOOK.md` FR-13 falsely claims a 1:3 minimum R:R floor from `0jM5Y31YJak`). | Documented with verbatim quotes below; included in `fabio-catalogue-merge-5-recovered-canoni`. |
| **G-TOM-1** | **CRITICAL** | Tom | **28 of 85 Tom speaker videos in `transcript_inventory_2026-10-09.md` are completely absent from `SETUP_CATALOG.md`**, and **`extracts/v2/tom/CATALOG_DELTA_v1batch1.md` (12 V2 re-extractions) is unmerged**: includes **8 gate-PASS V2 extracts** (`5Ljfwvtktek`, `Of_wlv3xaZo`, `QClPWDJ-BrU`, `ShYS_pD5cxQ`, `UrZ4vpHJ97g`, `WSCIURybK3U`, `etg6j0JybfE`, `oPyUif2Zrtk`), **7 gate-PASS V1 extracts** (`7BQPMJ39WpI`, `HySZZSjMxF8`, `WQ_OAdz-PJ8`, `aursfDVYzUk`, `zAwEX_tRUfE`, `gWjHq5UMisY`, `pgdmKLJ0hhA`), and **15 V1-only / no-anchor videos** (`vk0mkNPuhDc` 5m scalping, `vl01TiVTuoQ`, `usho6UVLqkE`, `3JqMyzE8jIQ`, `Fj4FDZQxw0I`, `VumVuGnCcFM`, `y67l86cSqb8`, etc.). Also, `SETUP_CATALOG.md` s6.2 still lists 10 V1 videos as *"FAILS with NO-GPS"* even though their V2 extracts (`extracts/v2/tom/*_v2.md`) already exist and pass the gate. | Documented with verbatim quotes below; follow-up card `tom-catalogue-merge-8-unmerged-v2-extrac` filed. |

---

## 1. Critical Gap G-FAB-1: The 5 "Missing" Fabio Transcripts Found on Disk

`CATALOGUE_AUDIT.md` (s3.4, line 82) stated: *"o-w5Gxss6T0 has no transcript or video on disk."*
`SETUP_CATALOG.md` (lines 835, 984) stated: *"Source transcript o-w5Gxss6T0 is not in raw_transcripts_canonical: no quote can be verified."*

In fact, `extracts/_staged_2026-09-27/raw/` contained all 13 `fabervaale_*_raw.txt` files from the 2026-09-27 staging batch, including the 5 transcripts absent from `raw_transcripts_canonical/`, plus 4 Phase-1 extracts in `extracts/_staged_2026-09-27/extracts/fabio_valentini/extracts/` (`extract_o-w5Gxss6T0.md`, `extract_cUTsoU-15Tc.md`, `extract_Khgj5q1-ln8.md`, `extract_Pz8f0wWW12M.md`). All 5 raw transcripts are now in `raw_transcripts_canonical/`.

### 1.1 `o-w5Gxss6T0` ("3 Order-flow Trading Tricks Exposed!") — Sourced Rules for FAB-8 & Absorption

- **FAB-8 Volume-Defined Fair Value Gap (SOURCED, resolves `NOT_IN_DATA` on `SETUP_CATALOG.md:835,984`):**
  Fabio defines an FVG not from a 3-candle price gap alone, but by anchoring a fixed-range volume profile from swing point A to point B (70% value area) and picking the lowest-volume price inside the value area (`raw_transcripts_canonical/o-w5Gxss6T0_raw.txt:71-118`):

> "to identify a real fair value gap, you need to get inside the candle and you need to see how the volume transacted."
**Source GPS: o-w5Gxss6T0 | MIDDLE**

> "the lowest volume of interaction in all the area of value area. So where 70% of the volume got transacted is exactly this one is the level that goes from 24,318 to 24,317."
**Source GPS: o-w5Gxss6T0 | MIDDLE**

- **Failed Auction + CVD Divergence Confirmation (SOURCED, `raw_transcripts_canonical/o-w5Gxss6T0_raw.txt:150-165`):**
  When CVD makes a lower low while price fails to make a lower low (holds the prior low), passive buyers are absorbing aggressive sellers:

> "in this case you can see that we have a lower low on the cumulative volume delta here while the market is still on the same level as before. This is what it's called it's called absorption."
**Source GPS: o-w5Gxss6T0 | END**

### 1.2 `cUTsoU-15Tc` ("The Simplest Orderflow Trading Model") — Sourced Entry, Stop & Target for FAB-6 (IVB)

`SETUP_CATALOG.md` (line 822) currently marks **FAB-6 (Initial Volume Balance / IVB)**: *"Entry, stop, target, management: NOT STATED in the canonical transcripts."*
`cUTsoU-15Tc` is Fabio's dedicated 25-minute lecture on the IVB model (`raw_transcripts_canonical/cUTsoU-15Tc_raw.txt`):

- **IVB Construction & Core Order Block (SOURCED, `raw_transcripts_canonical/cUTsoU-15Tc_raw.txt:85-135`):**
  Anchor a fixed-range volume profile across the first 15 to 30 minutes of the NY open (point A to point B). The zone between the Value Area edge and the POC is the reload block:

> "the most sensitive level after you have this is the level contained between the value area and the PC. This is our real block of orders. This is where when you retrace you can expect buyers to reload."
**Source GPS: cUTsoU-15Tc | BEGIN**

- **IVB Model 1 Stop / Invalidation (SOURCED, `raw_transcripts_canonical/cUTsoU-15Tc_raw.txt:130-145`):**
  When price breaks out above the IVB and retraces into the VA-to-POC block, the stop / invalidation is a closed candle below VAL (risk is measured from entry to VAL, not the far side of the range):

> "So you have a value area low that if it gets broken, so the market accept it, it's an invalidation point."
**Source GPS: cUTsoU-15Tc | BEGIN**

- **IVB Model 2 Order-Flow Trigger & Stop (SOURCED, `raw_transcripts_canonical/cUTsoU-15Tc_raw.txt:150-450`):**
  Wait for price to retrace into the IVB POC/VA and confirm with either (a) seller absorption (heavy aggressive selling with zero downward progress) or (b) seller exhaustion + buyer momentum, placing the stop below the defended area and targeting the protection level:

> "Maybe we have a lot of aggressive sellers here with zero result. This means that there is a big absorption on this level on the PC."
**Source GPS: cUTsoU-15Tc | BEGIN**

> "when you have aggression of the buyers for example here okay they are protecting the area you can consider a buy with a stop loss below that goes to the protection level."
**Source GPS: cUTsoU-15Tc | END**

### 1.3 `Pz8f0wWW12M` ("The Only Orderflow Guide You'll Ever Need") — Sourced LVN Rebalance (V3 Model A) & U2 Discriminator

- **LVN Rebalance Pivot — Direct Verbatim Source for V3 Model A (SOURCED, `raw_transcripts_canonical/Pz8f0wWW12M_raw.txt:520-560`):**
  `SETUP_CATALOG.md` (lines 103, 851) and `LAYER_REBUILD_PLAN_2026-10-15.md` (line 80) state that V3 Model A ("LVN pullback trend") is *"OURS only... not a Fabio setup until a quote is found."*
  In `Pz8f0wWW12M`, Fabio explicitly teaches the LVN rebalance continuation setup:

> "Usually, the market like to rebalance the low volume node before continuing in the direction of the trend."
**Source GPS: Pz8f0wWW12M | MIDDLE**

> "When you have a low volume node and the market goes in price discovery, you can clearly see a lot of days the price coming back to rebalance in this low volume node and using this as a pivot before resuming the direction of the auction."
**Source GPS: Pz8f0wWW12M | MIDDLE**

- **U2 Discriminator: Delta Absorption Continuation vs Exhaustion Reversal (SOURCED, `raw_transcripts_canonical/Pz8f0wWW12M_raw.txt:330-420`):**
  Resolves Unresolved Tension U2 in `SETUP_CATALOG.md` (s3.4):
  1. **Continuation (Delta Absorption):** Counter-trend market orders are absorbed inside the candle while the candle still closes in the trend direction:
  2. **Reversal (Exhaustion + Contrarian Imbalance):** Volume declines into the extreme ("dry up in volume") and a contrarian imbalance prints at the high/low:

> "we have a market that is in a consolidation phase here, and we can spot that all these aggressive market participants here got absorbed and the candle closed green. This is a potential continuation of the move"
**Source GPS: Pz8f0wWW12M | MIDDLE**

> "from the concept of vertical volume you can find an exhaustion where you can see that the market is pushing really strong, printing another green candle, but the volume is getting lower and lower. This is a dry up in volume, and usually what you see this in a pattern order flow is that you have a sudden reversal in price."
**Source GPS: Pz8f0wWW12M | MIDDLE**

- **P-Shape Profile Bullish Bias & VAL "Hook" Continuation (SOURCED, `raw_transcripts_canonical/Pz8f0wWW12M_raw.txt:550-650`):**

> "We have the value building on the upside. This is what we call the P shape. It's where the buyers are really aggressive and you close the cash session on the upside, so you can expect a directional move also on the day after."
**Source GPS: Pz8f0wWW12M | MIDDLE**

> "when we go back to the value area low and down, we do what we call the hook. So, they do a failed auction, they try to break, they get rejected. So, all this it's a rejection area, and when you go back inside, you have your continuation trade"
**Source GPS: Pz8f0wWW12M | MIDDLE**

### 1.4 `Khgj5q1-ln8` ("My Signature Orderflow Model") — Daily Bias Filter, Mandatory Retest & Opposing-Signal Exit

- **Daily Bias Hard Filter & Mandatory Retest Rule (SOURCED, `raw_transcripts_canonical/Khgj5q1-ln8_raw.txt:150-245`):**
  In `Khgj5q1-ln8`, Fabio combines "deep effort" (big trades) + "profile framing" to set a single daily direction (skipping counter-trend trades), and states a hard rejection rule: if a momentum candle closes above the area **without a retest**, he skips the trade (`FAB-020`):

> "So, I had a clear bias for the day and for this I use profile framing. So, all the short setup if I have a bias, I'm not interested into taking, okay? So, I can save the counter trend setups."
**Source GPS: Khgj5q1-ln8 | MIDDLE**

> "This one it's a momentum setup. Why momentum setup? Because it closed above it and never test. So, this one you couldn't take because the market don't give you a test."
**Source GPS: Khgj5q1-ln8 | MIDDLE**

> "And in situation of long momentum, it's not so difficult to take amazing risk to reward by covering below the areas, okay?"
**Source GPS: Khgj5q1-ln8 | END**

### 1.5 `06R-ebyOhDI` ("How To Find The BEST Entry Zones") — Delta Print & Volume Ledge Setups

Never extracted in V1 or V2 (`raw_transcripts_canonical/06R-ebyOhDI_raw.txt:1-162`). Teaches two specific order-flow entry zone models:
1. **Delta Print (`06R-ebyOhDI_raw.txt:1-87`):** Pull a fixed profile over the swing leg; where big trades + delta pressure + VAH align is the reload zone to enter on a retest with stop above the area (`1:3` to `1:5` R:R).
2. **Volume Ledge (`06R-ebyOhDI_raw.txt:98-155`):** A sharp drop from peak volume to low volume on the fixed profile combined with absorbed counter-traders inside the candle body marks the exact limit-order retrace level:

> "Specifically, we will see one indicator that show you the exact area called delta print."
**Source GPS: 06R-ebyOhDI | BEGIN**

> "So you have a confluence of value area high, big trades and delta level. This one is a super strong area."
**Source GPS: 06R-ebyOhDI | BEGIN**

> "Volume ledge is where the the volume goes from really peak point to really low point. Okay? So from high volume node to low volume node really fast."
**Source GPS: 06R-ebyOhDI | MIDDLE**

---

## 2. Critical Gap G-FAB-2: Unmerged `extracts/v2/fabio/CATALOG_DELTA.md`

On 2026-10-15, a V2 re-extraction of the 8 original canonical Fabio transcripts produced `extracts/v2/fabio/CATALOG_DELTA.md`, which has still not been merged into `SETUP_CATALOG.md`:

1. **FAB-7b (Retest Entry in `FawPrRUGNpk_raw.txt`):** `SETUP_CATALOG.md` moved `FAB-7` out of the setup list as a "chart element only", missing that `FawPrRUGNpk` explicitly defines an executable retest entry (`FAB-7b`) with a structural stop and `1:2`–`1:3` R:R:

> "I can enter on the test"
**Source GPS: FawPrRUGNpk | MIDDLE**

> "protect myself below the wall reload"
**Source GPS: FawPrRUGNpk | MIDDLE**

2. **FAB-6 Verbatim Source (`StaphlRH8NQ_raw.txt`):** `SETUP_CATALOG.md` (line 822) says FR-81 is an unverified rulebook paraphrase. In fact, `StaphlRH8NQ` has the exact verbatim quote:

> "The initial balance represent the high and low price established during the first 30 minutes of a regular cash trading"
**Source GPS: StaphlRH8NQ | MIDDLE**

3. **1% Daily Drawdown Stop (`0KyIEdvVKMQ_raw.txt`):** Missing from `SETUP_CATALOG.md` Section 2.2:

> "If I reach 1% of draw down, I stop for the day."
**Source GPS: 0KyIEdvVKMQ | END**

4. **Rulebook Error C5 (`FABIO_RULEBOOK.md` FR-13):** FR-13 claims *"Minimum 1:3 reward-to-risk on initial trades"* from `0jM5Y31YJak_raw.txt`, where Fabio only narrates a realized trade outcome, not a minimum R:R filter:

> "almost 1 to three even more 1:5 risk-to-reward ratio"
**Source GPS: 0jM5Y31YJak | MIDDLE**

---

## 3. Critical Gap G-TOM-1: 28 Tom Speaker Videos & V2 Batch 1 Delta Missing from `SETUP_CATALOG.md`

### 3.1 Stale V1-Only Table in `SETUP_CATALOG.md` Section 6.2 (10 Videos Already V2-Extracted)

`SETUP_CATALOG.md` s6.2 (lines 966-974) still flags `BVpYGKz9PBU`, `43JaKHRvxHk`, `qLnQan0KGmQ`, `Ld1dhjGdTCA`, `NkQeOVDTAec`, `YmygDgtoxO8`, `YVUcLTsCOZI`, `k0zm5NYn0IQ`, `n7ZSkjb7JXs`, and `ujedEcmvBMk` as *"V1 only — gate FAILS with NO-GPS"*.
In reality, all 10 were re-extracted into `extracts/v2/tom/*_v2.md` (with `PASS: 0 problem(s)`) and summarized in `extracts/v2/tom/CATALOG_DELTA_v1batch1.md`, which adds:
- **`BVpYGKz9PBU`:** 3-level confirmation hierarchy (Price -> Volume -> Order flow) and finished-auction definition (`"Zero. Either on the bid or the ask side."`).
- **`43JaKHRvxHk`:** VWAP execution rules (trade only 1st/2nd touch; 1st touch of prior-day closing VWAP as reversal; 2SD band as profit target or counter trigger).
- **`qLnQan0KGmQ`:** Range-breakout volume condition (rising volume on breakout + declining volume on pullback to upper edge; falling volume on breakout = fakeout back into range).
- **`n7ZSkjb7JXs` & `ujedEcmvBMk`:** Explicit trade management (12-tick stop at 659.75 -> 40-tick partial on 2 of 4 contracts -> trail 1 tick above big trade -> runner to 632.75 in `n7ZSkjb7JXs`; 50-point target missed by 1 tick when exiting on counter-aggression in `ujedEcmvBMk`).

### 3.2 8 Gate-PASS V2 Extracts in `extracts/v2/tom/` Completely Absent from `SETUP_CATALOG.md`

None of the following 8 V2 extracts (`extracts/v2/tom/*_v2.md`, all passing `verify_extract_quotes.py`) are cited anywhere in `SETUP_CATALOG.md`:

1. **`5Ljfwvtktek_v2.md` ("Trader Reacts to Trade Execution of Unprofitable Student"):**
   - FVG long entry after structure break + pullback into the FVG (`raw_transcripts_canonical/5Ljfwvtktek_raw.txt:7`):
   - Counter-long stop placed below the previous day's low (`5Ljfwvtktek_raw.txt:7`):
   - Exact footprint trigger: finished auction at the low + rising CVD (`5Ljfwvtktek_raw.txt:7`):

> "So, and now it runs up to the fair value gap and that is where you make your entry."
**Source GPS: 5Ljfwvtktek | BEGIN**

> "is suddenly in a price range where the market goes below the previous day's low and most likely continues its downtrend. So, it's a much more logical level."
**Source GPS: 5Ljfwvtktek | MIDDLE**

> "You see a finished auction down here. You see that the cumulative delta is rising down here."
**Source GPS: 5Ljfwvtktek | MIDDLE**

2. **`Of_wlv3xaZo_v2.md` ("1,000,000 Trader Battle Episode 3"):**
   - First-30-minute NY cash-open filter + opening-range width day-type classifier (`raw_transcripts_canonical/Of_wlv3xaZo_raw.txt:7`):
   - Cash-session profile rule when trading cash hours (`Of_wlv3xaZo_raw.txt:7`):

> "stop trading in the first 30 minutes of the New York session, and secondly, look at how big the open range is"
**Source GPS: Of_wlv3xaZo | MIDDLE**

> "If you see at the open after 30 minutes, thereby negating this problem here that the open is relatively narrow, then you can assume the market will likely trend after that."
**Source GPS: Of_wlv3xaZo | BEGIN**

3. **`QClPWDJ-BrU_v2.md` ("This is How You Actually Trade Profitably!"):**
   - Pre-session day-trade plan (long at 62, stop at 52 below last swing low, target 80 where liquidity fades, R:R 1.8) + swing-trade limit-buy plan at acceptance (entry 7,443, stop 7,420 below last high-liquidity station, target 7,513 just below next volume level, R:R 3.04) (`raw_transcripts_canonical/QClPWDJ-BrU_raw.txt:7`):

> "Where was the last time there was high liquidity?"
**Source GPS: QClPWDJ-BrU | MIDDLE**

> "The trade has an entry at 7,443, stop loss 7,420, take profit 7,513."
**Source GPS: QClPWDJ-BrU | MIDDLE**

4. **`etg6j0JybfE_v2.md` ("The Ultimate Swing Trading Strategy 2026"):**
   - Swing horizon (3–8 days), shrinking-corrections trend health proof, stop = entry minus largest past correction, minimum target = prior up-swing distances projected from entry (`raw_transcripts_canonical/etg6j0JybfE_raw.txt:7`):

> "this is the absolute maximum it has gone down in the past."
**Source GPS: etg6j0JybfE | END**

> "this level right here is now my defined risk. That's where I put my stop loss."
**Source GPS: etg6j0JybfE | END**

5. **`oPyUif2Zrtk_v2.md` ("Forget Candlestick Charts... Use THIS Instead!"):**
   - Return-to-greatest-liquidity rule (valid only after price breaks below the range low; holding above targets further highs) + 30-minute market-profiling chart rule (`raw_transcripts_canonical/oPyUif2Zrtk_raw.txt:7`).
6. **`ShYS_pD5cxQ_v2.md` ("The Easiest Way to Start Day Trading")** & **`UrZ4vpHJ97g_v2.md` ("The PERFECT risk-reward ratio")** & **`WSCIURybK3U_v2.md` ("The #1 Reason Traders Lose"):**
   - Sourced risk/sizing rules: 20% maximum business drawdown rule (`0.5%`–`0.7%` per-trade risk derived from strategy hit rate and losing streaks over 200–400 trades), never delete the predefined target (`UrZ4vpHJ97g_raw.txt:19`).

### 3.3 7 Gate-PASS V1 Extracts in `extracts/processed/tom/` Unmerged into Any Setup Row

Five videos in `extracts/processed/tom/new_selected_10/` (`7BQPMJ39WpI`, `HySZZSjMxF8`, `WQ_OAdz-PJ8`, `aursfDVYzUk`, `zAwEX_tRUfE`) and two swing videos (`gWjHq5UMisY`, `pgdmKLJ0hhA`) pass `verify_extract_quotes.py` but are not merged into `SETUP_CATALOG.md`:
- **`zAwEX_tRUfE` ("My Simple 1-Minute Scalping Strategy"):** Directly fills **TOM-7 (1m scalping)** gaps: uses prior-day equilibrium & VAH on 1m chart, targets upper edge of equilibrium, warns that placing stop below last 1m low yields R:R < 1, and exits immediately if price re-accepts the old equilibrium (`raw_transcripts_canonical/zAwEX_tRUfE_raw.txt:7`):

> "if I now book this trade here, as I just showed, I can plan it up to the upper edge of the equilibrium"
**Source GPS: zAwEX_tRUfE | BEGIN**

> "you're out relatively quickly down here if the market accepts the old equilibrium again"
**Source GPS: zAwEX_tRUfE | END**

- **`7BQPMJ39WpI` ("How to Trade Gold in 2026"):** Gives Tom's **impulse duplication target rule** for breakout continuation (`raw_transcripts_canonical/7BQPMJ39WpI_raw.txt:7`):

> "You can see how large the first impulse stretch was and simply duplicate that onto the second one. As simply as I'm explaining it right now and as simple as it sounds, that's how simple it's allowed to be."
**Source GPS: 7BQPMJ39WpI | MIDDLE**

- **`HySZZSjMxF8` ("Ultimate Multi-Timeframe Strategy"):** Explicit stop placement just above the prior swing high after volume exhaustion at pre-located highs (`raw_transcripts_canonical/HySZZSjMxF8_raw.txt:7`):

> "I can confidently say that my next stop loss is positioned just above this level. Right here, where the market previously set that swing high."
**Source GPS: HySZZSjMxF8 | END**

- **`pgdmKLJ0hhA` ("How I Made 6,000 EUR With 1 Trade (Swing Trading)"):** Concrete swing trade with entry above volume support, stop below volume support, and R:R 2.41 (`raw_transcripts_canonical/pgdmKLJ0hhA_raw.txt:19`).

### 3.4 15 Remaining Tom Speaker Videos in Inventory Never Merged or Re-Extracted to V2

The following 15 Tom-speaker videos in `transcript_inventory_2026-10-09.md` have raw transcripts in `raw_transcripts_canonical/` and V1 extracts that currently fail the quote/GPS gate or lack V2 extraction, and have **zero citations** in `SETUP_CATALOG.md`:
- Strategy/setup videos (high priority for V2 extraction):
  - `vk0mkNPuhDc` ("My Simple 5-Minute Scalping Strategy")
  - `vl01TiVTuoQ` ("Master Orderflow Trading")
  - `usho6UVLqkE` ("Orderflow System that 95% of Traders do NOT know")
  - `3JqMyzE8jIQ` ("How to Trade Fair Value Gaps in 2026")
  - `Fj4FDZQxw0I` ("Fair Value Gap Trading: Avoid This Common Mistake!")
  - `VumVuGnCcFM` ("The ONLY Trading Indicator You Need (VWAP)!")
  - `y67l86cSqb8` ("Cumulative Volume Delta (CVD) Trading Strategy")
  - `C9n_d91Uitc` ("Why Your Day Trading Strategy Stopped Working")
  - `sQ_biBKhPVU` ("The Volume Trading Blueprint for Beginners")
- General / psychology / indicator critiques (lower priority):
  - `-dMWA_bbm3o`, `9eHZMVXilgc`, `KEe_CWHyuSg`, `e6Gm1n2h05M`, `rrHj24GSR6M`, `v5EuDl9c0iI`.

---

## Verification Gate

```
python scripts/dev/verify_extract_quotes.py MyTradingSys/research/setup_catalog_2026-10-15/EXTRACTION_CRITICAL_GAPS_2026-10-18.md
```
