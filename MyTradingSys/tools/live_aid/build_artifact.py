"""Build the one-file Artifact copy of live_aid.html (indicators inlined, preview note added), and the phone-width playbook page.

The claude.ai viewer blocks exchange websockets and fetches (CSP), so the Artifact is a layout
preview whose feeds read NOT_IN_DATA; the live page is live_aid.html opened from disk.
Usage: python build_artifact.py <out.html>               (the live aid preview)
       python build_artifact.py --playbook <out.html>    (daily session playbook, phone width; data from playbook_data.js)
The playbook page needs no feed: daily_playbook.py computes everything, so it shows real numbers in the viewer.
"""
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
# Every page-local script is inlined; a tag left as a src= would read "—" in the Artifact (2026-11-06: tf_strip.js).
TAGS = ('<script src="live_aid_indicators.js"></script>', '<script src="news_feed.js"></script>', '<script src="news_weight.js"></script>', '<script src="events_strip.js"></script>', '<script src="events_strip_data.js"></script>', '<script src="tf_strip.js"></script>', '<script src="ma_strip.js"></script>',
        '<script src="cycle_flag_data.js"></script>', '<script src="cycle_flag.js"></script>', '<script src="playbook_data.js"></script>', '<script src="playbook.js"></script>')
TAG = TAGS[0]
NOTE = ('<p class="tag" id="preview-note">Preview copy. The claude.ai viewer blocks exchange connections, so every feed '
        'here reads NOT_IN_DATA. Live page: open MyTradingSys/tools/live_aid/live_aid.html from disk in Chrome or Edge.</p>')
NO_DATA = "window.PLAYBOOK_DATA = null;\n"   # playbook_data.js is gitignored (CBP text): a fresh checkout has none until daily_playbook.py runs

PHONE_CSS = """
:root { --bg: #0d1013; --panel: #141920; --line: #232b35; --fg: #e3e8ee; --dim: #8592a1; --up: #3fbf8a; --down: #e2665c; --amber: #e0a43a; --accent: #6ea8d9; color-scheme: dark; }
* { box-sizing: border-box; }
body { margin: 0; background: var(--bg); color: var(--fg); font: 16px/1.4 system-ui, -apple-system, "Segoe UI", sans-serif; }
main { max-width: 480px; margin: 0 auto; padding: 12px 12px 40px; display: grid; gap: 12px; }
h1 { margin: 0; font-size: 18px; } h3 { margin: 0 0 6px; font-size: 16px; }
.tag, .dim { color: var(--dim); } .tag { font-size: 12px; margin: 0; }
.up { color: var(--up); } .down { color: var(--down); }
.pbg { display: grid; gap: 12px; }
.pbc { background: var(--panel); border: 1px solid var(--line); border-radius: 8px; padding: 10px 12px; display: grid; gap: 6px; }
.pbc.now { border-color: var(--amber); box-shadow: 0 0 0 1px var(--amber); }
.pbh { font: 12px ui-monospace, Consolas, monospace; color: var(--dim); }
.pbst { font: 700 11px system-ui, sans-serif; padding: 1px 6px; border-radius: 3px; border: 1px solid var(--dim); color: var(--dim); }
.pbst.NOW { background: var(--amber); border-color: var(--amber); color: var(--bg); }
.pbs, .pbn, .pba ul { margin: 0; padding-left: 18px; display: grid; gap: 8px; } .pbn { font-size: 13px; color: var(--dim); gap: 4px; }
.pbs li { font-size: 14px; } .pbr { font-size: 14px; } .pbl { font-size: 13px; line-height: 1.7; }
.pbmsg { margin: 0; padding: 8px 10px; border: 1px solid var(--amber); border-radius: 6px; } .pbmsg.stale { color: var(--amber); }
.pby table { width: 100%; border-collapse: collapse; font-size: 13px; margin-top: 6px; } .pby th, .pby td { text-align: left; padding: 3px 4px; border-top: 1px solid var(--line); }
@media (max-width: 400px) { body { font-size: 15px; } main { padding: 8px 8px 32px; } .pby table { font-size: 12px; } }
"""


def build() -> str:
    page = (HERE / "live_aid.html").read_text(encoding="utf-8")
    assert page.count("<main>") == 1
    for tag in TAGS:
        name = tag.split('"')[1]
        f = HERE / name
        js = f.read_text(encoding="utf-8") if f.exists() or name != "playbook_data.js" else NO_DATA
        assert page.count(tag) == 1, name
        page = page.replace(tag, "<script>\n" + js + "</script>")
    return page.replace("<main>", "<main>\n  " + NOTE, 1)


def build_playbook(data_js=None) -> str:
    """Phone-width page for the daily playbook: playbook.js and the data inlined, rendered on load and every minute.
    data_js = the text of playbook_data.js (None: NOT_IN_DATA)."""
    js = (HERE / "playbook.js").read_text(encoding="utf-8")
    data = (data_js or NO_DATA).replace("</", "<\\/")
    fallback = "" if data_js else '<p class="pbmsg">PLAYBOOK NOT_IN_DATA (run MyTradingSys/tools/live_aid/daily_playbook.py)</p>'
    return ('<!doctype html>\n<html lang="en"><head><meta charset="utf-8">\n'
            '<meta name="viewport" content="width=device-width, initial-scale=1">\n<title>BTC daily session playbook</title>\n'
            "<style>" + PHONE_CSS + "</style></head>\n<body><main>\n  <h1>BTC daily session playbook</h1>\n"
            '  <p class="tag">Asia 00-08Z, Europe 07-13Z, US 13-21Z. Numbers from daily_playbook.py (history first touches, OURS); every map is a scenario-ledger row. '
            'Context only: no orders, no size, nothing gates.</p>\n  <div id="pb">' + fallback + "</div>\n</main>\n"
            "<script>\n" + js + "</script>\n<script>\n" + data + "</script>\n"
            "<script>\n(function () { var el = document.getElementById('pb'); function draw() { if (window.PLAYBOOK) el.innerHTML = PLAYBOOK.html(window.PLAYBOOK_DATA, Date.now()); }"
            " draw(); setInterval(draw, 60000); })();\n</script>\n</body></html>\n")


if __name__ == "__main__":
    if sys.argv[1] == "--playbook":
        d = HERE / "playbook_data.js"
        Path(sys.argv[2]).write_text(build_playbook(d.read_text(encoding="utf-8") if d.exists() else None), encoding="utf-8", newline="\n")
    else:
        Path(sys.argv[1]).write_text(build(), encoding="utf-8", newline="\n")
