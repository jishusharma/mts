# Tom/Fabio gap hunt, iteration 3: shared brief (2026-11-13)

Iteration 2 (`../tf_extraction_plan_1113/ITERATION_2.md`, 9d41c7e5) fired the stopping rule: market profile is named in 23 videos and has never been coded. So iteration 3 runs. Each topic runs on two Gemini models (flash, argon); MODEL_COMPARE.md then sorts every row into AGREED / SINGLE / CONFLICT.

Quality note 2026-11-13 (third check): Argon timestamps did not match the transcripts on IR-09 (cited [76:01], real 1:30:45), IR-18 ([100:51] vs 1:28:42), IR-19 ([130:07] vs 1:54:17). Check every Argon timestamp against the transcript before use in MODEL_COMPARE.md (card gemini-argon-timestamp-check-1113). Source: `../tf_extraction_plan_1113/THIRD_CHECK_I2_REFUTE.md`.

## The 5 gap patterns
1. **Our number labelled as his.** A number the trader never states is filled by us and labelled SOURCED.
2. **Named often, never coded.** A concept he names in many videos that has no code.
3. **One word, several claims.** For example, Tom's "70%" means three different things.
4. **Method lost in translation.** He reads by eye or from the tape; we used a fixed indicator.
5. **Transfer assumed.** Index cash-session rules applied to 24/7 BTC without his saying so.

## Iteration-2 headline gaps, to deepen rather than repeat
- **Context layer.** He reads balance from profile shape and uses a weekly value-migration read and an NY-session profile. We use a 24h UTC profile and candle-colour proxies.
- **After the fill.** 41 of 104 narrated steps happen after entry, and only 4 of those run in our code.
- **Fabio on BTC.** "I don't use order flow on Bitcoin" in Is1HvdfQm5c, versus "Saturday order flow scalping" in DyS79Eb92Ug.

## Rules
- Use transcripts on disk only: `raw_transcripts_canonical/<id>_raw.txt`.
- Copy every quote exactly and give the video id with `[mm:ss]`.
- Anything he leaves unstated is NOT_SEEN, never filled from our docs or from model knowledge.
- `verify_extract_quotes.py` must exit 0.
- Some transcripts carry sponsor copy ("World Class Edge"); never quote it.
