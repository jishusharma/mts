# GPT audit: FORMULAS.md vs trendlines layer (2026-10-31)

**SOUND** - three toy outputs match; 19.1-19.9 formula family and implementation references are mapped below. The 10-bar fixture is too short for the specified 14-TR ATR, so a full candidate line cannot be formed on this fixture.

## Scope and method

Read `MyTradingSys/backtest/layers/FORMULAS.md` lines 492-514 and 591, plus `MyTradingSys/backtest/layers/trendlines/trendline_core.py` and its tests. Ran an in-memory synthetic 10-bar fixture only (no market data): lows `[12,11,10,5,9,10,11,12,13,14]`; each bar had high=low+4, close=low+2, volume=100, hourly timestamps. Command: Python here-document importing `TrendlineDetector`, `line_price`, `true_range`, and `atr_sma` from the module; output: support pivot `{i:3, price:5, available_at:6}`, linear line price `112.0`, TR at index 9 `4`, ATR at 9 `None`, zero detected lines.

## Formula mapping and checks

| FORMULAS.md | Layer implementation and evidence | Hand calculation / fixture result | Code result | Verdict |
|---|---|---|---|---|
| 19.1 strict k-bar pivot, available at i+k (FORMULAS.md:496) | `trendline_core.py:137-160`; strict neighbor comparisons and `available_at=t` | With k=3, low[3]=5 is below lows at 0-2 and 4-6; known at 3+3=6. | Support pivot i=3, price=5, available_at=6 | SAME |
| 19.2 linear/log interpolation (FORMULAS.md:499) | `trendline_core.py:52-58`; linear branch applies anchor interpolation | Independent anchors (1,100),(5,108), evaluate at 7: 100+(8)*(6/4)=112. | `line_price("linear",1,100,5,108,7)` = 112.0 | SAME |
| 19.3 TR SMA(14), ATR fixed at anchor b (FORMULAS.md:502) | `trendline_core.py:39-49`, `:163-167`; ATR needs 14 TRs | For fixture bar 9, previous close=15, H=18, L=14: TR=max(4,3,1)=4. Only 9 TR observations exist by index 9, so ATR(14) is unavailable. | `true_range(...,9)=4`; `atr_sma(...,9)=None`; no pair line | SAME for TR; NOT_IN_DATA for ATR/candidate line on this 10-bar fixture |
| 19.4 ATR and log slopes (FORMULAS.md:504) | `trendline_core.py:186-188` computes `(pb-pa)/spacing/atr_b` and log slope | The requested slope needs a valid line and ATR_b; neither is available with 10 bars and ATR(14). | No line record / slope output | NOT_IN_DATA (fixture length limitation) |
| 19.5 contact, penetration, break boundaries (FORMULAS.md:507) | `trendline_core.py:222-234` penetration; `:258-280` break/contact/poke | Formula thresholds are 0.10, 0.25 and 0 ATR_b margins; exercise would require a constructed line with ATR_b. | No such line can be created with this fixture | NOT_IN_DATA (fixture length limitation) |
| 19.6 contact episode/reset (FORMULAS.md:510) | `trendline_core.py:265-280`; reset when inside distance > RESET_DIST*ATR_b; first contact opens an episode | Reset threshold is 1.0*ATR_b; needs line state/ATR_b. | No line state on this fixture | NOT_IN_DATA (fixture length limitation) |
| 19.7 anchor volume >=2x prior-20 mean (FORMULAS.md:512) | `trendline_core.py:236-241`; requires 20 prior bars and tests anchor volume | Fixture has only 10 bars; no 20-bar baseline exists. | `_volume_ok` returns false for i<20; arm V cannot qualify | NOT_IN_DATA (fixture length limitation) |
| 19.8 arm B third pivot within 0.25 ATR_b (FORMULAS.md:514) | `trendline_core.py:273-284`; compares later pivot to `_L` within TOUCH_TOL*ATR_b | Needs an existing line, later pivot, and ATR_b. | No line exists | NOT_IN_DATA (fixture length limitation) |
| 19.9 v1.1 close-arm penetration, availability window, E11 pairing (FORMULAS.md:591) | `trendline_core.py:189-207` close-arm external test and pre-availability break; `:182-187` E11 anchor filtering; test coverage `test_trendline_core.py:237-277` | The stated v1.1 behavior is wired; not numerically exercised by the 10-bar fixture because it cannot construct an ATR-qualified line. | Relevant branches and contract tests present; fixture output not available | SAME for implementation mapping; NOT_IN_DATA for a fresh numeric replay |

## Hand-computed outputs

1. Pivot: index 3 low 5 is a strict local minimum across the 3 bars on both sides; available at index 6. Module returns the same pivot.
2. Line interpolation: `L(7)=100+(108-100)*(7-1)/(5-1)=112`. Module returns 112.0.
3. True range: at index 9, H=18, L=14, prior close=15; `max(18-14, |18-15|, |14-15|)=max(4,3,1)=4`. Module returns 4.0. ATR(14) is unavailable at index 9 (module returns `None`), so the formula's ATR-dependent line outputs cannot be produced from ten bars.

No source edits made. No follow-up cards created.
