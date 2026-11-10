FOUND: 6 | DIFF: 0 | NOT_IN_DATA: 34

# Blind Read of `MyTradingSys/research/cbp/INDIAN_EXCHANGE_FEES_2026-11-03.md`

- **Card**: `gemini-blind-read-indian-fees-1103` (`OURS`)
- **Audited Document**: `MyTradingSys/research/cbp/INDIAN_EXCHANGE_FEES_2026-11-03.md` (`SOURCED`: commit `5fb3ce500d04`, lines `1-16`)
- **Cross-Checked Directory**: `MyTradingSys/research/cbp/` (`12` peer files read/grepped; `0` stored Indian exchange spot fee schedule files in `MyTradingSys/research/cbp/` or `MyTradingSys/cbp/`, `OURS`)
- **Counts Breakdown**:
  - **Strict CBP-store / internal-arithmetic audit (Line 1)**: `FOUND: 6 | DIFF: 0 | NOT_IN_DATA: 34` (`40` total numeric tokens in `INDIAN_EXCHANGE_FEES_2026-11-03.md:1-16`, `OURS`).
    - The `6` `FOUND` rows are:
      1. `2026-11-03` header check date (`INDIAN_EXCHANGE_FEES_2026-11-03.md:1`), corroborated by `SISTER_NOTE_2026-11-03.md:1` (`"3 Nov 2026"`, `SOURCED`) and commit `5fb3ce500d04` (`SOURCED`).
      2. `30 %` tax on VDA gains (`INDIAN_EXCHANGE_FEES_2026-11-03.md:14`), corroborated in the CBP folder by `SISTER_NOTE_2026-11-03.md:28` (`"Every sale has 1% TDS cut and 30% tax on profit"`, `SOURCED`).
      3. `1 %` TDS on every sale (`INDIAN_EXCHANGE_FEES_2026-11-03.md:14`), corroborated in the CBP folder by `SISTER_NOTE_2026-11-03.md:28` (`"Every sale has 1% TDS cut and 30% tax on profit"`, `SOURCED`).
      4. `about 0.9 %` INR-native retail round trip before GST and TDS (`INDIAN_EXCHANGE_FEES_2026-11-03.md:16`), derived by exact arithmetic from the ZebPay and Mudrex base spot tiers in `INDIAN_EXCHANGE_FEES_2026-11-03.md:7-8`: `2 * 0.45% = 0.90%` (`OURS`; including `18 %` GST on fees `INDIAN_EXCHANGE_FEES_2026-11-03.md:7,14`, `0.90% * 1.18 = 1.062%`, `OURS`).
      5. `about 0.2 %` Binance VIP 0 round trip (`INDIAN_EXCHANGE_FEES_2026-11-03.md:16`), derived by exact arithmetic from the Binance VIP 0 maker/taker row in `INDIAN_EXCHANGE_FEES_2026-11-03.md:12`: `2 * 0.1% = 0.20%` (`OURS`; with BNB discount `2 * 0.075% = 0.15%`, `OURS`).
      6. `1 %` TDS per sale in the closing read (`INDIAN_EXCHANGE_FEES_2026-11-03.md:16`), matching `INDIAN_EXCHANGE_FEES_2026-11-03.md:14` (`"1 % TDS on every sale"`, `SOURCED`) and `SISTER_NOTE_2026-11-03.md:28` (`"Every sale has 1% TDS cut"`, `SOURCED`).
    - The `34` `NOT_IN_DATA` rows are all external web-page / third-party-site / memory claims in `INDIAN_EXCHANGE_FEES_2026-11-03.md:7-14` (`ZebPay`, `Mudrex`, `CoinDCX`, `CoinSwitch`, `WazirX`, `Binance`, and `Budget 2026-27` / `GST` / URL IDs), because no fee schedule pages or raw HTML/JSON snapshots for those venues are stored anywhere in `MyTradingSys/research/cbp/` or `MyTradingSys/cbp/` (and no web fetch is permitted per card scope, `OURS`).

---

## 1. Number-by-Number Audit Table (`INDIAN_EXCHANGE_FEES_2026-11-03.md:1-16`)

