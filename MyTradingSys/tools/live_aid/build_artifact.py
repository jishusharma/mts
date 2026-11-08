"""Build the one-file Artifact copy of live_aid.html (indicators inlined, preview note added).

The claude.ai viewer blocks exchange websockets and fetches (CSP), so the Artifact is a layout
preview whose feeds read NOT_IN_DATA; the live page is live_aid.html opened from disk.
Usage: python build_artifact.py <out.html>
"""
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
# Every page-local script is inlined; a tag left as a src= would read "—" in the Artifact (2026-11-06: tf_strip.js).
TAGS = ('<script src="live_aid_indicators.js"></script>', '<script src="news_feed.js"></script>', '<script src="news_weight.js"></script>', '<script src="events_strip.js"></script>', '<script src="events_strip_data.js"></script>', '<script src="tf_strip.js"></script>', '<script src="ma_strip.js"></script>',
        '<script src="cycle_flag_data.js"></script>', '<script src="cycle_flag.js"></script>')
TAG = TAGS[0]
NOTE = ('<p class="tag" id="preview-note">Preview copy. The claude.ai viewer blocks exchange connections, so every feed '
        'here reads NOT_IN_DATA. Live page: open MyTradingSys/tools/live_aid/live_aid.html from disk in Chrome or Edge.</p>')


def build() -> str:
    page = (HERE / "live_aid.html").read_text(encoding="utf-8")
    assert page.count("<main>") == 1
    for tag in TAGS:
        name = tag.split('"')[1]
        js = (HERE / name).read_text(encoding="utf-8")
        assert page.count(tag) == 1, name
        page = page.replace(tag, "<script>\n" + js + "</script>")
    return page.replace("<main>", "<main>\n  " + NOTE, 1)


if __name__ == "__main__":
    Path(sys.argv[1]).write_text(build(), encoding="utf-8", newline="\n")
