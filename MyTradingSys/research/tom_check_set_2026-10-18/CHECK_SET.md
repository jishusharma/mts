# TOM CHECK SET - FRAMES-ONLY TRADE RECAPS (2026-10-18)

Protocol: `TOM_LAYER_V2_SPEC.md` section 7.
Rule: **no caption read** (frozen into CHECK before any caption file is read or transcribed).
Auditing rule: A-20261018-7 (blind reading only, unreadable fields are NOT_IN_DATA).

## 1. Status

none found beyond S7/S8 with the queries tried

The Tom CHECK set remains frozen at **2 trades** (S7 / T11 and S8 / T12), exactly as specified in `TOM_LAYER_V2_SPEC.md` section 7.

## 2. Inventory of Videos in `F:/MTS/data/tom_videos`

Inventory count: 10 .mp4 videos on disk (SOURCED `F:/MTS/data/tom_videos`, 2026-10-18):
- 7 videos with transcript files (`.vtt` / `.txt` present) -> **DESIGN** set:
  - `k0zm5NYn0IQ` (S2 / T2, T2b)
  - `l8RZrBfzvp4` (S6 / T7)
  - `n7ZSkjb7JXs` (S1 / T1, T8)
  - `T6hDJcHrVBM` (S4 / T5)
  - `ujedEcmvBMk` (S3 / T3, T3b)
  - `UOBgXV20yCM` (S9 / T4)
  - `zQTbdEweG3c` (S5 / T6)
- 3 videos with `.mp4` and **no** `.vtt` or `.txt`:
  - `liEJMfE_PXg` (S7 / T11): CHECK set (frames-only)
  - `ZZeET7ng1nk` (S8 / T12): CHECK set (frames-only)
  - `SANOimk8M9o`: Second video of S3 trade (same trade as `ujedEcmvBMk` T3/T3b, already DESIGN from `ujedEcmvBMk` transcript)

## 3. German Channel Playlist & Query Census

Searched on 2026-10-18 via `yt-dlp` metadata-only (zero caption files downloaded or read):
1. **Channel playlist:** Tom Vorwald DE (`UCAR0K4mcBgTnWbo_FtTkXlA/videos`)
   - Total videos on playlist: 114 entries (SOURCED `yt-dlp --flat-playlist`, 2026-10-18)
   - Every entry inspected by title, duration, and metadata:
     - 14 videos correspond to German uploads of already transcribed English videos in the design/spec catalog:
       - `4uc5-s0ckH4` = `k0zm5NYn0IQ` (S2 / T2, T2b)
       - `xkto58NPv4Y` = `n7ZSkjb7JXs` (S1 / T1, T8)
       - `tdtXoHNcVGg` = `zQTbdEweG3c` (S5 / T6)
       - `cuX5x6MgRSE` = `T6hDJcHrVBM` (S4 / T5)
       - `xqSSl2Ls9TI` = `UOBgXV20yCM` (S9 / T4)
       - `evBmBheW7K8` = `l8RZrBfzvp4` (S6 / T7)
       - `VKsPuRPsoS4` = `kXhIAug0Gh8` (spec/catalog TOM-5)
       - `IJ7Z49G9QNw` = `4MoNjEQ2Dd8` (foundational transcript)
       - `LXZWJ0selx8` = `OUM9LYwL8eA` (catalog TOM-1b)
       - `ecb2RJ7X_4M` = `yRvMW6lgN1o` (catalog TOM-3)
       - `ywuuUchu4Ns` = `wPMiyJXL0zU` (catalog ANG R20)
       - `b8XCUlD9VJM` = `tS6ZEiHj8gQ` (catalog TOM-1b)
       - `xgnwstDX0YQ` = `uk4PZV59nYw` (catalog TOM-6)
       - `PAhpkXvaIvo` = `ODdF0Bn_KSc` (catalog TOM-4)
     - 3 videos are the existing CHECK set / S3 duplicate:
       - `liEJMfE_PXg` (S7 / T11)
       - `ZZeET7ng1nk` (S8 / T12)
       - `SANOimk8M9o` (S3 second video)
     - Remaining 97 videos are educational explainers (indicator overviews, volume profile theory, mindset/psychology, swing trading for beginners, Trader Battle reality-show episodes) without on-screen live order panel executions.
2. **Search queries executed:**
   - `ytsearch10:Tom Vorwald Live Trading DAX`: returned known videos (`ujedEcmvBMk`, `yWO8hVpRXeY` [EN dub of `ZZeET7ng1nk`], `liEJMfE_PXg`, `SANOimk8M9o`, `wPMiyJXL0zU`, `ZZeET7ng1nk`, `T6hDJcHrVBM`, `UOBgXV20yCM`, `VumVuGnCcFM`, `zAwEX_tRUfE`).
   - `ytsearch20:Tom Vorwald Live Trading DAX`: confirmed no additional trade recaps.
   - Historical queries from ledger session:
     - `ytsearch25: "World Champion LIVE trade DAX"`
     - `ytsearch25: "Trading World Champion DAX live trade recap"`
     - `ytsearch25: "World Champion trades DAX short stop target explained"`
   - Result: no HTTP 429 encountered during metadata search.
   - Conclusion: zero new live recap candidates exist beyond S7/S8.

## 4. Frozen CHECK Set Trades (S7 & S8)

| Session | Video ID | Trade ID | Market | Side | Qty | Entry | Stop | Target | Frame Path | Frame Time / Taskbar | Status |
|---|---|---|---|---|---|---|---|---|---|---|---|
| S7 | `liEJMfE_PXg` | T11 | FDAX | short | 2 | 26444 | 26490 (46pt, panel 46T) | 26286 (158pt) | `F:/MTS/data/tom_videos/frames/liEJMfE_PXg_0270.jpg` | t=270 (taskbar 10:05) | CHECK (frames only, no caption read) |
| S7 | `liEJMfE_PXg` | T11-x | FDAX | exit | 2 | 26444 | 26490 | 26286 | `F:/MTS/data/tom_videos/frames/liEJMfE_PXg_0630.jpg` | t=600-630 (taskbar 10:10-10:12) | CHECK ("Ziel erreicht" annotation; fill unobserved) |
| S8 | `ZZeET7ng1nk` | T12 | FDAX | short | 1 | 25116 | 25139 (23pt, panel -23T) | 24974 (142pt, panel 142T) | `F:/MTS/data/tom_videos/frames/ZZeET7ng1nk_0330.jpg` | before t=120 (taskbar 08:08-08:10 CEST) | CHECK (frames only, no caption read) |
| S8 | `ZZeET7ng1nk` | T12-m1 | FDAX | stop_tighten | -1 | 25116 | 25038 (moved from 25139) | 24974 | `F:/MTS/data/tom_videos/frames/ZZeET7ng1nk_0990.jpg` | t=900 (SL 25097) to t=990 (SL 25038, taskbar 08:54 CEST) | CHECK (stop to profit locked 78pt; exit unobserved) |

Unreadable/unverified fields per A-20261018-7:
- `executed_contract`: `NOT_IN_DATA` (chart header symbol is not proof of executed contract)
- `execution_minute`: `UNKNOWN` (no frame shows the moment of execution)
- `date`: empty (observed trade date not proven by order frame; legacy dates unverified)