| # | Source Line | Table Row / Section | Number in Doc (`SOURCED`) | Context / Quote (`SOURCED`) | Our Figure / CBP Store Check (`OURS` / `SOURCED`) | Status |
|---|---|---|---|---|---|---|
| 1 | `INDIAN_EXCHANGE_FEES_2026-11-03.md:1` | Title / Header | `2026-11-03` | `# Indian exchange fees for buying alts (checked 2026-11-03, Eagle_Eyes)` (`INDIAN_EXCHANGE_FEES_2026-11-03.md:1`) | `2026-11-03` (`SOURCED`: `SISTER_NOTE_2026-11-03.md:1` `"# Crypto note, 3 Nov 2026"`; commit `5fb3ce500d04` date `2026-11-03`) | `FOUND` |
| 2 | `INDIAN_EXCHANGE_FEES_2026-11-03.md:7` | Row 1 (`ZebPay`) | `0.45 %` | `0.45 % maker and taker under Rs 5 lakh 30-day volume` (`INDIAN_EXCHANGE_FEES_2026-11-03.md:7`) | `NOT_IN_DATA` in CBP files (`0` hits for `zebpay` or `0.45` outside `INDIAN_EXCHANGE_FEES_2026-11-03.md`; page-only claim from `zebpay.com/in/fees`, `OURS`) | `NOT_IN_DATA` |
| 3 | `INDIAN_EXCHANGE_FEES_2026-11-03.md:7` | Row 1 (`ZebPay`) | `Rs 5 lakh` (1st) | `0.45 % maker and taker under Rs 5 lakh 30-day volume` (`INDIAN_EXCHANGE_FEES_2026-11-03.md:7`) | `NOT_IN_DATA` in CBP files (`0` hits for `lakh` outside `INDIAN_EXCHANGE_FEES_2026-11-03.md`; page-only claim from `zebpay.com/in/fees`, `OURS`) | `NOT_IN_DATA` |
| 4 | `INDIAN_EXCHANGE_FEES_2026-11-03.md:7` | Row 1 (`ZebPay`) | `30-day` (`30`) | `under Rs 5 lakh 30-day volume` (`INDIAN_EXCHANGE_FEES_2026-11-03.md:7`) | `NOT_IN_DATA` in CBP files (page-only volume window from `zebpay.com/in/fees`, `OURS`) | `NOT_IN_DATA` |
| 5 | `INDIAN_EXCHANGE_FEES_2026-11-03.md:7` | Row 1 (`ZebPay`) | `0.18 %` | `0.18 % from Rs 5 lakh` (`INDIAN_EXCHANGE_FEES_2026-11-03.md:7`) | `NOT_IN_DATA` in CBP files (`0` hits for `0.18` outside `INDIAN_EXCHANGE_FEES_2026-11-03.md`; page-only claim from `zebpay.com/in/fees`, `OURS`) | `NOT_IN_DATA` |
| 6 | `INDIAN_EXCHANGE_FEES_2026-11-03.md:7` | Row 1 (`ZebPay`) | `Rs 5 lakh` (2nd) | `0.18 % from Rs 5 lakh` (`INDIAN_EXCHANGE_FEES_2026-11-03.md:7`) | `NOT_IN_DATA` in CBP files (page-only tier threshold from `zebpay.com/in/fees`, `OURS`) | `NOT_IN_DATA` |
| 7 | `INDIAN_EXCHANGE_FEES_2026-11-03.md:7` | Row 1 (`ZebPay`) | `0.13 %` | `0.13 % from Rs 75 lakh` (`INDIAN_EXCHANGE_FEES_2026-11-03.md:7`) | `NOT_IN_DATA` in CBP files (`0` hits for `0.13` outside `INDIAN_EXCHANGE_FEES_2026-11-03.md`; page-only claim from `zebpay.com/in/fees`, `OURS`) | `NOT_IN_DATA` |
| 8 | `INDIAN_EXCHANGE_FEES_2026-11-03.md:7` | Row 1 (`ZebPay`) | `Rs 75 lakh` | `0.13 % from Rs 75 lakh` (`INDIAN_EXCHANGE_FEES_2026-11-03.md:7`) | `NOT_IN_DATA` in CBP files (page-only tier threshold from `zebpay.com/in/fees`, `OURS`) | `NOT_IN_DATA` |
| 9 | `INDIAN_EXCHANGE_FEES_2026-11-03.md:7` | Row 1 (`ZebPay`) | `18 %` | `plus 18 % GST` (`INDIAN_EXCHANGE_FEES_2026-11-03.md:7`) | `NOT_IN_DATA` in CBP files (`0` hits for `GST` or `18 %` outside `INDIAN_EXCHANGE_FEES_2026-11-03.md:7,14`; page-only claim, `OURS`) | `NOT_IN_DATA` |
| 10 | `INDIAN_EXCHANGE_FEES_2026-11-03.md:7` | Row 1 (`ZebPay`) | `Rs 15` | `INR withdrawal Rs 15` (`INDIAN_EXCHANGE_FEES_2026-11-03.md:7`) | `NOT_IN_DATA` in CBP files (page-only withdrawal fee from `zebpay.com/in/fees`, `OURS`) | `NOT_IN_DATA` |
| 11 | `INDIAN_EXCHANGE_FEES_2026-11-03.md:7` | Row 1 (`ZebPay`) | `2024-10-12` | `zebpay.com/in/fees (schedule effective 2024-10-12)` (`INDIAN_EXCHANGE_FEES_2026-11-03.md:7`) | `NOT_IN_DATA` in CBP files (page-only schedule effective date from `zebpay.com/in/fees`, `OURS`) | `NOT_IN_DATA` |
| 12 | `INDIAN_EXCHANGE_FEES_2026-11-03.md:8` | Row 2 (`Mudrex`) | `0.45 %` | `0.45 % under Rs 2 lakh` (`INDIAN_EXCHANGE_FEES_2026-11-03.md:8`) | `NOT_IN_DATA` in CBP files (`0` hits for `mudrex` or `0.45` outside `INDIAN_EXCHANGE_FEES_2026-11-03.md`; page-only claim from `mudrex.com/fee`, `OURS`) | `NOT_IN_DATA` |
| 13 | `INDIAN_EXCHANGE_FEES_2026-11-03.md:8` | Row 2 (`Mudrex`) | `Rs 2 lakh` (1st) | `0.45 % under Rs 2 lakh` (`INDIAN_EXCHANGE_FEES_2026-11-03.md:8`) | `NOT_IN_DATA` in CBP files (page-only tier threshold from `mudrex.com/fee`, `OURS`) | `NOT_IN_DATA` |
| 14 | `INDIAN_EXCHANGE_FEES_2026-11-03.md:8` | Row 2 (`Mudrex`) | `0.42 %` | `0.42 % from Rs 2 lakh` (`INDIAN_EXCHANGE_FEES_2026-11-03.md:8`) | `NOT_IN_DATA` in CBP files (`0` hits for `0.42` outside `INDIAN_EXCHANGE_FEES_2026-11-03.md`; page-only claim from `mudrex.com/fee`, `OURS`) | `NOT_IN_DATA` |
| 15 | `INDIAN_EXCHANGE_FEES_2026-11-03.md:8` | Row 2 (`Mudrex`) | `Rs 2 lakh` (2nd) | `0.42 % from Rs 2 lakh` (`INDIAN_EXCHANGE_FEES_2026-11-03.md:8`) | `NOT_IN_DATA` in CBP files (page-only tier threshold from `mudrex.com/fee`, `OURS`) | `NOT_IN_DATA` |
| 16 | `INDIAN_EXCHANGE_FEES_2026-11-03.md:8` | Row 2 (`Mudrex`) | `0.25 %` | `0.25 % from Rs 10 lakh` (`INDIAN_EXCHANGE_FEES_2026-11-03.md:8`) | `NOT_IN_DATA` in CBP files (`0` hits for `0.25` outside `INDIAN_EXCHANGE_FEES_2026-11-03.md`; page-only claim from `mudrex.com/fee`, `OURS`) | `NOT_IN_DATA` |
| 17 | `INDIAN_EXCHANGE_FEES_2026-11-03.md:8` | Row 2 (`Mudrex`) | `Rs 10 lakh` | `0.25 % from Rs 10 lakh` (`INDIAN_EXCHANGE_FEES_2026-11-03.md:8`) | `NOT_IN_DATA` in CBP files (page-only tier threshold from `mudrex.com/fee`, `OURS`) | `NOT_IN_DATA` |
| 18 | `INDIAN_EXCHANGE_FEES_2026-11-03.md:8` | Row 2 (`Mudrex`) | `0.22 %` | `0.22 % from Rs 75 lakh` (`INDIAN_EXCHANGE_FEES_2026-11-03.md:8`) | `NOT_IN_DATA` in CBP files (`0` hits for `0.22` outside `INDIAN_EXCHANGE_FEES_2026-11-03.md`; page-only claim from `mudrex.com/fee`, `OURS`) | `NOT_IN_DATA` |
| 19 | `INDIAN_EXCHANGE_FEES_2026-11-03.md:8` | Row 2 (`Mudrex`) | `Rs 75 lakh` | `0.22 % from Rs 75 lakh` (`INDIAN_EXCHANGE_FEES_2026-11-03.md:8`) | `NOT_IN_DATA` in CBP files (page-only tier threshold from `mudrex.com/fee`, `OURS`) | `NOT_IN_DATA` |
| 20 | `INDIAN_EXCHANGE_FEES_2026-11-03.md:9` | Row 3 (`CoinDCX`) | `0.1 %` | `0.1 % to 0.5 % depending on the source` (`INDIAN_EXCHANGE_FEES_2026-11-03.md:9`) | `NOT_IN_DATA` in CBP files (`0` hits for `coindcx` outside `INDIAN_EXCHANGE_FEES_2026-11-03.md`; third-party site claim, `OURS`) | `NOT_IN_DATA` |
| 21 | `INDIAN_EXCHANGE_FEES_2026-11-03.md:9` | Row 3 (`CoinDCX`) | `0.5 %` | `0.1 % to 0.5 % depending on the source` (`INDIAN_EXCHANGE_FEES_2026-11-03.md:9`) | `NOT_IN_DATA` in CBP files (third-party site claim, `OURS`) | `NOT_IN_DATA` |
| 22 | `INDIAN_EXCHANGE_FEES_2026-11-03.md:9` | Row 3 (`CoinDCX`) | `0.02` (`0.02 %`) | `futures 0.02 / 0.05 % consistent` (`INDIAN_EXCHANGE_FEES_2026-11-03.md:9`) | `NOT_IN_DATA` in CBP files (third-party site futures maker fee claim, `OURS`) | `NOT_IN_DATA` |
| 23 | `INDIAN_EXCHANGE_FEES_2026-11-03.md:9` | Row 3 (`CoinDCX`) | `0.05 %` | `futures 0.02 / 0.05 % consistent` (`INDIAN_EXCHANGE_FEES_2026-11-03.md:9`) | `NOT_IN_DATA` in CBP files (third-party site futures taker fee claim; `SCORECARD_GPT.md:14` `0.05%` is Deribit taker fee, not CoinDCX, `OURS`) | `NOT_IN_DATA` |
| 24 | `INDIAN_EXCHANGE_FEES_2026-11-03.md:9` | Row 3 (`CoinDCX`) | `403` | `fee page returned 403` (`INDIAN_EXCHANGE_FEES_2026-11-03.md:9`) | `NOT_IN_DATA` in CBP files (live HTTP status code on check day, `OURS`) | `NOT_IN_DATA` |
| 25 | `INDIAN_EXCHANGE_FEES_2026-11-03.md:10` | Row 4 (`CoinSwitch`) | `0.04 %` | `0.04 % to 0.5 % depending on the source` (`INDIAN_EXCHANGE_FEES_2026-11-03.md:10`) | `NOT_IN_DATA` in CBP files (`0` hits for `coinswitch` outside `INDIAN_EXCHANGE_FEES_2026-11-03.md`; third-party site claim, `OURS`) | `NOT_IN_DATA` |
| 26 | `INDIAN_EXCHANGE_FEES_2026-11-03.md:10` | Row 4 (`CoinSwitch`) | `0.5 %` | `0.04 % to 0.5 % depending on the source` (`INDIAN_EXCHANGE_FEES_2026-11-03.md:10`) | `NOT_IN_DATA` in CBP files (third-party site claim, `OURS`) | `NOT_IN_DATA` |
| 27 | `INDIAN_EXCHANGE_FEES_2026-11-03.md:10` | Row 4 (`CoinSwitch`) | `March 2026` (`2026`) | `"zero-fee race" claim March 2026` (`INDIAN_EXCHANGE_FEES_2026-11-03.md:10`) | `NOT_IN_DATA` in CBP files (third-party site date claim, `OURS`) | `NOT_IN_DATA` |
| 28 | `INDIAN_EXCHANGE_FEES_2026-11-03.md:11` | Row 5 (`WazirX`) | `Rs 99` | `ZERO plan Rs 99 per month, zero spot fee claimed` (`INDIAN_EXCHANGE_FEES_2026-11-03.md:11`) | `NOT_IN_DATA` in CBP files (`0` hits for `wazirx` or `99` outside `INDIAN_EXCHANGE_FEES_2026-11-03.md`; third-party partner piece claim, `OURS`) | `NOT_IN_DATA` |
| 29 | `INDIAN_EXCHANGE_FEES_2026-11-03.md:12` | Row 6 (`Binance`) | `2024-08` | `Binance (FIU-registered since 2024-08)` (`INDIAN_EXCHANGE_FEES_2026-11-03.md:12`) | `NOT_IN_DATA` in CBP files (external registration date claim, `OURS`) | `NOT_IN_DATA` |
| 30 | `INDIAN_EXCHANGE_FEES_2026-11-03.md:12` | Row 6 (`Binance`) | `0.1 %` | `0.1 % maker and taker VIP 0, 0.075 % with BNB (fee page did not load this day; figure from memory, re-check)` (`INDIAN_EXCHANGE_FEES_2026-11-03.md:12`) | `NOT_IN_DATA` in CBP files (`0` Binance spot fee figures in `MyTradingSys/research/cbp/`; `SCORECARD_GPT.md:14` `0.10%` is Deribit 2-side RT fee, not Binance 1-side spot fee, `OURS`) | `NOT_IN_DATA` |
| 31 | `INDIAN_EXCHANGE_FEES_2026-11-03.md:12` | Row 6 (`Binance`) | `VIP 0` (`0`) | `0.1 % maker and taker VIP 0` (`INDIAN_EXCHANGE_FEES_2026-11-03.md:12`) | `NOT_IN_DATA` in CBP files (external tier label from memory, `OURS`) | `NOT_IN_DATA` |
| 32 | `INDIAN_EXCHANGE_FEES_2026-11-03.md:12` | Row 6 (`Binance`) | `0.075 %` | `0.075 % with BNB (fee page did not load this day; figure from memory, re-check)` (`INDIAN_EXCHANGE_FEES_2026-11-03.md:12`) | `NOT_IN_DATA` in CBP files (`0` hits for `0.075` in `MyTradingSys/research/cbp/`; figure from memory, `OURS`) | `NOT_IN_DATA` |
| 33 | `INDIAN_EXCHANGE_FEES_2026-11-03.md:14` | Tax paragraph | `2026-27` | `Tax (Budget 2026-27, unchanged)` (`INDIAN_EXCHANGE_FEES_2026-11-03.md:14`) | `NOT_IN_DATA` in CBP files (`0` hits for `2026-27` or `Budget` in `MyTradingSys/research/cbp/` outside `INDIAN_EXCHANGE_FEES_2026-11-03.md`, `OURS`) | `NOT_IN_DATA` |
| 34 | `INDIAN_EXCHANGE_FEES_2026-11-03.md:14` | Tax paragraph | `30 %` | `30 % on VDA gains, no loss offset` (`INDIAN_EXCHANGE_FEES_2026-11-03.md:14`) | `30%` (`SOURCED`: `MyTradingSys/research/cbp/archive/SISTER_NOTE_2026-11-03.md:28` `"- Every sale has 1% TDS cut and 30% tax on profit, losses cannot be set off."`) | `FOUND` |
| 35 | `INDIAN_EXCHANGE_FEES_2026-11-03.md:14` | Tax paragraph | `1 %` | `1 % TDS on every sale` (`INDIAN_EXCHANGE_FEES_2026-11-03.md:14`) | `1%` (`SOURCED`: `MyTradingSys/research/cbp/archive/SISTER_NOTE_2026-11-03.md:28` `"- Every sale has 1% TDS cut and 30% tax on profit, losses cannot be set off."`) | `FOUND` |
| 36 | `INDIAN_EXCHANGE_FEES_2026-11-03.md:14` | Tax paragraph | `18 %` | `18 % GST on fees` (`INDIAN_EXCHANGE_FEES_2026-11-03.md:14`) | `NOT_IN_DATA` in CBP files outside `INDIAN_EXCHANGE_FEES_2026-11-03.md` (`matches row 1 INDIAN_EXCHANGE_FEES_2026-11-03.md:7 "plus 18 % GST"`, `SOURCED`; `0` hits in other CBP files, `OURS`) | `NOT_IN_DATA` |
| 37 | `INDIAN_EXCHANGE_FEES_2026-11-03.md:14` | Tax paragraph | `356601` | `Sources: decrypt.co/356601, kucoin.com news flash, outlookmoney.com.` (`INDIAN_EXCHANGE_FEES_2026-11-03.md:14`) | `NOT_IN_DATA` in CBP files (external article path ID, `OURS`) | `NOT_IN_DATA` |
| 38 | `INDIAN_EXCHANGE_FEES_2026-11-03.md:16` | Closing Read | `0.9 %` | `Read: on an INR-native exchange a retail round trip costs about 0.9 % plus GST before TDS` (`INDIAN_EXCHANGE_FEES_2026-11-03.md:16`) | `0.90 %` (`OURS` exact arithmetic from `INDIAN_EXCHANGE_FEES_2026-11-03.md:7-8`: ZebPay base spot `0.45 %` * `2` sides = `0.90 %`; Mudrex base spot `0.45 %` * `2` sides = `0.90 %`; with `18 %` GST on fees, `0.90 % * 1.18 = 1.062 %`, `OURS`) | `FOUND` |
| 39 | `INDIAN_EXCHANGE_FEES_2026-11-03.md:16` | Closing Read | `0.2 %` | `on Binance about 0.2 %` (`INDIAN_EXCHANGE_FEES_2026-11-03.md:16`) | `0.20 %` (`OURS` exact arithmetic from `INDIAN_EXCHANGE_FEES_2026-11-03.md:12`: Binance VIP 0 base spot `0.1 %` * `2` sides = `0.20 %`; with BNB discount `0.075 % * 2 = 0.15 %`, `OURS`) | `FOUND` |
| 40 | `INDIAN_EXCHANGE_FEES_2026-11-03.md:16` | Closing Read | `1 %` | `The 1 % TDS per sale is the biggest friction on any venue and dwarfs the exchange-fee gap.` (`INDIAN_EXCHANGE_FEES_2026-11-03.md:16`) | `1 %` (`SOURCED`: `INDIAN_EXCHANGE_FEES_2026-11-03.md:14` `"1 % TDS on every sale"`, and `MyTradingSys/research/cbp/archive/SISTER_NOTE_2026-11-03.md:28` `"Every sale has 1% TDS cut"`) | `FOUND` |

