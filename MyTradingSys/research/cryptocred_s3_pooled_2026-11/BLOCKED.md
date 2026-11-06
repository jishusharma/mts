# BLOCKED: pooled BTC+ETH power gate fails (2026-11-06, card route-cryptocred-s3-power-unblock)

Verdict word: BLOCKED. Count-only: `cc_s3_pooled_count.py` calls `find_limit_fill` only; no trade simulated, no R, no exit, no VALIDATION/HOLDOUT bar (bars cut at 2024-07-01, `splits.assert_dev_only`). No PRE_REG frozen (gate exit 1), so no DEV run.

Recount (`count.json`, DEV 2022-01..2024-06, 4h Setup 1 sr_flip, ATR buffer 1.0; fills do not depend on the stop): BTCUSDT 217 signals, 207 filled (matches the 11-01 count); ETHUSDT 210 signals, 202 filled (tick 0.01, SOURCED Binance filter); pooled n = 409 (the card's 414 was a rough 2x).

Gate (`gate_output.txt`, exit 1): `prereg_gate.py --n 409 --sd 1.24 --cost 0.068 --m auto --new-cells 1` -> m 221 (220 prior DEV variants from the verdicts count + 1 new cell), z_holm 3.688, MDE 0.278 R + cost 0.068 R = 0.346 R > 0.30 R max plausible gross; n needed 586 (short by 177, 30 percent). sd 1.24 R is the two-point value of BLOCKED.md of 11-01 (SOURCED to that file, no outcome read); cost 0.068 R is OURS-UNREPRODUCED.

Note: the DEV variant count grew from 105 to 220 since 11-01, so pooling (n 207 -> 409) and one cell instead of six still do not clear the gate. With m = 1 the MDE would be 0.172 + 0.068 = 0.240 R (would pass), but changing repo m or the 0.30 R cap is out of scope.

END reason: no further 1m symbols exist (only BTC and ETH), DEV window is fixed by splits.py. Unblock needs an operator overrule of m / the cap, or a longer sample; either is a new PRE_REG. CryptoCred 4h Setup 1 is NOT killed (no outcome read); the underpowered result is "untested", never "no edge".

DECISION (OURS, conservative default): BLOCKED, END; no run.

## Kill scope
Count-only block of the single pooled cell (4h Setup 1, ATR buffer 1.0, BTC+ETH DEV, fixed 1.5 R bracket, Deribit all_taker). Setup 2, other buffers, and 1d are not covered by this card.
