"""Live-aid cycle-bottom flag line (card cycle-bottom-rule-window-gap-and-live-line). Expected strings are written by hand."""
import json
import os
import shutil
import subprocess
import sys
from datetime import date, datetime, timezone
from pathlib import Path

import pytest

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import build_cycle_flag  # noqa: E402
import build_artifact  # noqa: E402

JS = HERE / "cycle_flag.js"
DATA = {"line": "CYCLE4 d397 [363-406] WAIT", "built_utc": "2026-11-07T00:00:00Z"}
T0 = 1_794_009_600_000  # 2026-11-07T00:00:00Z


def _text(data, now):
    node = shutil.which("node")
    if not node:
        pytest.skip("node not installed")
    runner = "const P=require(process.argv[1]);let j='';process.stdin.on('data',d=>j+=d).on('end',()=>{j=JSON.parse(j);console.log(JSON.stringify(P.text(j.d,j.n)))})"
    out = subprocess.run([node, "-e", runner, str(JS)], input=json.dumps({"d": data, "n": now}), capture_output=True,
                         text=True, encoding="utf-8", timeout=30, env=os.environ.copy())
    assert out.returncode == 0, out.stderr
    return json.loads(out.stdout)


def test_fresh_line_shown_as_is():
    assert _text(DATA, T0 + 3_600_000) == DATA["line"]


def test_stale_after_36h_still_shows_line_with_warning():
    t = _text(DATA, T0 + 37 * 3_600_000)
    assert t.startswith("CYCLE FLAG STALE") and t.endswith(DATA["line"])


def test_missing_or_bad_data_fails_closed():
    assert _text(None, T0).startswith("CYCLE FLAG: NOT_IN_DATA")
    assert _text({"line": "", "built_utc": "x"}, T0).startswith("CYCLE FLAG: NOT_IN_DATA")
    assert _text({"line": "x", "built_utc": "garbage"}, T0).startswith("CYCLE FLAG: NOT_IN_DATA")


def test_generator_writes_the_python_flag_line():
    now = datetime(2026, 11, 7, 1, 0, tzinfo=timezone.utc)
    s = build_cycle_flag.render(date(2026, 11, 7), now)
    assert s.startswith("// generated") and 'window.CYCLE_FLAG_DATA = ' in s
    data = json.loads(s.split("window.CYCLE_FLAG_DATA = ", 1)[1].rstrip().rstrip(";"))
    assert data["built_utc"] == "2026-11-07T01:00:00Z"
    assert data["line"].startswith("CYCLE4 d397 [363-406]") and "WAIT" in data["line"]


def test_page_has_the_flag_line_and_artifact_inlines_it():
    page = (HERE / "live_aid.html").read_text(encoding="utf-8")
    assert 'id="cycle-flag"' in page and "CYCLEFLAG.text(" in page
    assert page.count('<script src="cycle_flag.js"></script>') == 1 and page.count('<script src="cycle_flag_data.js"></script>') == 1
    art = build_artifact.build()
    assert 'src="cycle_flag' not in art and "root.CYCLEFLAG = api" in art and "CYCLE_FLAG_DATA" in art