---

## 2. Recomputed Round-Trip Arithmetic From the Table Rows (`INDIAN_EXCHANGE_FEES_2026-11-03.md:7-16`)

1. **INR-Native Retail Base Tier (ZebPay & Mudrex, `INDIAN_EXCHANGE_FEES_2026-11-03.md:7-8,16`)**:
   - **ZebPay base tier** (`< Rs 5 lakh` 30-day volume, `INDIAN_EXCHANGE_FEES_2026-11-03.md:7`, `SOURCED`): `0.45 %` per side (`maker` and `taker`).
     - Pre-GST, pre-TDS round trip (`buy + sell`): `0.45 % + 0.45 % = 0.90 %` (`OURS`), matching `INDIAN_EXCHANGE_FEES_2026-11-03.md:16` (`"about 0.9 % plus GST before TDS"`, `SOURCED`).
     - Including `18 %` GST on fees (`INDIAN_EXCHANGE_FEES_2026-11-03.md:7,14`, `SOURCED`): `0.45 % * 1.18 = 0.531 %` per side -> `1.062 %` round trip (`OURS`), plus `Rs 15` flat INR withdrawal fee (`INDIAN_EXCHANGE_FEES_2026-11-03.md:7`, `SOURCED`).
     - Including `1 %` TDS on the sale leg (`INDIAN_EXCHANGE_FEES_2026-11-03.md:14,16`, `SOURCED`): `0.90 % + 0.162 % (GST) + 1.00 % (TDS) = 2.062 %` total cash drag on a round trip (`OURS`).
   - **Mudrex base tier** (`< Rs 2 lakh`, `INDIAN_EXCHANGE_FEES_2026-11-03.md:8`, `SOURCED`): `0.45 %` per side.
     - Pre-GST, pre-TDS round trip (`buy + sell`): `0.45 % + 0.45 % = 0.90 %` (`OURS`), matching `INDIAN_EXCHANGE_FEES_2026-11-03.md:16` (`"about 0.9 % plus GST before TDS"`, `SOURCED`).
     - Including `18 %` GST on fees: `1.062 %` round trip (`OURS`); INR deposit and withdrawal are `free` (`Rs 0`, `INDIAN_EXCHANGE_FEES_2026-11-03.md:8`, `SOURCED`).
   - **Higher volume tiers in the table (for completeness, `OURS`)**:
     - ZebPay (`INDIAN_EXCHANGE_FEES_2026-11-03.md:7`): `>= Rs 5 lakh` -> `2 * 0.18 % = 0.36 %` pre-GST (`0.4248 %` with `18 %` GST); `>= Rs 75 lakh` -> `2 * 0.13 % = 0.26 %` pre-GST (`0.3068 %` with `18 %` GST) (`OURS`).
     - Mudrex (`INDIAN_EXCHANGE_FEES_2026-11-03.md:8`): `>= Rs 2 lakh` -> `2 * 0.42 % = 0.84 %` pre-GST (`0.9912 %` with `18 %` GST); `>= Rs 10 lakh` -> `2 * 0.25 % = 0.50 %` pre-GST (`0.59 %` with `18 %` GST); `>= Rs 75 lakh` -> `2 * 0.22 % = 0.44 %` pre-GST (`0.5192 %` with `18 %` GST) (`OURS`).
   - **Unverified INR venues in the table (`INDIAN_EXCHANGE_FEES_2026-11-03.md:9-11`, `OURS`)**:
     - CoinDCX spot (`0.1 % to 0.5 %` per side, `INDIAN_EXCHANGE_FEES_2026-11-03.md:9`): `0.20 % to 1.00 %` round trip pre-GST (`OURS`).
     - CoinSwitch spot (`0.04 % to 0.5 %` per side, `INDIAN_EXCHANGE_FEES_2026-11-03.md:10`): `0.08 % to 1.00 %` round trip pre-GST (`OURS`).
     - WazirX (`ZERO plan Rs 99 per month, zero spot fee claimed`, `INDIAN_EXCHANGE_FEES_2026-11-03.md:11`): `0.00 %` variable spot round trip plus `Rs 99`/month subscription (`OURS`).

