# Spec tests for `fetch_captions.py`

**13 tests pass; 3/3 scratch mutations detected.** Added `scripts/dev/test_fetch_captions.py` and registered it in `scripts/dev/extra_tests.tsv`.

## Checked and run

- Read `scripts/dev/fetch_captions.py` lines 1-125. Audited pure components covering `vid_of`, `vtt_to_text`, `pick_track`, and `fetch`.
- Branches covered:
  - `vid_of`: raw 11-char ID extraction, leading hyphen support, standard YouTube watch URL, youtu.be short URL, query parameter handling (timestamps, playlists), fragment handling, and invalid length / malformed string validation raising `ValueError`.
  - `vtt_to_text`: WebVTT header removal, comment/Kind/Language/NOTE lines filtering, timestamp and digit cue filtering, HTML tag stripping (`<c>...</c>`), HTML entity unescaping (`&gt;`, `&lt;`, `&amp;`), consecutive duplicate line collapse, phrase echo deduplication via regex (`\b(\w+(?: \w+){2,8}) \1\b`), and empty string handling.
  - `pick_track`: priority of manual subtitles over automatic captions, language candidate precedence order matching `langs`, fallback to `-orig` language keys, and graceful `(None, None)` return when no subtitles match.
  - `fetch`: existing file fast path returning `EXISTS` with zero network calls, `NOCAPS` handling when no tracks match, `BLOCKED` classification on HTTP 429 (`guard.BLOCK_MARKS`), `PRIVATE` classification on private/members-only messages, and canonical metadata header write (`# Video ID:`, `# Title:`, `# Published:`, `# Source:`, `# Analyst:`, `# Word count:`).
- `python -m pytest scripts/dev/test_fetch_captions.py -v`: **13 passed in 0.52s**.
- Scratch mutations verified:
  - M1: `vid_of` modified to return `m.group(0)` instead of `m.group(1)` (**FAILED: 1 failed, 12 deselected**; caught by `test_vid_of_standard_and_variations`).
  - M2: Disabled HTML tag stripping `re.sub(r"<[^>]+>", "", line)` in `vtt_to_text` (**FAILED: 1 failed, 12 deselected**; caught by `test_vtt_to_text_basic_cleaning`).
  - M3: Inverted manual vs auto precedence order in `pick_track` to `((autos, "auto"), (subs, "manual"))` (**FAILED: 1 failed, 12 deselected**; caught by `test_pick_track_manual_priority_over_auto`).
- Audited source unchanged: SHA-256 of `scripts/dev/fetch_captions.py` is `de9ebc38f21ea553951a28db9de05da1c393cc546b9c8985472caf1ae8547989`.

## Findings

| Severity | File:line | Result | Evidence | Proposed fix |
|---|---|---|---|---|
| LOW | `scripts/dev/fetch_captions.py:1-125` | MATCH | Pure functions match docstring specification and error fallbacks. Audited source hash unchanged. | None. |
| LOW | `scripts/dev/extra_tests.tsv:173` | MATCH | Registered `scripts/dev/test_fetch_captions.py` into extra tests. | None. |

## Follow-up cards

None.
