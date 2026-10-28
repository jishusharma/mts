# B067 - CRYPTO MODULE GATING AUDIT

Register row: MyTradingSys/research/BUGS.md B067.
Opened: 2026-09-24 by session MTS-2026-09-24-1100Z.

## THE DEFECT

Crypto-hack fields may be gating the core verdict, in violation of
PROJECT_VISION.md doctrine: "modules never gate core behavior."

## EVIDENCE

Source: MyTradingSys/methodology/crypto_adaptations.md (2026-08-06).
Crypto-hack items with UNVALIDATED status; Tom never mentions any of them:

1. Aggregated CVD (Binance+Bybit+OKX)
2. Funding rate as context
3. Liquidation clusters as squeeze risk
4. OI delta for confirmation
5. UTC 00:00 as daily open
6. Funding reset times (00:00/08:00/16:00 UTC)
7. Slippage buffer (Net R:R = gross x 0.75)
8. Correlation-adjusted risk

Validated rows in same file (kept): perpetual swaps, CoinGlass as source.

## AUDITED SO FAR

post_funding_vp: demoted 2026-09-24. Was producing 781 of 8200
rank-1 verdict lines. Removed from candidate zone list and from
target pool in SetupCandidatesBuilder.java and math_object_builder.py.
Still emitted in snapshot; visible in feed; shown as POST_FUNDING in
current_market_state.md. Cannot drive tier, stop, target, or rank-1.

## NOT YET AUDITED

For each remaining crypto hack: does it feed the verdict (tier, stop,
target, rank-1, or a rule read)? If yes, demote or document an
exception with evidence.

Priority order (highest gating risk first):
1. UTC 00:00 as daily open - anchors state_code.json CVD and
   mts_math.py session CVD. Live verdict input.
2. Funding rate - read by verdict function as a context field.
3. OI delta - read by open_interest block and shown in feed.
4. Aggregated CVD - not implemented (T035).
5. Liquidation clusters - deprecated at system level.
6. Slippage buffer - applied to all net_rr values. Verdict-changing constant.
7. Correlation-adjusted risk - not implemented.

## STATE

2026-09-24 OPEN. Only post_funding_vp resolved. Audit of the rest is
owed. UTC 00:00 anchor and the 0.75 slippage multiplier are the next
two to review because both are live verdict inputs.

# END