2. **Binance Round Trip (`INDIAN_EXCHANGE_FEES_2026-11-03.md:12,16`)**:
   - **VIP 0 base spot** (`0.1 % maker and taker VIP 0`, `INDIAN_EXCHANGE_FEES_2026-11-03.md:12`, `SOURCED`):
     - Round trip (`buy + sell`): `0.1 % + 0.1 % = 0.20 %` (`OURS`), matching `INDIAN_EXCHANGE_FEES_2026-11-03.md:16` (`"on Binance about 0.2 %"`, `SOURCED`).
   - **VIP 0 with BNB discount** (`0.075 % with BNB`, `INDIAN_EXCHANGE_FEES_2026-11-03.md:12`, `SOURCED`):
     - Round trip (`buy + sell`): `0.075 % + 0.075 % = 0.15 %` (`OURS`).

3. **Comparison with `1 %` TDS Per Sale (`INDIAN_EXCHANGE_FEES_2026-11-03.md:14,16`)**:
   - Exchange-fee round-trip gap between INR-native base tier (`0.90 %` pre-GST / `1.062 %` with `18 %` GST) and Binance VIP 0 (`0.20 %`): `0.70 %` pre-GST (`0.862 %` with GST) (`OURS`).
   - The `1.00 %` TDS deducted on every sale (`INDIAN_EXCHANGE_FEES_2026-11-03.md:14,16`, `SOURCED`) exceeds both the `0.90 %` pre-GST INR-native round-trip fee and the `0.70 %` (`0.862 %` with GST) venue fee gap (`OURS`).

