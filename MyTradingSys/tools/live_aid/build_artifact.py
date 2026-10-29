"""Build the one-file Artifact copy of live_aid.html (indicators inlined, preview note added).

The claude.ai viewer blocks exchange websockets and fetches (CSP), so the Artifact is a layout
preview whose feeds read NOT_IN_DATA; the live page is live_aid.html opened from disk.
Usage: python build_artifact.py <out.html>
"""
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
TAG = '<script src="live_aid_indicators.js"></script>'
NOTE = ('<p class="tag" id="preview-note">Preview copy. The claude.ai viewer blocks exchange connections, so every feed '
        'here reads NOT_IN_DATA. Live page: open MyTradingSys/tools/live_aid/live_aid.html from disk in Chrome or Edge.</p>')


def build() -> str:
    page = (HERE / "live_aid.html").read_text(encoding="utf-8")
    js = (HERE / "live_aid_indicators.js").read_text(encoding="utf-8")
    assert page.count(TAG) == 1 and page.count("<main>") == 1
    return page.replace(TAG, "<script>\n" + js + "</script>").replace("<main>", "<main>\n  " + NOTE, 1)


if __name__ == "__main__":
    Path(sys.argv[1]).write_text(build(), encoding="utf-8", newline="\n")
