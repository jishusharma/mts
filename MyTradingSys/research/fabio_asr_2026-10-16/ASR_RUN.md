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
(filled when the run ends: see section 5)

## 4. Limits of this transcript (read before quoting)
- Machine transcription, not captions: numbers, tickers and contract counts can be misheard; every quote from it is labelled ASR and the frames stay the arbiter for prices.
- No speaker labels. Is1HvdfQm5c is Fabio answering live chat questions (viewer names are spoken: "Tom", "Amano"); xUyqIjCfZzg has TWO traders (Fabio and Carmine Rosato). The extracts mark the speaker UNKNOWN wherever the words do not settle it.
- Whisper hallucinates credit lines on silence ("Subs by www..."); `asr_to_canonical.py` drops them and counts them in the header (`# ASR QA`).
- Stream audio with chat/music gaps: VAD drops non-speech, so line timestamps are speech-only, but they stay on the original video timeline.

## 5. Result
(filled at the end)