---

## 3. Consistency Check Against the CBP Store and `MyTradingSys/research/cbp/`

A full search across `MyTradingSys/research/cbp/` (`13` files total) and `MyTradingSys/cbp/` (`3` files total) for `zebpay|mudrex|coindcx|coinswitch|wazirx|binance|fee|tds|gst|vda|0\.45|0\.18|0\.13|0\.42|0\.25|0\.22|0\.075|lakh|inr` shows (`OURS`):

1. **`MyTradingSys/research/cbp/archive/SISTER_NOTE_2026-11-03.md:28-29` (`SOURCED`)**:
   - Line `28`: `"- Every sale has 1% TDS cut and 30% tax on profit, losses cannot be set off. So trade less, hold longer."` — matches `INDIAN_EXCHANGE_FEES_2026-11-03.md:14,16` (`30 % on VDA gains, no loss offset; 1 % TDS on every sale`, `SOURCED`).
   - Line `29`: `"- Exchange fee is small next to that. Stay on the exchange you already use."` — qualitative summary consistent with `INDIAN_EXCHANGE_FEES_2026-11-03.md:16`, containing no numeric exchange fee percentages (`SOURCED`).
2. **`MyTradingSys/research/cbp/SCORECARD_GPT.md:14` (`SOURCED`)**:
   - Line `14`: `"3. **Fee Hurdle**: Net scoring requires accounting for execution frictions: Deribit taker fee 0.05% per side = 0.10% round trip (10 bps RT; MyTradingSys/backtest/fees.py:5; MyTradingSys/backtest/layers/FORMULAS.md:403)."` — stores only the Deribit BTC perpetual taker fee (`0.05%` per side = `0.10%` round trip), not any Indian exchange or Binance spot fee (`SOURCED`).
