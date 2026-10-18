# Malkan channel list and caption shortlist (2026-10-15)

Channel: Malkansview, `UCKxWWqBQZYKTA01GkyQdMHA` (uploader @Malkansview01; found from `A-CQiV_UFB4`).
Full listing: 876 videos, metadata only (flat playlist: id, views, duration, title). Upload dates are blank in flat mode, so dates are not given here.
Method: ranked by topic fit to the Malkan method (RSI 40/60 zones, 5-star / Grandfather-Father-Son, divergence, setups, entries and stops), then by views.
Language is inferred from the title only (Hinglish titles = Hindi). Confirm at caption time: the Hindi track must exist.

Caption status: **all captions PENDING_CAPTIONS**. YouTube returned HTTP 429 on the first request (`hNfjyrJEytI`, 2026-10-15 12:18Z). Nothing below has been fetched in this session.

## English shortlist (up to 10)

| # | id | views | title | fit | status |
|---|----|------:|-------|-----|--------|
| 1 | v8pCR_bA0_0 | 569000 | RSI - 5 Star Set Up #1 | setup (5-star) | PENDING_CAPTIONS |
| 2 | kVIvcn7T44o | 566000 | RSI Powerful Strategy | RSI strategy | PENDING_CAPTIONS (in the 5 refused ids) |
| 3 | -2uZSqKKrFQ | 53000 | RSI 40-60 Strategy Explained, Grandfather-Father-Son Trading System | 40/60 zones, GFS | PENDING_CAPTIONS |
| 4 | 2HcJ3NeZmEQ | 56000 | RSI 5 Star Set Up #1 (Sell Setup) | setup (5-star, short) | already in raw_transcripts_canonical (V1) |
| 5 | 5Aoyw_sG_88 | 127000 | RSI - Set up 1 - Targets | setup, targets | PENDING_CAPTIONS |
| 6 | kL7_ybtI_Fc | 255000 | RSI - 5 - | RSI, 5-star (title unclear) | PENDING_CAPTIONS |
| 7 | cQ-y1oULkBw | 370000 | Divergence Trading Strategy | divergence | already in raw_transcripts_canonical (V1) |
| 8 | GbXnw_tNMtw | 338000 | Reverse Divergence - Positive & Negative Divergence! | divergence | PENDING_CAPTIONS |
| 9 | TrZQ4Xat_sQ | 166000 | RSI Divergence Trade | divergence, entry | PENDING_CAPTIONS |
| 10 | TO3pLafk7Us | 124000 | RSI Divergence Class A/B/C | divergence classes | PENDING_CAPTIONS |

Bench (fit is good, not in the 10): `hGPqIpWRUMQ` Pullback Trading Using Unconventional RSI Part 1; `pdDwUMVi6MA` RSI PRD - Trend-Following Entries; `gfr5n6B5QJk` 6. RSI divergence (3X3 series); `RUKGEMdVNYA` RSI Range Shift; `qES8tmcq520` Back to Basics - RSI; `13QOxEJBG2w` GFS Magic on 3 Stocks; `hc5t_ckZoEg` RSI + GFS Breakdown; `ccCcuGWZQRI` 4 Risk Setups Every Trader MUST Know; `ctBtClaBdk0` Exit Strategies.

Excluded: options-only (v5hoPMN2RP0, Options Simplified episodes tp4zg8-V7qM, lgyI-GOWZUE, fya-UAJAIFg), market updates, mindset and testimonial videos, and series with no RSI content.

## Hindi shortlist (10, from Hinglish titles)

Only about 10 Hinglish titles on the method exist in the listing, so the list is short of a full 10 RSI-specific videos. Ranked by fit, then views.

| # | id | views | title | fit | status |
|---|----|------:|-------|-----|--------|
| 1 | sPu2SnAFEIY | 141000 | 5. RSI Ki Ye Strategy Koi Nahi Batayega (3X3 Swing Trading) | RSI strategy | PENDING_CAPTIONS |
| 2 | fgN6QBFY3Ss | 160000 | 11. Bollinger Bands Ka Father-Son Strategy | Father-Son (GFS) | PENDING_CAPTIONS (in the 5 refused ids) |
| 3 | RPmxr3c8mso | 47000 | RSI Se Trend Kaise Samjhe? | RSI trend | PENDING_CAPTIONS |
| 4 | qbx6lnPb4kA | 47000 | RSI Se Entry Kaise Pakde? (Options Simplified Ep 5) | RSI entries | PENDING_CAPTIONS |
| 5 | 4uiBvqei6CI | 57000 | Simple RSI Se Option Trading | RSI, options | PENDING_CAPTIONS |
| 6 | qqKt3Ulmc3g | 60000 | Bollinger Bands Ka Complete Trading Guide | indicator | PENDING_CAPTIONS |
| 7 | Z2zJo7QFk0o | 45000 | 4 Mahine Mein 50% Up! Kaise Stocks Choose Karein (Top-Down Approach) | top-down method | PENDING_CAPTIONS |
| 8 | kd0xQ-zP9BQ | 42000 | Banking Sector Mein Big Breakout! | breakout setup | PENDING_CAPTIONS |
| 9 | xBd5iG7g51w | 68000 | Charts Ka Simple Logic | chart reading | PENDING_CAPTIONS |
| 10 | Q2ikog1RFbQ | 23000 | Tips Se Nahi, System Se Trading Karo | system | PENDING_CAPTIONS |

Already in raw_transcripts_canonical as Hindi (V1 pass): `A-CQiV_UFB4` "8. RSI Reverse Divergence" (`_hi_raw.txt`). Not on the list above; it is the best Hindi RSI-divergence video on this channel.

## Next step
Per the card: retry the captions once a day for 3 days, one request at a time, at least 60 s apart, no cookies. Then fetch the English shortlist (`--langs en`) and the Hindi shortlist (`--langs hi,en`, which saves `_hi_raw.txt` plus the English translation), using `fetch_one_at_a_time.py` from the side-session notes folder.
