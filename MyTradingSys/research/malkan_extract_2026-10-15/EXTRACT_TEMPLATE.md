# MALKAN EXTRACT TEMPLATE - structure only, no content (Phase 1 workers read THIS and their transcript, nothing else)

Derived from research/krown_ta101_2026-10-13/EXTRACT_TEMPLATE.md + PROTOCOL.md (the newest protocol, concept format; the V2 trade-recap
format is NOT used because Malkan teaches concepts and does not recap trades; this resolves the conflict with
LAYER_REBUILD_PLAN_2026-10-15.md, which names V2). Changes against the Krown template, and why:
- The repo's Malkan transcripts (raw_transcripts_canonical/<id>_raw.txt) carry NO timestamps, so `t=` cannot be written. Positions are
  given as BEGIN / MIDDLE / END of the body (by character position) wherever Krown uses t=.
- Added: Source class (PRIMARY = Malkan speaks, SECONDARY = another presenter explains Malkan), Language, and a Setups section
  (entry / stop / target in his words, or NOT STATED) because the output feeds a setup summary.
- Hindi videos: quote the Hindi original AND the English translation; the translation is machine-made (YouTube MT of Hindi ASR).

File name: `extracts/extract_<VIDEO_ID>.md`. Input: `raw_transcripts_canonical/<VIDEO_ID>_raw.txt` (header lines start with `#`, body after `# ---`).
Hindi videos also have `raw_transcripts_canonical/<VIDEO_ID>_hi_raw.txt` (Devanagari auto ASR; the original audio is Hindi).
LF line endings, ASCII only EXCEPT Devanagari inside `- Hindi original:` lines. One video per file, one worker per video.

```
# MALKAN EXTRACT - <VIDEO_ID> - <title>

- Video ID: <id>
- Title: <exact>
- Published: <date or unknown>
- Uploader: <from the header>
- Source class: PRIMARY (Malkan speaks) | SECONDARY (<name of presenter>; explains Malkan's system, label every claim as theirs)
- Language: en | hi (original audio Hindi; English file = YouTube machine translation, MACHINE-MADE)
- Caption source: <from the header>
- Word count: <n>
- Analyst: Vishal B Malkan (@Malkansview). Evidence tier: T3 (ideas/definitions only; a quote is not evidence of edge).
- Series note: <episode number only if said>
- Scope note: <only if the video is not about trading setups>

## Concepts

### M-<VIDEO_ID>-<NN> <short name in his terms>
- Type: LEVEL | ENTRY-TRIGGER | EXIT/STOP | INDICATOR | PATTERN | CONTEXT/REGIME | PROCESS | RISK/SIZING | MENTAL-MODEL | SETUP
- Side: long | short | both | none          (as said; never infer; "none" for context rules)
- Stated mechanics: <what he says, every number exactly as spoken; "no numbers given" if none>
- Quotes:
> "<verbatim words from the English file, one passage, no ellipsis>"
**Source GPS: <VIDEO_ID> | BEGIN or MIDDLE or END**
- Hindi original: "<verbatim Devanagari from the _hi_raw file, same passage>"      (Hindi videos only, one line per quote)
- Translation status: MACHINE-MADE                                                (Hindi videos only)
- Inferred: <only if you inferred something; start with INFERRED:. Where the machine translation is garbled, give your reading of the Hindi here, INFERRED>

## Setups
(One block per distinct setup he teaches, in his name for it. Every field is a quote or the literal text NOT STATED.)
### S-<VIDEO_ID>-<NN> <name>
- Context / what the chart shows: <his words>
- Entry: <quote + GPS, or NOT STATED>
- Stop: <quote + GPS, or NOT STATED>
- Target: <quote + GPS, or NOT STATED>
- Timeframe / indicator settings: <quote + GPS, or NOT STATED>
- Side: long | short | both
- Concept ids that support it: M-...

## Framing and mental models
(quote + GPS lines, one idea each)

## Negative rules
(what he says NOT to do; quote + GPS lines)

## Gaps
- <every threshold, stop, target, size, lookback or definition he leaves open or defers, with position BEGIN/MIDDLE/END>
- If he gives no stop, target or sizing, write that as its own line.
```

Rules:
1. GPS third: BEGIN = first third of the body, MIDDLE = second third, END = last third (by character position of the English file). The gate checks it. In a quote block under a Setups field the same `> "..."` + GPS pair is used (quote line, then the GPS line right after).
2. A concept exists only if a verbatim quote supports it (in-vivo rule). No concept from memory, from other videos, from the title or from what you know about the RSI 5 star system.
3. Numbers: copy digits as spoken. If the caption is garbled, copy it and write INFERRED. Do not convert units.
4. Do not map to our labels (CT, TC, Tom, Fabio, "layer", "setup family"). Describe in his words.
5. Do not write the mirror rule unless he states it. Side per what he says.
6. A hypothetical illustration is a concept with "(illustration)" in the name; open profit is not a target.
7. Losing or failed examples get the same detail as winners.
8. Admitted errors and rejections ("I would not...") go under Negative rules.
9. No cross-references to other videos' content. If he refers to another episode, write his words only.
10. Secondary presenter: everything the presenter says is theirs; mark it so in the concept name or Stated mechanics.
11. Machine-translated text can be garbled (names, numbers, "RSI" turned into other words). Quote what the file says; put your reading in `Inferred:`. Never repair a quote.
12. Finish with the gates passing; paste their last lines at the end of your reply, not into the file:
```
python -I scripts/dev/verify_extract_quotes.py MyTradingSys/research/malkan_extract_2026-10-15/extracts/extract_<ID>.md
python -I MyTradingSys/research/malkan_extract_2026-10-15/tools/check_numbers.py MyTradingSys/research/malkan_extract_2026-10-15/extracts/extract_<ID>.md
python -I MyTradingSys/research/malkan_extract_2026-10-15/tools/check_hindi.py MyTradingSys/research/malkan_extract_2026-10-15/extracts/extract_<ID>.md     (Hindi videos only)
```