3. **ZebPay and Mudrex Rows vs CBP Store (`OURS`)**:
   - Neither `MyTradingSys/research/cbp/` nor `MyTradingSys/cbp/` (which holds only `MyTradingSys/cbp/__init__.py`, `MyTradingSys/cbp/discord_rows.py`, and `MyTradingSys/cbp/schema.json`) stores any ZebPay or Mudrex fee schedule, HTML capture, or JSON fixture (`0` occurrences outside `INDIAN_EXCHANGE_FEES_2026-11-03.md:7-8`, `OURS`). Therefore, all ZebPay (`INDIAN_EXCHANGE_FEES_2026-11-03.md:7`) and Mudrex (`INDIAN_EXCHANGE_FEES_2026-11-03.md:8`) tier figures are page-only claims marked `NOT_IN_DATA` (`OURS`).

Noticed: In `INDIAN_EXCHANGE_FEES_2026-11-03.md:16`, the closing read quotes the INR-native retail round trip as `"about 0.9 % plus GST before TDS"` (`2 * 0.45 % = 0.90 %` pre-GST; `1.062 %` after adding the `18 %` GST from lines `7` and `14`), so once `18 %` GST is applied (`1.062 %`) the round-trip fee + GST slightly exceeds the `1.00 %` single-sale TDS even though the exchange-fee gap vs Binance (`0.70 %` pre-GST, `0.862 %` with GST) remains smaller than `1 %` TDS (`OURS`).
