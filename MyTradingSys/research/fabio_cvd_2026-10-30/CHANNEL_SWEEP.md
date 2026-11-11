CHANNEL SWEEP - Fabervaale ENG (card fabervaale-cvd-sweep, DSA-NUC, 2026-11-11)

Goal: every upload of the Fabervaale ENG channel plus the guest videos and shorts, with the
CVD / delta / absorption / exhaustion passages extracted verbatim. This file is the inventory.
The concept rows live in CVD_CONCEPTS.md (section 5, F-CVD17 to F-CVD32).

Method
- Upload list: yt-dlp --flat-playlist on https://www.youtube.com/@FabervaaleENG/videos and /shorts.
  Captions only, never video or audio.
- Captions come from the shared store raw_transcripts_canonical/<id>_raw.txt through
  scripts/dev/fetch_captions_timed.py (the guarded fetcher). Existing files are never re-fetched.
- Every quote below is checked by scripts/dev/verify_extract_quotes.py (exit 0 required).

BLOCKED, stated plainly: the shared YouTube guard in scripts/dev/fetch_captions_timed.py reports
the host JIS-NUC and its public IP under a level 3 of 3 lockout, blocked until 2026-11-13T13:58:11Z
(6/24/72 h escalating lockout, OURS). The fetcher makes no network call while that record stands.
So the 4 guest videos and the 13 shorts listed as MISSING below were not fetched by this card, and
no workaround was attempted (the guard is the operator's rule, not an obstacle to route around).
They need a re-run after 2026-11-13T13:58Z, or from a host whose IP is not blocked.

Upload dates: yt-dlp --flat-playlist returns NA for upload_date on this channel, and the per-video
metadata call is a network call the guard refuses. Date is therefore "n/a" for every row and the
order is the channel order (newest first) that yt-dlp printed.

## 1. Channel uploads (13), all 13 already in raw_transcripts_canonical

| # | Id | Title | Date | Transcript | CVD/delta hits | Read |
|---|---|---|---|---|---|---|
| 1 | StaphlRH8NQ | 5 Edges that refuse to die. | n/a | local | 0 | y |
| 2 | LQvv5xgy_ik | Exposing my Risk Management Protocol | n/a | local | 0 | y |
| 3 | FawPrRUGNpk | The Only Liquidity Guide You will Ever Need | n/a | local | 31 | y |
| 4 | Khgj5q1-ln8 | My Signature Orderflow Model | n/a | local | 5 | y |
| 5 | cUTsoU-15Tc | The Simplest Orderflow Trading Model | n/a | local | 23 | y |
| 6 | Pz8f0wWW12M | The Only Orderflow Guide You will Ever Need | n/a | local | 42 | y |
| 7 | 8CWKfoSJu3c | How I did 20R in one NQ Session | n/a | local | 8 | y |
| 8 | 06R-ebyOhDI | How To Find The BEST Entry Zones | n/a | local | 9 | y |
| 9 | 0KyIEdvVKMQ | Winning the Mental Game of Trading | n/a | local | 0 | y |
| 10 | fZlNGWvd2Ko | My Best Trading Session of the Month | n/a | local | 3 | y |
| 11 | jasv3L-d8ZE | Watch me Manage a -10.000$ trading Session | n/a | local | 2 | y |
| 12 | o-w5Gxss6T0 | 3 Order-flow Trading Tricks Exposed! | n/a | local | 19 | y |
| 13 | 0jM5Y31YJak | My Top 3 Trades from the Competition | n/a | local | 1 | y |

Hit count = lines matching cvd|cumulative volume|delta|absor|exhaust in the canonical transcript.
A zero means the video has no CVD, delta, absorption or exhaustion passage at all; nothing was
extracted from it, and that is the finding, not a gap.

## 2. Shorts (13), none fetched (guard blocked)

| Id | Title | Date | Read |
|---|---|---|---|
| _xEhztnK2g0 | Market micro mechanics | n/a | n (quoted 10-30, transcript not stored) |
| 3GwHv2FF4Hw | Reload on Deepdom | n/a | n |
| 5H1MCBG87YI | How I set up my take profit | n/a | n (quoted 10-30) |
| FDrHnl7StOM | What professional traders actually use | n/a | n |
| 3JZH06L28us | My tools Tier list | n/a | n (quoted 10-30) |
| Dy0e_mwTHkM | You owe it to yourself. | n/a | n |
| gdaKf6Z_WX0 | The Best Trading Strategy for a Beginner | n/a | n |
| elgkR5exc-4 | What is your favourite position? | n/a | n |
| _PFPIMaHfb8 | Why OF trading | n/a | n |
| _i2pfX42MEY | REAL orderflow trading | n/a | n |
| kbqYiUny0YY | SmartER Money Concepts trading | n/a | n |
| qx_lismAZMs | The only The Algo | n/a | n |
| rUC4cRRLvjE | Steal the 3 things | n/a | n |

F-CVD13 to F-CVD16 in CVD_CONCEPTS.md section 3b were quoted from 3JZH06L28us, 5H1MCBG87YI and
_xEhztnK2g0 on 2026-10-30, when those captions were fetched and then not stored. They cannot be
re-verified today: verify_extract_quotes.py would report NO-TRANSCRIPT for them. They are left as
they are and this note says why.

## 3. Guest and partner videos (4), none fetched (guard blocked)

| Id | Channel | Length | Read |
|---|---|---|---|
| agjftXPkLUE | Andrea Cimi + Fabervaale | 25 min | n |
| cLgdXZnLL_0 | Andrea Cimi + Fabervaale | 34 min | n |
| feV6CATGUqo | HijoTrades | 3 h | n |
| pZai3k1e-Jg | HijoTrades | 1.9 h | n |

## 4. What changed on this card

- 10 of the 13 uploads were read for CVD, delta, absorption and exhaustion passages. The 10-30 file
  had used 8 transcripts; cUTsoU-15Tc, 8CWKfoSJu3c, Khgj5q1-ln8 and jasv3L-d8ZE carry passages that
  were not in it, and they are now F-CVD17 to F-CVD32 in CVD_CONCEPTS.md section 5.
- 16 new concept rows, every one backed by a verbatim quote with a Source GPS tag, checked by
  verify_extract_quotes.py.
- Still open: 4 guest videos and 13 shorts, blocked by the YouTube guard until 2026-11-13T13:58:11Z.

## 5. BTC relevance (OURS)

None of the new quotes is about BTC: the whole channel trades NQ. Two rows transfer to our BTC work
without a new measurement because they are statements about what a delta tool reads, not about a
market: F-CVD17 (law of effort and result) and F-CVD23 (zero result on big pressure). The rest are
NQ-specific and only become BTC claims after a measurement, exactly like the 10-30 file says.

End of sweep.
