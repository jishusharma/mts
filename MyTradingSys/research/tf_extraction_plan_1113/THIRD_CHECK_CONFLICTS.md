# Third check of the 5 iteration-3 conflicts (read from transcripts, 2026-11-13)

Method: read `raw_transcripts_canonical/<id>_raw.txt` directly; neither model was trusted. Tom = Tom Vorwald videos (no `[m:ss]` stamps in his cleaned files, so none are given for him); Fabio = Fabio Valentini videos (stamps from the caption file).

## 1. Verdicts

| id | question | verdict | one line |
|---|---|---|---|
| BS-49 | Do Tom or Fabio use D / b / P / B profile shapes? | BOTH-RIGHT-DIFFERENT-SCOPE | Tom uses the letters D, P, B (his own "PBD logic": D = balance, P = aggressive up, B = aggressive down), never "b-shape" or "D-shape". Fabio says "P-shape" and "double distribution" but never D or B. Argon right on the concept, Flash right on the literal word. |
| MG-08 | Does Tom (and Fabio) trail a clean target? | BOTH-RIGHT-DIFFERENT-SCOPE | Tom: conditional, default NO on a clean planned target (about 6:1), YES behind a liquidity line when he thinks the move has further to go. Fabio: YES, trails (aggressively) once in floating profit. Flash's "always" and Argon's "does not" are each one speaker. |
| MG-11 | Hold the full target vs partials when well ahead | BOTH-RIGHT-DIFFERENT-SCOPE | They do not conflict. The day-P&L rule is stated outright in 8CWKfoSJu3c (down on the day: take profit to break even; up $27k: do not be conservative). DyS79Eb92Ug is a general talk about not set-and-forget on a personal account, with no day-P&L state. |
| NY-12 | Opening-range window length | BOTH-RIGHT-DIFFERENT-SCOPE | Fabio states 15, 30 and 60 minutes in cUTsoU-15Tc. Argon's {15, 30} is the same sentence minus the 60; Flash's {15, 30, 60} is complete. The ORB headline is 15; the IVB is plotted over 30. No other video cited. |
| OL-05 | Malkan buy-stop entry above the signal candle's high, SL below its low, 2:1 | CONFIRMED (substance); NOT gate-verified | In `W1HrDl70Lhk_asr_raw.txt` at [9:03] (and 6 more places). The words "buy stop" are never said; "buy above the high of the candle" is. The `_raw.txt` (YouTube machine-translated) file lacks the sentence. |

## 2. Evidence

### BS-49 (BOTH-RIGHT-DIFFERENT-SCOPE)

