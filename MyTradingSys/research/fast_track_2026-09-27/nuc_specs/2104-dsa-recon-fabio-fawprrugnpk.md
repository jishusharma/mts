TASK: Trade reconstruction of one Fabio video (FawPrRUGNpk) using the section 3.2 template; one extract only.
SCOPE: raw_transcripts_canonical/FawPrRUGNpk_raw.txt
SCOPE: MyTradingSys/research/fast_track_2026-09-27/MISSING_PIECES_2026-09-30.md:40-107
SCOPE: MyTradingSys/research/fast_track_2026-09-27/MISSING_PIECES_2026-09-30.md:244-257
CREATE: extracts/processed/fabio_valentini/recon/FawPrRUGNpk_recon.md
OUTPUT: One FILE block, full content: extracts/processed/fabio_valentini/recon/FawPrRUGNpk_recon.md. Nothing else.
OUTPUT_TOKENS: 6000
EXPECT: # Trade reconstruction FawPrRUGNpk
EXPECT: ## Portability

Read the transcript in full. The first SCOPE range is a worked example (Fabio jasv3L-d8ZE); the second is the
template with its 7 additions. Your job: rebuild the trade(s) this trader actually takes in THIS video, end to end,
not a list of rules.

File layout:
# Trade reconstruction FawPrRUGNpk
Line 2: trader, video title if stated, instrument, session/time of day, whether it is a live trade, a replay or a lesson.
If the video contains no concrete trade (only concepts), write one line "NO TRADE WALKTHROUGH" plus the concepts in
<= 10 bullets, then the Portability section, and stop.
## Trade N (one section per concrete trade, in order)
One table row per template field: market state; location; leading signal; trigger; initial stop (price and % of
price, and ticks if futures); target(s) and planned R:R; management (breakeven, adds, trail anchor); exit (what
actually ended it); outcome in R and in money if stated; day selection / day type; horizon (minutes held);
what he explicitly does NOT do. Each field has a verbatim quote from the transcript in double quotes, or the word
NOT STATED. Never paraphrase inside quotes. Never use a quote from another video.
## Session view
Whole-session result if stated (losing trades count; the model is judged per day).
## Portability
Stop width in % of price vs Deribit BTC-PERPETUAL round trip (maker 0, taker 5 bps per side = 10 bps if taker both
ways): fee per stop-out in R = 0.10% / stop%. State whether the trade survives at that stop width, and which BTC
hours correspond to his session (US cash open 13:30 UTC summer / 14:30 UTC winter).
Tom is core; Fabio and every other trader are separate layers, never a filter on Tom.
