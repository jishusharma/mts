# Fabio trade-recap video search (card find-more-fabio-trade-recap-videos-yt-dl, 2026-10-17)

Method: `search.py` = six `yt_dlp --flat-playlist ytsearch15:` queries, metadata only (id, title, channel, duration). No downloads, 0 caption fetches
(cap 5/session; HTTP 429 ends caption fetching for the day; none hit). Output: `candidates.csv` (44 unique ids). Titles are claims by uploaders, not verified content.

Already in the ledger or handled (do not re-read): 8CWKfoSJu3c, 0jM5Y31YJak, fZlNGWvd2Ko, 9IliXww64uM, jasv3L-d8ZE, DyS79Eb92Ug, Is1HvdfQm5c, xUyqIjCfZzg, Jpd96fLqr5M, gLHd20jE8UQ (not Fabio), 9I5vTvwsMBk.
Note: the card's six named candidates are all already downloaded/read in earlier passes (see FABIO_TRADE_LEDGER.md "Find-more pass"); the ledger has 15 parent trades / 73 rows, past the 8-entry premise of the card.

## NEW candidates with live trades on screen likely (ranked by length of live content; read order for follow-up cards)
| id | duration s | channel | why |
|---|---|---|---|
| tvERE-Beu2U | 12733 | Chart Fanatics | "Trading LIVE with a World TOP Ranked Scalper" - live session (check it is not a re-upload of DyS79Eb92Ug/xUyq) |
| TvoQr6ObjnU | 20376 | Chart Fanatics + Andrea Cimi | live session, longest |
| feV6CATGUqo | 10801 | HijoTrades | full strategy explained, likely chart examples |
| pZai3k1e-Jg | 6971 | HijoTrades | strategy breakdown with examples |
| xArUSiXyUzI | 5866 | HijoTrades | "LIVE Trading" |
| HUYBdYnXUNc | 1990 | IQCapital | "Live On Chart" |
| agjftXPkLUE | 1496 | Andrea Cimi + Fabervaale | traded with Fabio-style scalper |
| cLgdXZnLL_0 | 2056 | Andrea Cimi + Fabervaale | same series |
| DD73wDVvObI | 2134 | World Class Edge | 4 champions trade same session |
| Khgj5q1-ln8, cUTsoU-15Tc, o-w5Gxss6T0, 06R-ebyOhDI, Pz8f0wWW12M | 434-2464 | Fabervaale ENG | same channel as the 5 productive recap videos; likely 1-2 trades each |

Lower value (third-party explainers/indicators, no Fabio trades): The Zero Print, LuxAlgo, Strix Systems, Orderflow Tools, Pavlovic, One7rade, Kai Capital.
Duplicate risk: tvERE-Beu2U, TvoQr6ObjnU, HUYBdYnXUNc may replay the same NQ sessions already read in DyS79Eb92Ug (F6-F14); dedupe by Daily P/L at start before adding rows.

## Defaults taken (logged)
- Did not download or read frames: task text assumed the six old candidates were open; they are not, so the new work is this list. Reading is follow-up cards, one video per session.
- Fabervaale ENG short videos first (cheap, sheets.py workflow already proven), then long live sessions.