Grep over all 161 base transcripts (`_asr_` and `_hi_` skipped) for "b-shape", "b shape", "D shape", "D-shape": 0 hits. "P-shape" / "P shape": 5 hits (3 videos, all Fabio or Tom's "P-shaped"). "double distribution": 3 videos.

Per trader, what each shape means:

| trader | shape word | video | meaning he gives |
|---|---|---|---|
| Tom | D profile | `Of_wlv3xaZo` | "a D profile here, a balanced day" |
| Tom | D (PBD logic) | `m3IMdc7QwN4` | D = large balance phase |
| Tom | P profile / P's | `m3IMdc7QwN4`, `UOBgXV20yCM`, `Ly62G168MkQ`, `0CrkbfuIhkc`, `lO-Iptd29t4`, `OUM9LYwL8eA` | aggressive trend phase up; imbalance on the buy side |
| Tom | B profile / B's | `m3IMdc7QwN4`, `vk0mkNPuhDc`, `rFPCtOcfUMI`, `tS6ZEiHj8gQ`, `BVpYGKz9PBU`, `OUM9LYwL8eA` | aggressive trend phase down; first sign of strong aggressive selling; weakness |
| Tom | double distribution | `-dMWA_bbm3o`, `K8qtT2_axPo` | two profiles in one day, needs a single print between |
| Tom | "P-shaped" | `gFJBg8Bsw68` | aggressive buying with single prints |
| Fabio | P-shape | `Pz8f0wWW12M` [30:09], [34:41]; `DyS79Eb92Ug` [1:14:28], [1:38:23] | volume built on the top part, POC above 50% of range, thin absorbed low; buyers in control, trend up expected |
| Fabio | double distribution | `Pz8f0wWW12M` [31:35] | thin low, big profile on the upside |
| Fabio | D, B, b | none | not said |

Note for coding: Tom's PBD letters are his own phase model (profile plus closing-price count), not a pure volume-profile shape. Fabio's P-shape is a volume-profile shape. Our Java `shape` (P for any skew) matches neither exactly.

> "By the way, the D's are nothing more than large balance phases. The P's are the aggressive trend phases upwards, and the B's are the aggressive trend phases downwards."
**Source GPS: m3IMdc7QwN4 | END**

> "This is a P-shape, so the buyers from daily point of view are in control of the movement. You can see that also the POC is higher. It's located above the 50%."
**Source GPS: Pz8f0wWW12M | END**

> "We have a D profile here, a balanced day"
**Source GPS: Of_wlv3xaZo | MIDDLE**

### MG-08 (BOTH-RIGHT-DIFFERENT-SCOPE, speaker split)

Every trail line found in the four named videos plus the other Fabio cites:

| trader | video | where | what | trail? |
|---|---|---|---|---|
| Tom | `k0zm5NYn0IQ` | no stamp | "Trailing the stop loss is something a lot of people like to do. In this case, I don't do that" (about 6:1); later moves the stop of the remainder to 310 after taking profit | no on a clean plan |
| Tom | `UOBgXV20yCM` | no stamp | trailing would often have earned more, "why didn't Tom do that?"; he does not, because his predefined levels often get a quick reversal; a moved-up stop turns the trade into 1:1 | no |
| Tom | `e83njGZFrPw` | no stamp | "I decided to trail the stop loss at some point", at a liquidity dividing line; "The second option would be to trail a stop-loss accordingly, especially when you think the market still has a journey ahead" | yes, conditional |
| Fabio | `Is1HvdfQm5c` | [1:20:33], [1:21:20], [2:16:04] | stop in profit below the big trade near target; "aggression trailing"; tells a viewer "you trail your stop" | yes |
| Fabio | `DyS79Eb92Ug` | [11:26], [20:07], [24:08], [55:41] | trail once buyers/sellers take over or structure fails; [1:18:08] is a story about a CFD account | yes |
| Fabio | `8CWKfoSJu3c` | [2:26], [3:03], [8:59] | "trailing aggressively my stop loss"; "aggressive trailing stop that I take when we have already a nice floating profit" | yes, once floating profit |
| Fabio | `Pz8f0wWW12M` | [40:23], [40:28] | "you can trail your position following the aggression of the market" | yes |

Per trader: Tom conditional (default no on a clean target); Fabio yes (conditional on floating profit and structure). Flash's "always trail" is too strong for Tom; Argon's "Tom does not trail" is too strong because `e83njGZFrPw` has him trailing.

> "Trailing the stop loss is something a lot of people like to do. In this case, I don't do that because I just see that the overall position with a riskreward ratio of about 6 to1 is simply so good that I don't worry about it."
**Source GPS: k0zm5NYn0IQ | BEGIN**

> "The second option would be to trail a stop-loss accordingly, especially when you think the market still has a journey ahead of it."
**Source GPS: e83njGZFrPw | END**

> "This is an aggressive trailing stop that I take when we have already a nice floating profit."
**Source GPS: 8CWKfoSJu3c | BEGIN**

### MG-11 (BOTH-RIGHT-DIFFERENT-SCOPE, they do not conflict)

Context at each passage:

| video | day-P&L state at that moment | what he says |
|---|---|---|
| `8CWKfoSJu3c` [5:03-5:27] | up $27,000 realised plus $12,000 floating | explicit day-P&L rule: "if you were in loss for the day, for example, let's say minus 5,000, it will be smart to take profit and to bring your balance back to break even"; up big, "doesn't make sense to be super conservative on the profit taking" |
| `DyS79Eb92Ug` [44:48-45:25] | no P&L stated; general interview talk about statistics (max standard deviation reached about 1 session in 10) | "traders think in terms of set and forget ... I go to eat pizza. I cannot do this", having seen 1:20 to 1:30 go back to zero, you "start to take partials" on a personal account; he then calls it "totally a personal opinion" |

So the day-P&L-keyed rule neither model states is stated by Fabio himself in `8CWKfoSJu3c`: flat or down on the day, take profit to reach break even; well up, hold. `DyS79Eb92Ug` is about giving back open profit on one trade, not about day P&L. Not a contradiction; a scope split (day-P&L state vs open-trade giveback).

> "if you were in loss for the day, for example, let's say minus 5,000, it will be smart to take profit and to bring your balance back to break even so you can take a next trade in a calm way."
**Source GPS: 8CWKfoSJu3c | MIDDLE**

> "considering that we have $27,000 profit plus $12,000 profit floating for the day. Doesn't make sense to be super conservative on the profit taking."
**Source GPS: 8CWKfoSJu3c | MIDDLE**

> "And when it's personal account and when you are giving back to the market 40 50,000 trust me that you start to take partials."
**Source GPS: DyS79Eb92Ug | BEGIN**

### NY-12 (BOTH-RIGHT-DIFFERENT-SCOPE)

Every window length Fabio states in `cUTsoU-15Tc` (the only video cited):

| stamp | window | context |
|---|---|---|
| [0:06] | 15 min | ORB headline: "breakout of the first 15 minutes of the cash session" |
| [2:12] | 15, 30 or 60 min | two defined levels; "depends how you want to use it", scalp vs intraday bias |
| [2:34] | 15 or 30 min | "first 15 minutes of New York opening or 30" |
| [3:18] | 15 min | value computed "using the first 15 minutes of the session without implementing volume" |
| [4:30] | 15 to 30 min | point A and point B; "for 15 30 depends on what you prefer" |
| [10:53], [11:16], [16:36], [20:46] | 30 min | IVB is plotted and waited out over the first 30 minutes (the range "is expanding till you don't have the closure of the first 30 minutes") |

Window set he states: {15, 30, 60}, 60 only once, at [2:12]. The IVB model itself is 30. Our IB_LEN = 30 stays OURS.

> "You have two defined levels that are the top and the bottom of the range of the first 15, 30 or 60 minutes. It depends how you want to use it."
**Source GPS: cUTsoU-15Tc | BEGIN**

> "We have a top. We have a bottom on the first 15 to 30 minutes."
**Source GPS: cUTsoU-15Tc | BEGIN**

> "The range is expanding till you don't have the closure of the first 30 minutes."
**Source GPS: cUTsoU-15Tc | MIDDLE**

### OL-05 (CONFIRMED on substance; exempt from the gate)

The quote exists only in `raw_transcripts_canonical/W1HrDl70Lhk_asr_raw.txt` (Malkan, "5 Star RSI Strategy", ASR). The gate reads only `W1HrDl70Lhk_raw.txt`, which has the machine-translated version without this sentence, so it is NOT in a gate block here (a gate block would exit 1). Verified by hand against `_asr_raw.txt` (normalised substring match, lines 59-61):

Quote text (no gate block, deliberately): "candle formed so we will buy above the high of the candle stop loss will be below the low of the candle risk reward will be 2 to 1" (`W1HrDl70Lhk_asr_raw.txt`, [8:52]-[9:03]; position MIDDLE of the 18:12 video, hence third 2 of 3).

Same pattern repeats in the same file at [5:23] (stop at the high of the candle / below the low), [8:27] ("entry above the high of the candle stop loss will be below the low of the candle"), [11:06], [12:09]. Sell side mirrored at [6:04], [14:49]. Risk-reward 2-1 is stated at [7:11] and [9:03]; at [5:23] he notes the video did not state a target. Caveats: "buy stop" as an order type is never said (entry "above the high" is the observable rule); the 2:1 is not on every example (some targets are RSI 60).

verified by hand against `_asr_raw.txt`
