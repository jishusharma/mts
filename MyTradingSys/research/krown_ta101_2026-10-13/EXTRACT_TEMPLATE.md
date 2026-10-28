# KROWN EXTRACT TEMPLATE - structure only, no content (Phase 1 workers read THIS, never another extract)

Why this file exists: methodology/extraction.md SAFEGUARD 5 (clean slate) forbids loading prior extractions during Phase 1.
The old STATE.md pointed workers at extracts/extract_HhV4HI9p5Uw.md as the format example; that is replaced by this skeleton.

File name: `extracts/extract_<VIDEO_ID>.md`. Input: `transcripts/<VIDEO_ID>_timed.txt` (one caption per line as `[HH:MM:SS] text`).
LF line endings, ASCII only. One video per file, one worker per video.

```
# KROWN TA101 EXTRACT - <VIDEO_ID> - <title>

- Video ID: <id>
- Title: <exact>
- Published: <date or unknown>
- Duration: <seconds> s (<mm:ss>)
- Caption source: yt_dlp captions (<manual|auto>); uploader: Krown
- Word count: <n>
- Analyst: Krown (@ECKrown), playlist TA 101 - Everything You Need To Know. Evidence tier: T3 (ideas/definitions only; a quote is not evidence of edge).
- Series note: <episode number only if he says it>
- Scope note: <only if the video is not technical analysis>

## Concepts

### K-<VIDEO_ID>-<NN> <short name in his terms>
- Type: LEVEL | ENTRY-TRIGGER | EXIT/STOP | INDICATOR | PATTERN | CONTEXT/REGIME | PROCESS | RISK/SIZING | MENTAL-MODEL
- Side: long | short | both | none          (as he says it; never infer; write "none" for context rules)
- Stated mechanics: <what he says, with every number exactly as spoken; "no numbers given" if none>
- Quotes:
> "<verbatim words, one passage, no ellipsis>"
**Source GPS: <VIDEO_ID> | BEGIN | t=HH:MM:SS**
- Inferred: <only if you inferred something; start with INFERRED:>

## Framing and mental models
(quote + GPS lines, one idea each)

## Negative rules
(what he says NOT to do; quote + GPS lines)

## Gaps
- <every threshold, stop, target, size, lookback or definition he leaves open or defers, with (t=HH:MM:SS)>
- If he gives no stop, target or sizing, write that as its own line.
```

Rules (all from the lessons list in PROTOCOL.md):
1. GPS third: BEGIN = first third of the body, MIDDLE = second third, END = last third (by character position). The gate checks it.
2. A concept exists only if a verbatim quote supports it (in-vivo rule). No concept from memory, from other videos or from the title.
3. Numbers: copy digits as spoken. If the caption is garbled, copy it and write INFERRED. Do not convert units.
4. Do not map to our labels (CT, TC, Tom, Fabio, "layer", "setup family"). Describe in his words. Mapping is Phase 2.
5. Do not write the mirror rule unless he states it. Write Side per what he says.
6. A hypothetical illustration is a concept with `Type` as usual and "(illustration)" in the name; open profit is not a target.
7. Losing or failed examples get the same detail as winners.
8. Admitted errors, rejections ("I would not...") go under Negative rules.
9. No cross-references to other videos' content. If he refers to another episode, write his words only.
10. Finish with both gates passing (below); paste their last lines at the end of your reply, not into the file.
```
python -I scripts/dev/verify_extract_quotes.py MyTradingSys/research/krown_ta101_2026-10-13/extracts/extract_<ID>.md
python -I MyTradingSys/research/krown_ta101_2026-10-13/tools/check_numbers.py MyTradingSys/research/krown_ta101_2026-10-13/extracts/extract_<ID>.md
```
