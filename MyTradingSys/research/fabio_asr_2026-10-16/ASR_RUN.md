# Fabio ASR run: local speech-to-text for the two uncaptioned live sessions (2026-10-16)

Operator approval, 2026-10-16 (verbatim): "Yes: install a local open-source transcriber on JIS-NB, run it at low priority on Fabio's two long sessions (Is1HvdfQm5c, xUyqIjCfZzg), and extract them." This flips Fable's D2 (CATALOGUE_AUDIT.md s6, default NO) to YES; logged as `q-fabio-asr-d2` in system/OPERATOR_DECISIONS.md.

## 1. What was run
| item | value |
|---|---|
| sources | Is1HvdfQm5c "World Cup Trader Reveals His Order Flow LIVE", HijoTrades, 2026-09-28, 2:28:01 (8,881 s); xUyqIjCfZzg "Trading LIVE with TWO World Class Order Flow Scalpers (FT Fabio Valentini & Carmine Rosato)", Chart Fanatics, 2026-05-17, 3:49:37 (13,777 s). Total 22,658 s = 6.29 h |
| audio | the `.f398.mp4` files on F: are VIDEO-ONLY (no audio track: checked for `soun`/`mp4a` atoms). The audio-only YouTube stream (format 251, opus webm) was fetched with yt-dlp into `F:/MTS/data/fabio_videos/audio/` (108 + 188 MiB; YouTube is pre-approved in CLAUDE.md). Not in git |
| engine | `faster-whisper` 1.2.1 (SYSTRAN, PyPI) on CTranslate2 4.8.3, CPU, int8; venv `F:/MTS/tools/asr-venv` (outside the repo). `av` pinned to 16.1.0: av 19 breaks faster-whisper 1.2.1 (`open() got an unexpected keyword argument 'metadata_errors'`) |
| models | official `Systran/faster-whisper-{small,medium}.en` from Hugging Face, cached in `F:/MTS/tools/asr-models` (not in git) |
| low priority | process class BELOW_NORMAL (set by psutil inside `scripts/dev/asr_transcribe.py`), `cpu_threads` 4 (half of 8 logical cores, the cap), `num_workers` 1, one video at a time, background; no live process touched |
| decode | beam 5, language en, word timestamps on, Silero VAD on (min silence 500 ms), `condition_on_previous_text` off, hotwords "Nasdaq NQ absorption big trades cumulative volume delta footprint liquidity heat map stop loss break even" (vocabulary hint only) |
| outputs | word-level JSONL + logs in `F:/MTS/data/fabio_videos/asr/` (not in git); canonical transcripts `raw_transcripts_canonical/<id>_raw.txt` (in git, like the other 129) |
| code | `scripts/dev/asr_transcribe.py` (resumable run), `scripts/dev/asr_to_canonical.py` (JSONL -> canonical), `scripts/dev/test_asr_to_canonical.py` |

## 2. Model choice: DECISION (OURS) small.en
Rule from the task: time a 5-minute slice with medium.en and small.en; medium.en only if the projected total for both videos is 8 h or less. Slice = Is1HvdfQm5c 1800-2100 s (live commentary, VAD speech 223.7 s). RTF = transcribe seconds / audio seconds. JIS-NB was CPU-saturated by other sessions during all runs, so RTF swings with the cores the job got (`job_cores_avg`, max 4); the figures are real wall-clock under that load, not best case.

| run | model | beam | RTF | cores got | system CPU | words | speech covered |
|---|---|---|---|---|---|---|---|
| 1 | small.en | 5 | 2.058 | n/a | n/a | 546 | 280 s |
| 1 | small.en | 1 | 0.244 | n/a | n/a | 549 | |
| 2 | medium.en | 5 | about 10.1 (stopped: 114 s of the 300 s slice done in 1,146 s) | n/a | 99 % | | |
| 4 | small.en | 5 | 0.299 | 3.15 | 90 % | 546 | 280 s |
| 4 | medium.en | 1 | 0.538 | 3.75 | 76 % | 469 | 234 s |
| 4 | medium.en | 5 | 1.743 | 2.16 | 95 % | 555 | 286 s |
| 4 | small.en | 1 | 1.394 | 0.85 | 100 % | 545 | |

