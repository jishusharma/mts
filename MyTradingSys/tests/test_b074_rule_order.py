"""B074 (Compute-Verdict rule order) and B069 (state-update wrapper log vs exit code).
Both run the real code text from scripts/core/start-trading-day.ps1 under pwsh.
Expected values come from the item docs, not from code: B074 - the broken-value override wins regardless of
proofDir, one snapshot gives one verdict and one reason; B069 - the wrapper log line carries the exit code, and
a failing run surfaces the stderr tail instead of discarding it."""
import re
import shutil
import subprocess
import tempfile
from pathlib import Path

import pytest

PS1 = Path(__file__).resolve().parents[2] / "scripts" / "core" / "start-trading-day.ps1"
PWSH = shutil.which("pwsh") or shutil.which("powershell")
pytestmark = pytest.mark.skipif(PWSH is None, reason="pwsh not available")

SNAP = """@{
  current_price = 100.0; timestamp_utc = '2026-10-04T00:00:00Z'
  conditions = @{ vp_shape = 'D'; price_vs_va = 'below_val'; cvd_slope = 'falling' }
  setup_candidates = @(@{ direction = 'long'; setup_type = 'T'; math = @{ net_rr = 2.0; tier = 'actionable' }
                          score = @{ proof_count = 5 }; zone = @{ name = 'z'; price = 99.0 } })
}"""


def _run_ps(script):
    r = subprocess.run([PWSH, "-NoProfile", "-Command", script], capture_output=True, text=True, timeout=60)
    assert r.returncode == 0, r.stderr
    return r.stdout.strip().splitlines()


def _verdict_fn():
    src = PS1.read_text(encoding="utf-8")
    m = re.search(r"^function Compute-Verdict \{.*?^\}\n", src, re.S | re.M)
    assert m, "Compute-Verdict not found"
    return m.group(0)


def test_b074_override_wins_for_every_proof_dir():
    script = (
        "function Get-NetRrFloor { return 1.0 }\n" + _verdict_fn() + "\n$snap = " + SNAP + "\n"
        "foreach ($pd in 'aligned','contradiction','error') {\n"
        "  $v = Compute-Verdict -snap $snap -proofDir $pd\n"
        "  Write-Output ($pd + '|' + $v.verdict + '|' + $v.reason)\n}"
    )
    out = _run_ps(script)
    want = "WAIT_RR|broken below_val + CVD falling vs LONG"
    assert out == [f"{pd}|{want}" for pd in ("aligned", "contradiction", "error")], out


def test_b069_wrapper_log_agrees_with_exit_code():
    src = PS1.read_text(encoding="utf-8")
    a = src.index("$umsCmd = ")
    b = src.index("$s = Get-ChildItem", a)
    block = src[a:b]
    tmp = Path(tempfile.mkdtemp())
    (tmp / "runtime_data").mkdir()
    (tmp / "runtime_data" / "ums.log").write_text("Traceback\nValueError: boom\n", encoding="utf-8")
    outs = {}
    for rc in (0, 1):
        script = (
            f"$R = '{tmp}'\nfunction Log-Line($m) {{ Write-Output $m }}\n"
            f"function Invoke-WithTimeout {{ param($File,$ArgList,$TimeoutSec,$Tag,$WorkDir) return {rc} }}\n" + block
        )
        outs[rc] = " ".join(_run_ps(script))
    assert "exit=0" in outs[0] and "WARN" not in outs[0], outs[0]
    assert "STATE_UPDATE_WARN exit=1" in outs[1] and "ValueError: boom" in outs[1], outs[1]
