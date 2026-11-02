"""Spec-derived tests for pure helpers in scripts/dev/asr_transcribe.py.

Covers:
  - resume_point:
    * nonexistent file returns (0.0, 0, 0)
    * empty file returns (0.0, 0, 0)
    * whitespace and empty lines skipped
    * single segment with word list
    * multiple segments accumulating count, words, and tracking max end
    * out-of-order segment timestamps correctly taking maximum
    * missing 'words' attribute defaulting gracefully
    * torn / corrupted trailing line handled gracefully (skips invalid JSON)
    * corrupted line in the middle skipped while valid lines parsed
  - log:
    * stdout output format with timestamp [%H:%M:%S]
    * file handle write and flush behavior
"""
import io
import json
import re
from pathlib import Path
import pytest

import asr_transcribe as asr


def test_resume_point_nonexistent_file(tmp_path):
    missing_file = tmp_path / "missing.jsonl"
    assert asr.resume_point(missing_file) == (0.0, 0, 0)


def test_resume_point_empty_file(tmp_path):
    empty_file = tmp_path / "empty.jsonl"
    empty_file.write_text("", encoding="utf-8")
    assert asr.resume_point(empty_file) == (0.0, 0, 0)


def test_resume_point_whitespace_only(tmp_path):
    ws_file = tmp_path / "ws.jsonl"
    ws_file.write_text("   \n\n\t  \n  \n", encoding="utf-8")
    assert asr.resume_point(ws_file) == (0.0, 0, 0)


def test_resume_point_single_valid_segment(tmp_path):
    f = tmp_path / "single.jsonl"
    rec = {
        "start": 1.25,
        "end": 4.5,
        "text": "bitcoin breaking high",
        "words": [
            ["bitcoin", 1.25, 2.0, 0.95],
            ["breaking", 2.05, 3.1, 0.92],
            ["high", 3.15, 4.5, 0.98],
        ],
    }
    f.write_text(json.dumps(rec) + "\n", encoding="utf-8")
    last, n_seg, n_words = asr.resume_point(f)
    assert last == 4.5
    assert n_seg == 1
    assert n_words == 3


def test_resume_point_multiple_segments_accumulate(tmp_path):
    f = tmp_path / "multi.jsonl"
    rec1 = {"start": 0.0, "end": 10.0, "words": [["one", 0, 1, 0.9], ["two", 1, 2, 0.9]]}
    rec2 = {"start": 10.0, "end": 22.75, "words": [["three", 10, 11, 0.9], ["four", 11, 12, 0.9], ["five", 12, 13, 0.9]]}
    lines = [json.dumps(rec1), json.dumps(rec2)]
    f.write_text("\n".join(lines) + "\n", encoding="utf-8")

    last, n_seg, n_words = asr.resume_point(f)
    assert last == 22.75
    assert n_seg == 2
    assert n_words == 5


def test_resume_point_out_of_order_takes_max_end(tmp_path):
    f = tmp_path / "order.jsonl"
    # End of seg1 is 50.0, seg2 is 35.0 (e.g. overlapping / adjusted window)
    rec1 = {"start": 0.0, "end": 50.0, "words": [["a", 0, 1, 0.9]]}
    rec2 = {"start": 10.0, "end": 35.0, "words": [["b", 10, 11, 0.9]]}
    f.write_text(f"{json.dumps(rec1)}\n{json.dumps(rec2)}\n", encoding="utf-8")

    last, n_seg, n_words = asr.resume_point(f)
    assert last == 50.0
    assert n_seg == 2
    assert n_words == 2


def test_resume_point_missing_words_defaults_to_zero(tmp_path):
    f = tmp_path / "no_words.jsonl"
    rec = {"start": 5.0, "end": 15.0, "text": "no word timestamps here"}
    f.write_text(json.dumps(rec) + "\n", encoding="utf-8")

    last, n_seg, n_words = asr.resume_point(f)
    assert last == 15.0
    assert n_seg == 1
    assert n_words == 0


def test_resume_point_torn_trailing_line_skipped(tmp_path):
    f = tmp_path / "torn.jsonl"
    rec1 = {"start": 0.0, "end": 12.0, "words": [["word", 0, 1, 0.9]]}
    # Torn incomplete JSON line at EOF from terminated process
    torn_content = json.dumps(rec1) + "\n" + '{"start": 12.0, "end": 18.5, "te'
    f.write_text(torn_content, encoding="utf-8")

    last, n_seg, n_words = asr.resume_point(f)
    assert last == 12.0
    assert n_seg == 1
    assert n_words == 1


def test_resume_point_corrupt_middle_line_skipped(tmp_path):
    f = tmp_path / "corrupt_mid.jsonl"
    rec1 = {"start": 0.0, "end": 8.0, "words": [["first", 0, 1, 0.9]]}
    rec2 = {"start": 8.0, "end": 16.0, "words": [["second", 8, 9, 0.9]]}
    content = f"{json.dumps(rec1)}\nCORRUPTED_NOT_JSON\n{json.dumps(rec2)}\n"
    f.write_text(content, encoding="utf-8")

    last, n_seg, n_words = asr.resume_point(f)
    assert last == 16.0
    assert n_seg == 2
    assert n_words == 2


def test_log_stdout_and_file_handle(capsys):
    buf = io.StringIO()
    asr.log("testing audio pipeline", fh=buf)

    captured = capsys.readouterr().out
    assert re.search(r"\[\d{2}:\d{2}:\d{2}\] testing audio pipeline", captured)

    file_content = buf.getvalue()
    assert re.search(r"\[\d{2}:\d{2}:\d{2}\] testing audio pipeline\n", file_content)