- medium.en, beam 5 (the faster-whisper default and the quality setting): 1.743 x 22,658 s = 39,500 s = **11.0 h > 8 h** (run 2 would project to about 64 h). Rule fails: not medium.en.
- medium.en greedy (beam 1) fits (0.538 -> 3.4 h) but dropped a 11 s passage ("remember that also the small position ... one to three point nine") and 52 s of covered speech in the slice, so it is rejected on recall; extraction needs every sentence.
- small.en, beam 5: 0.299 (best) to 2.06 (worst load) -> 1.9 h to 13 h projected. Chosen: **small.en, beam 5**. Text quality on the slice read fine (jargon: "absorbed", "naked POC", "squeeze", contract counts correct).

## 3. Full run
| video | audio | model | transcribe time | RTF | job cores (avg) | segments / words | state |
|---|---|---|---|---|---|---|---|
| Is1HvdfQm5c | 8,881 s (2.47 h) | small.en beam 5 | 15,366 s (4.27 h) | 1.73 | 0.66 | 997 / 17,283 | DONE 2026-10-16 08:49 IST (3 low-confidence segments, 0 dropped credit lines) |
| xUyqIjCfZzg | 13,777 s (3.83 h) | small.en beam 5 | running | about 1.0 to 1.7 expected (4 to 6.5 h) | | | restarted 10:43 IST after a machine restart killed the first job; resumable |

Contention: the RTF swings with what else the machine runs (the 5-minute benchmark gave 0.30 idle and 2.06 loaded); the job got 0.66 of a core on average over Is1H because the shipping gate and other sessions ran at the same time.

Convert xUyqIjCfZzg when `F:/MTS/data/fabio_videos/asr/xUyqIjCfZzg.jsonl.summary.jsonl` exists (the job is done):
```
python scripts/dev/asr_to_canonical.py --jsonl F:/MTS/data/fabio_videos/asr/xUyqIjCfZzg.jsonl --id xUyqIjCfZzg --title "Trading LIVE with TWO World Class Order Flow Scalpers (FT Fabio Valentini & Carmine Rosato)" --published 2026-05-17 --uploader "Chart Fanatics" --model small.en --date 2026-10-16 --note "two speakers (Fabio Valentini and Carmine Rosato); ASR has no speaker labels" --out raw_transcripts_canonical/xUyqIjCfZzg_raw.txt
```
If the job died (restart), start the same command again WITHOUT --fresh (section 1): it resumes from the last written segment. Card: fabio-xuyq-asr-extract.

## 4. Limits of this transcript (read before quoting)
- Machine transcription, not captions: numbers, tickers and contract counts can be misheard; every quote from it is labelled ASR and the frames stay the arbiter for prices.
- No speaker labels. Is1HvdfQm5c is Fabio answering live chat questions (viewer names are spoken: "Tom", "Amano"); xUyqIjCfZzg has TWO traders (Fabio and Carmine Rosato). The extracts mark the speaker UNKNOWN wherever the words do not settle it.
- Whisper hallucinates credit lines on silence ("Subs by www..."); `asr_to_canonical.py` drops them and counts them in the header (`# ASR QA`).
- Stream audio with chat/music gaps: VAD drops non-speech, so line timestamps are speech-only, but they stay on the original video timeline.

## 5. Result (2026-10-16)
- model small.en (beam 5, int8, VAD on, word timestamps), RTF 1.73 on Is1HvdfQm5c.
- audio transcribed and extracted so far: 2.47 h (Is1HvdfQm5c); 3.83 h (xUyqIjCfZzg) still to do.
- Is1HvdfQm5c: raw_transcripts_canonical/Is1HvdfQm5c_raw.txt (932 lines, 17,227 words) and extracts/v2/fabio/Is1HvdfQm5c_v2.md (333 decision rows, 9 trade blocks, quote checker PASS). Finding: mostly teaching and viewer Q&A; no confirmed live fill with stated entry and stop.
- Catalogue: ASR quotes added to FAB-1 (momentum entry at a wall: worst case), FAB-2 (absorbed buyers, small stop above the area, 1 to 4.5 [ASR number]), FAB-4 (counter-trend reversal declined), FAB-5 ("the squeeze setup", stop below the area), FAB-8 (micro gap = inefficient volume), plus the names 'virgin POC test', 'last sniper', 'deep effort' under Fabio: unassigned. No new FAB row: no second video states entry, stop and target.
- Commits: c2e2f6ce (tooling), c2c555b1 (transcript + addendum), 0b4240ec (extract); the catalogue and card commit follows (see git log of this folder).

