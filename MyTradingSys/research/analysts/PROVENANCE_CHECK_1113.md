# Provenance check 1113: rlinda, bennett, cryptochase CALL_LEDGER rows

Card: callers-peer-ledger-provenance-1113. Method: public WebFetch of each source_url (no login, no Chrome). Price check: BTC daily high/low from `MyTradingSys/research/pitchfork_2026-10-19/btc_1d_2020_2026.csv` for the call date.

Verdict rule: a row is REAL only if its source_url fetches as a post whose levels match. A 404, a 402 (login or paywall) or a generic page is UNVERIFIED. Nothing was guessed.

Outcome: 0 REAL, 0 SAMPLE by content, 9 UNVERIFIED. All 9 rows keep their data and get `SAMPLE:` at the start of `notes` (rows not deleted, git history and call_ids intact).

| call_id | analyst | source_url | fetch | entry | BTC day low-high | entry in day range? | verdict | action |
|---|---|---|---|---|---|---|---|---|
| TV-RLINDA-2024-10-18-67500 | rlinda | tradingview.com/chart/BTCUSDT/h2aJ9K1x-... | 404 | 67500 | 67165-69000 | yes | UNVERIFIED | notes SAMPLE |
| TV-RLINDA-2024-10-19-69200 | rlinda | tradingview.com/chart/BTCUSDT/p9L8mQ2z-... | 404 | 69200 | 68000-68685 | no | UNVERIFIED | notes SAMPLE |
| TV-RLINDA-2024-09-28-62800 | rlinda | tradingview.com/chart/BTCUSDT/m3K7xV8y-... | 404 | 62800 | 65368-66237 | no | UNVERIFIED | notes SAMPLE |
| DPA-2024-10-18-68400 | bennett | dailypriceaction.com/market-analysis/bitcoin-fvg-retest-68400/ | 404 | 68400 | 67165-69000 | yes | UNVERIFIED | notes SAMPLE |
| DPA-2024-10-06-63800 | bennett | dailypriceaction.com/market-analysis/bitcoin-breakout-channel-63800/ | 404 | 63800 | 61779-62962 | no | UNVERIFIED | notes SAMPLE |
| DPA-2024-09-17-59800 | bennett | dailypriceaction.com/market-analysis/bitcoin-fvg-fill-59800/ | 404 | 59800 | 57589-61345 | yes | UNVERIFIED | notes SAMPLE |
| SOC-CRYPTOCHASE-2024-10-18-65200 | cryptochase | x.com/Crypto_Chase/status/1847240182941016320 | 402 | 65200 | 67165-69000 | no | UNVERIFIED | notes SAMPLE |
| SOC-CRYPTOCHASE-2024-10-09-67800 | cryptochase | x.com/Crypto_Chase/status/1844001298418299136 | 402 | 67800 | 60252-62521 | no | UNVERIFIED | notes SAMPLE |
| SOC-CRYPTOCHASE-2024-09-24-62400 | cryptochase | x.com/Crypto_Chase/status/1838549102984921088 | 402 | 62400 | 62688-64666 | no | UNVERIFIED | notes SAMPLE |

Notes:
- The price check is only a secondary signal. Entries inside the day range (3 rows) do not make a row REAL; a fetchable post is required.
- No call_id is referenced outside the three CSVs (repo grep), so nothing else needed editing.
- Still open: a human or logged-in check is needed to turn any row REAL. Out of scope for this card.
