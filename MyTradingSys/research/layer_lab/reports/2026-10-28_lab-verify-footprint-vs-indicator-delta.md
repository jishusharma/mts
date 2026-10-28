# LAB-VERIFY: CoinGlass Net Delta indicator vs Legend footprint delta vs spot taker delta

**Label**: Sonnet/Claude-derived read (Claude Code, host DESKTOP-F7IU69N, 2026-10-28). This is NOT an
independent cross-vendor (DeepSeek/DSA) check — DSA was unreachable, so a Supervisor session stood in on
the stuck desk-queue row `20261026-172202-lab-verify-footprint-vs-indicator-delta`.

**Card**: `lab-verify-footprint-vs-indicator-delta` (DSA, prio 3).
**Result: BLOCKED (partial)** — 1 of 3 sources computed; the other 2 are not reachable from this host.

## What happened

The card's `scope_in` names 7 shot ids (`1f3d02f3e0aa 34bad00c5501 d31c5690e8c0 43fc5ddec27b df6257dd397a
8dc124f61332 7a8737e4c81b`) holding the CoinGlass Net Delta indicator and Legend footprint delta reads for
the 13:00-14:30Z 2026-10-26 window. The desk-queue row (`MyTradingSys/system/desk_queue/20261026-172202-...json`)
shows these were posted `"from": "JIS-NB"`. The shot store is per-machine and gitignored
(`MyTradingSys/methodology/screenshot_intake.md:30`: "one per machine, shared by all worktrees, gitignored").
On this host (DESKTOP-F7IU69N) `python scripts/dev/shot.py list` / `show` finds none of the 7 ids — the
store here holds only 34 unrelated shots (Windows/app/BIOS screenshots). `MyTradingSys/research/BUGS.md` B201
confirms these 7 ids were only ever classified, never read-and-extracted into a committed file, so no
extracted indicator/footprint numbers exist anywhere in the repo either (checked via repo-wide grep for each id).

**DECISION (OURS)**: rather than wait or ask, broadcast a request to JIS-NB (`mts_signal.py broadcast`,
sent 2026-10-28) to run `shot.py read --extract` on its own local copy of these 7 shots if it still has
them, and land the CoinGlass/footprint numbers in this research tree. Meanwhile compute the one leg that
is mechanically reproducible from public data on any host: spot taker delta.

## Spot taker delta (reproducible, computed here)

Source: `data-api.binance.vision` public klines, `BTCUSDT`, `15m`, UTC bar-open label, 2026-10-26
13:00-14:15Z (6 bars, covering the 13:00-14:30Z window). Units: BTC (base-asset volume). Formula:
`spot_delta = 2*taker_buy_base_volume - volume` (taker_buy − taker_sell, both base units).

| Bar (UTC, open) | Close | Volume (BTC) | Taker-buy (BTC) | Spot taker delta (BTC) |
|---|---|---|---|---|
| 13:00 | 80,172.00 | 384.104 | 200.788 | **+17.473** |
| 13:15 | 79,952.00 | 209.411 | 79.733 | **-49.946** |
| 13:30 | 79,773.72 | 757.676 | 408.987 | **+60.299** |
| 13:45 | 79,702.63 | 513.501 | 244.204 | **-25.093** |
| 14:00 | 79,954.01 | 360.026 | 222.308 | **+84.591** |
| 14:15 | 79,873.02 | 426.461 | 241.191 | **+55.922** |

Bar alignment: label = bar OPEN time, UTC, closed bars only (close = `open + 15m - 1ms`). This is the same
convention `MyTradingSys/methodology/screenshot_intake.md:48` already states for TradingView/CoinGlass
(UTC); it flags that `legend.coinglass.com` footprint pages render in IST (UTC+5:30) — a naive footprint
screenshot time must be shifted by -5:30 before lining up with this table.

Sign note at 13:30Z: the operator's prior note says the indicator read this bar as selling while the
footprint showed +2.13K buying. This spot-taker-delta leg is **+60.299** (buying) for the 13:30Z bar —
same sign as the footprint, opposite the indicator read — consistent with (but not proof of) the prior
3-of-6 footprint/spot sign-agreement count; this session did not re-derive that count because the
footprint and indicator columns are unavailable here (see below).

## What is still missing

- **CoinGlass Net Delta indicator** column: unavailable (screenshots on JIS-NB only, never extracted to a
  committed file).
- **Legend footprint delta** column: same.
- **Sign agreement count**: cannot be computed without those two columns. The card's DONE-when prior
  value ("spot vs footprint was 3 of 6") is carried over from the card text, not re-verified here.
- **Verdict on which source Eagle_Eyes should quote going forward**: a provisional, conservative one-line
  rule is written below and into `screenshot_intake.md`, but it is NOT a full cross-vendor sign-agreement
  verdict — that needs the indicator/footprint numbers this session could not reach, or Lab_Guy
  judgment on cross-vendor weighting once those numbers are in hand. Flagging per the LAB-VERIFY class
  note (A-20261018-1 / ROUTING.md C4): this slipped from a mechanical run-script-and-compare job into a
  cross-vendor/missing-data judgment call, so it should not be self-certified as a closed verdict by a
  Sonnet stand-in.

## One-line quoting rule (provisional, OURS)

Until the indicator and footprint legs are verified against each other: **Eagle_Eyes quotes the spot
taker delta (`2*taker_buy_base_volume - volume`, Binance `data-api.binance.vision`, UTC bar-open label) as
the source of record over the CoinGlass Net Delta indicator or the Legend footprint panel**, because it is
the only one of the three that is independently and mechanically re-derivable from disk-free public data
on any host; the indicator/footprint reads stay context notes until this card is reopened with the 7
shots (or their extracted numbers) actually reachable.

## Next step for whoever reopens this

1. Check whether JIS-NB's local `runtime_data/screenshots/` still has `1f3d02f3e0aa 34bad00c5501
   d31c5690e8c0 43fc5ddec27b df6257dd397a 8dc124f61332 7a8737e4c81b` (shot store is gitignored; it may
   have been cleaned since 2026-10-26).
2. If yes: `shot.py read --extract` there, commit the extracted values, redo the per-bar table with all
   3 columns and the real sign-agreement count, and replace the provisional rule above.
3. If no: the card is NOT_IN_DATA for good — the indicator/footprint numbers for this specific window are
   gone; the provisional rule above (quote spot taker delta) stands as the practical fallback.
