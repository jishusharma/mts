"""Local speech-to-text for caption-less sources (faster-whisper, CPU, int8, low priority).

Runs from the dedicated venv outside the repo, so nothing here imports at repo level:
    F:/MTS/tools/asr-venv/Scripts/python.exe scripts/dev/asr_transcribe.py \
        --audio F:/MTS/data/fabio_videos/audio/<id>.f251.webm --out F:/MTS/data/fabio_videos/asr/<id>.jsonl

Design (operator approval 2026-10-16, ASR_RUN notes in research/fabio_asr_2026-10-16):
  * process priority BELOW_NORMAL, cpu_threads capped at half the logical cores (max 4), one job at a time;
  * models are the official Systran faster-whisper repos, cached under --models-dir (never in git);
  * word timestamps on, Silero VAD on (timestamps are mapped back to the original timeline);
  * resumable: each segment is appended to the JSONL as soon as it is decoded; a re-run with the same
    --out continues after the last written segment end;
  * --start/--end transcribe a slice (the model-choice timing run); timestamps stay in source seconds.
Prints one JSON summary line at the end with load/decode/transcribe seconds and the real-time factor
(RTF = transcribe seconds / audio seconds, so 0.5 means twice as fast as real time).
"""
import argparse
import json
import os
import sys
import time
from pathlib import Path

SR = 16000
HOTWORDS = ("Nasdaq NQ absorption big trades cumulative volume delta footprint "
            "liquidity heat map stop loss break even")


def log(msg, fh=None):
    line = "[%s] %s" % (time.strftime("%H:%M:%S"), msg)
    print(line, flush=True)
    if fh:
        fh.write(line + "\n")
        fh.flush()


def lower_priority():
    import psutil
    p = psutil.Process()
    if os.name == "nt":
        p.nice(psutil.BELOW_NORMAL_PRIORITY_CLASS)
    else:
        p.nice(10)
    return p.nice()


def resume_point(out):
    """(last segment end in source seconds, segments, words) already in the JSONL."""
    last, n, w = 0.0, 0, 0
    if out.exists():
        for line in out.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            try:
                r = json.loads(line)
            except ValueError:
                continue  # torn last line after a kill; the slice restarts before it
            last = max(last, float(r["end"]))
            n += 1
            w += len(r.get("words", []))
    return last, n, w


def main(argv):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--audio", required=True)
    ap.add_argument("--out", required=True, help="JSONL output (appended, resumable)")
    ap.add_argument("--model", default="medium.en", help="Systran faster-whisper model name, e.g. medium.en, small.en")
    ap.add_argument("--models-dir", default="F:/MTS/tools/asr-models")
    ap.add_argument("--start", type=float, default=0.0, help="slice start, source seconds")
    ap.add_argument("--end", type=float, default=0.0, help="slice end, source seconds (0 = to the end)")
    ap.add_argument("--threads", type=int, default=0, help="cpu_threads (0 = half the logical cores, max 4)")
    ap.add_argument("--beam", type=int, default=5)
    ap.add_argument("--no-hotwords", action="store_true")
    ap.add_argument("--fresh", action="store_true", help="ignore and overwrite an existing --out")
    a = ap.parse_args(argv)

    out = Path(a.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    logf = open(str(out) + ".log", "a", encoding="utf-8", newline="\n")
    prio = lower_priority()
    threads = a.threads or max(1, min(4, (os.cpu_count() or 2) // 2))
    log("start audio=%s model=%s threads=%d priority_class=%s" % (a.audio, a.model, threads, prio), logf)

    if a.fresh and out.exists():
        out.unlink()
    resume_from, n_seg, n_words = resume_point(out)

    from faster_whisper import WhisperModel
    from faster_whisper.audio import decode_audio

    t0 = time.time()
    model = WhisperModel(a.model, device="cpu", compute_type="int8", cpu_threads=threads, num_workers=1,
                         download_root=a.models_dir)
    load_s = time.time() - t0
    log("model loaded in %.1fs" % load_s, logf)

    t0 = time.time()
    audio = decode_audio(a.audio, sampling_rate=SR)
    decode_s = time.time() - t0
    total = len(audio) / SR
    log("decoded %.1fs of audio in %.1fs" % (total, decode_s), logf)

    lo = max(a.start, resume_from)
    hi = min(a.end, total) if a.end else total
    if lo >= hi - 1.0:
        log("nothing left to do (resume_from=%.1f, end=%.1f)" % (resume_from, hi), logf)
        return 0
    if resume_from:
        log("resuming at %.1fs (%d segments already written)" % (resume_from, n_seg), logf)
    chunk = audio[int(lo * SR):int(hi * SR)]
    audio_s = len(chunk) / SR

    import psutil
    me = psutil.Process()
    psutil.cpu_percent(None)  # prime the system-wide counter
    cpu0 = me.cpu_times()
    t0 = time.time()
    segments, info = model.transcribe(
        chunk, language="en", beam_size=a.beam, word_timestamps=True,
        vad_filter=True, vad_parameters=dict(min_silence_duration_ms=500),
        condition_on_previous_text=False,
        hotwords=None if a.no_hotwords else HOTWORDS)
    new_seg = new_words = 0
    last_log = t0
    with open(out, "a", encoding="utf-8", newline="\n") as fh:
        for s in segments:
            rec = {
                "start": round(lo + s.start, 3), "end": round(lo + s.end, 3), "text": s.text.strip(),
                "avg_logprob": round(s.avg_logprob, 3), "no_speech_prob": round(s.no_speech_prob, 3),
                "compression_ratio": round(s.compression_ratio, 3),
                "words": [[w.word, round(lo + w.start, 3), round(lo + w.end, 3), round(w.probability, 3)]
                          for w in (s.words or [])],
            }
            fh.write(json.dumps(rec, ensure_ascii=True) + "\n")
            fh.flush()
            new_seg += 1
            new_words += len(rec["words"])
            now = time.time()
            if now - last_log >= 60:
                done = rec["end"] - lo
                log("pos %.0fs/%.0fs (%.1f%%) elapsed %.0fs rtf %.3f" % (
                    rec["end"], hi, 100.0 * done / audio_s, now - t0, (now - t0) / max(done, 1.0)), logf)
                last_log = now
    transcribe_s = time.time() - t0
    cpu1 = me.cpu_times()
    my_cores = ((cpu1.user + cpu1.system) - (cpu0.user + cpu0.system)) / max(transcribe_s, 1e-6)
    summary = {
        "model": a.model, "audio": os.path.basename(a.audio), "slice": [round(lo, 1), round(hi, 1)],
        "audio_s": round(audio_s, 1), "load_s": round(load_s, 1), "decode_s": round(decode_s, 1),
        "transcribe_s": round(transcribe_s, 1), "rtf": round(transcribe_s / audio_s, 3),
        "segments": new_seg, "words": new_words, "threads": threads, "priority_class": prio,
        "vad_speech_s": round(info.duration_after_vad, 1), "beam": a.beam,
        # contention gauge: cores this job actually got (max = threads) and system-wide CPU % over the run
        "job_cores_avg": round(my_cores, 2), "system_cpu_pct": psutil.cpu_percent(None),
    }
    log("DONE " + json.dumps(summary), logf)
    with open(str(out) + ".summary.jsonl", "a", encoding="utf-8", newline="\n") as sf:
        sf.write(json.dumps(summary) + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
