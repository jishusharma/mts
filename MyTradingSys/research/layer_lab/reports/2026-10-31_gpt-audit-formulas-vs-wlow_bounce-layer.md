FIX-FIRST

## Scope and method
- Read `MyTradingSys/backtest/layers/FORMULAS.md` sections 1 and 22, the `wlow_bounce` detector, and its imported RSI core.
- Ran a 10-bar synthetic series through the layer functions (no market data): closes `[10,12,11,14,13,15,14,16,15,17]`; volumes all `10`; taker-buy volumes `[7,2,6,5,8,1,4,7,3,9]`. For compact hand checks, BB used `n=4,k=2` and RSI used period `3`; production defaults remain `n=20,k=2` and RSI 14.
- Command: inline Python importing `detector`, `rsi_core`; called `D.bollinger_upper(closes,4,2.0)`, `rsi_core(closes,3)`, and `D.delta_sum(candles,0,9)`.

## Formula inventory and comparisons

| Formula / use | FORMULAS.md | Code evidence | Hand result vs code | Result |
|---|---|---|---|---|
| Bollinger upper: SMA of last n closes + k times population SD; unavailable before n bars | `FORMULAS.md:556`: “sd[t] = POPULATION standard deviation ... upper = mid + mult*sd”; example and warmup at `:558` | `wlow_bounce/detector.py:28-34`: rolling window, `statistics.pstdev`, mean + k*sd | At bar 9, last window `[14,16,15,17]`; mean `15.5`; population variance `(2.25+.25+.25+2.25)/4 = 1.25`; SD `1.11803399`; upper `15.5+2*1.11803399 = 17.73606798`. Code returned `17.73606797749979`. | SAME |
| Wilder RSI: first period deltas seed arithmetic mean gains/losses; recursive Wilder smoothing; RSI transform | `FORMULAS.md:12-21`, worked period-3 example `:55-57` | `wlow_bounce/detector.py:37-40` calls core; `rsi/rsi_core.py:6-10,21-47` implements seed, recurrence, transform | Period 3. Seed deltas `[+2,-1,+3]`: avg gain `5/3`, avg loss `1/3`. Recurrence through bar 9 gives avg gain `2714/2187`, avg loss `862/2187`; RSI `100-100/(1+2714/862) = 75.89485459`. Code returned `75.89485458612975`. | SAME |
| Taker delta summed over an inclusive bar interval (layer's CVD change) | `FORMULAS.md:367-368` identifies `delta = 2*tbv-v` and running sum; section 14 context | `wlow_bounce/detector.py:124-125` returns sum of `2*tbv-v` on `candles[a:b+1]` | Per-bar deltas `[4,-6,2,0,6,-8,-2,4,-4,8]`; total `4`. Code returned `4`. | SAME |
| Weekly-low reference and episode/hold trigger definitions used by detector | No corresponding `wlow_bounce` formula/contract found in `FORMULAS.md` (searched weekly-low terms; nearest generic prior-week anchor is unrelated section 18.4) | `wlow_bounce/detector.py:49-67` defines prior complete ISO week / rolling 168 bars; `:69-109` defines hold/event logic | Not hand-computed: these are not specified in FORMULAS.md, so an independent formula-vs-code comparison cannot be made from that source. | NOT_IN_DATA |

## Finding
The three formula outputs requested for numeric parity match. The audit is **FIX-FIRST** because the layer's weekly-low episode and hold/trigger rules are material detector behavior but have no matching definitions in `FORMULAS.md`; the implementation currently serves as the only checked-in definition for those rules. Add a formula contract before treating that part as independently audited.

No code edited. No development or holdout market data read.

## Follow-up cards
None.