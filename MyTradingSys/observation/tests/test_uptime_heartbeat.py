import json
import subprocess
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import uptime_heartbeat as uh  # noqa: E402

D0 = datetime(2026, 11, 1, tzinfo=timezone.utc)
NOW = D0 + timedelta(days=1)  # end of 2026-11-01


def _line(t, host="JIS-NB"):
    return json.dumps({"utc": t.strftime("%Y-%m-%dT%H:%M:%SZ"), "host": host})


def _fill(path, start, minutes, host="JIS-NB", skip=()):
    with open(path, "a", newline="\n") as f:
        for m in range(minutes):
            if m in skip:
                continue
            f.write(_line(start + timedelta(minutes=m), host) + "\n")


def test_a_full_day_100_and_3h_gap_87_5(tmp_path):
    p = tmp_path / "b.jsonl"
    _fill(p, D0, 1440)
    r = uh.read_uptime(p, "JIS-NB", days=1, now=NOW)
    assert r["status"] == "OK" and r["days"]["2026-11-01"] == 100.0
    q = tmp_path / "c.jsonl"
    _fill(q, D0, 1440, skip=range(360, 540))
    r = uh.read_uptime(q, "JIS-NB", days=1, now=NOW)
    assert r["days"]["2026-11-01"] == 87.5


def test_b_restart_double_minute_counts_once_gap_counts_down(tmp_path):
    p = tmp_path / "b.jsonl"
    _fill(p, D0, 720)
    _fill(p, D0 + timedelta(minutes=700), 20)  # overlap rewrites minutes 700-719
    r = uh.read_uptime(p, "JIS-NB", days=1, now=NOW)
    assert r["days"]["2026-11-01"] == 50.0


def test_c_missing_garbage_torn(tmp_path):
    r = uh.read_uptime(tmp_path / "none.jsonl", "JIS-NB", days=1, now=NOW)
    assert r["status"] == "NOT_IN_DATA" and r["pct"] is None
    g = tmp_path / "g.jsonl"
    g.write_text("garbage\n\x00\x00\n", newline="\n")
    assert uh.read_uptime(g, "JIS-NB", days=1, now=NOW)["status"] == "NOT_IN_DATA"
    t = tmp_path / "t.jsonl"
    _fill(t, D0, 1440)
    with open(t, "a", newline="\n") as f:
        f.write('{"utc": "2026-11-01T23:5')  # torn tail
    r = uh.read_uptime(t, "JIS-NB", days=1, now=NOW)
    assert r["days"]["2026-11-01"] == 100.0


def test_d_wrong_host_and_future_no_credit(tmp_path):
    p = tmp_path / "w.jsonl"
    _fill(p, D0, 1440, host="OTHER")
    assert uh.read_uptime(p, "JIS-NB", days=1, now=NOW)["status"] == "NOT_IN_DATA"
    f = tmp_path / "f.jsonl"
    now = D0 + timedelta(hours=1)
    _fill(f, D0, 60)
    _fill(f, now + timedelta(minutes=3), 600)  # more than 2 min ahead
    r = uh.read_uptime(f, "JIS-NB", days=1, now=now)
    assert r["days"]["2026-11-01"] == 100.0  # only the 60 real minutes, none of the future


def test_e_no_network_or_exchange_import():
    src = Path(uh.__file__).read_text()
    for bad in ("requests", "socket", "urllib", "http", "websocket", "binance", "deribit", "ccxt"):
        assert f"import {bad}" not in src and f"from {bad}" not in src


def test_f_no_account_input():
    import inspect
    for fn in (uh.write_beat, uh.read_uptime):
        names = " ".join(inspect.signature(fn).parameters)
        assert "account" not in names and "balance" not in names and "key" not in names


def test_write_beat_roundtrip_and_cli(tmp_path):
    p = tmp_path / "b.jsonl"
    uh.write_beat(p, "JIS-NB", now=D0)
    row = json.loads(p.read_text().strip())
    assert row == {"utc": "2026-11-01T00:00:00Z", "host": "JIS-NB"}
    q = tmp_path / "c.jsonl"
    for d in range(14):
        _fill(q, D0 + timedelta(days=d - 13), 1440)
    out = subprocess.run([sys.executable, str(Path(uh.__file__)), "report", "--host", "JIS-NB", "--days", "14",
                          "--file", str(q), "--now", "2026-11-02T00:00:00Z"], capture_output=True, text=True)
    assert out.returncode == 0 and "PASS" in out.stdout and "100.0" in out.stdout
    out = subprocess.run([sys.executable, str(Path(uh.__file__)), "report", "--host", "JIS-NB", "--days", "14",
                          "--file", str(tmp_path / "no.jsonl")], capture_output=True, text=True)
    assert "NOT_IN_DATA" in out.stdout and "PASS" not in out.stdout
