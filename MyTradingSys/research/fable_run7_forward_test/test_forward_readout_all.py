"""Tests for forward_readout_all.py and the c30 slot / T06 side split. Fixtures in tmp_path only."""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import forward_readout_all as fa  # noqa: E402

MS = 1_796_083_200_000
DAY = 86_400_000
C30 = "layer:wt:c30_h2_long"
T06 = "layer:rsi:rsi_ma_cross:4h"


def jl(tmp_path, name, rows):
    p = tmp_path / name
    p.write_text("\n".join(json.dumps(r) for r in rows) + "\n", encoding="utf-8")
    return p


def out(tmp_path, **kw):
    none = tmp_path / "missing.jsonl"
    a = dict(ledger=none, malkan=none, t06=none, c30=none, asof="2027-01-20")
    a.update(kw)
    return fa.combined(**a)


def test_missing_files_four_rows_no_crash(tmp_path):
    c = out(tmp_path)
    txt = fa.render(c)
    assert [r["name"] for r in c["rows"]] == ["Krown S8", "Malkan", "T06L", "C30"]
    assert txt.count("n 0, no data yet") == 4


def test_c30_outcome_rows_scored_by_t_and_source(tmp_path):
    rows = [{"kind": "outcome", "t": MS + i * DAY, "side": "long", "net_r": r, "source": C30}
            for i, r in enumerate([1.0, -0.5])]
    rows += [{"kind": "signal", "t": MS, "source": C30}, {"kind": "no_fill", "t": MS, "source": C30}]
    c = out(tmp_path, c30=jl(tmp_path, "c.jsonl", rows))
    r = c["rows"][3]
    assert r["n"] == 2 and abs(r["mean_r"] - 0.25) < 1e-9 and r["state"] == "RUNNING"


def test_t06_long_scored_short_separate(tmp_path):
    rows = [{"kind": "outcome", "t_fill": MS, "status": "closed", "net_r": 1.0, "side": "long", "source": T06},
            {"kind": "outcome", "t_fill": MS + DAY, "status": "closed", "net_r": -2.0, "side": "short", "source": T06}]
    c = out(tmp_path, t06=jl(tmp_path, "t.jsonl", rows))
    assert c["rows"][2]["n"] == 1 and c["rows"][2]["mean_r"] == 1.0
    assert c["res"]["t06_short"]["n"] == 1
    assert "T06 short (reported, not a lead): n 1, mean R -2.000" in fa.render(c)


def test_kill_state_at_30_trades_nonpositive(tmp_path):
    rows = [{"kind": "outcome", "t": MS + i * DAY, "side": "long", "net_r": 0.0, "source": C30} for i in range(30)]
    c = out(tmp_path, c30=jl(tmp_path, "c.jsonl", rows))
    assert c["rows"][3]["state"] == "KILL"


def test_journal_kill_row_displayed(tmp_path):
    rows = [{"kind": "outcome", "t": MS, "side": "long", "net_r": 0.5, "source": C30},
            {"kind": "kill", "source": C30, "verdict": "KILL"}]
    c = out(tmp_path, c30=jl(tmp_path, "c.jsonl", rows))
    txt = fa.render(c)
    assert c["rows"][3]["state"] == "KILL (journal row)" and "Kill row:" in txt


def test_cli_missing_paths_never_crash(capsys, tmp_path):
    assert fa.main(["--ledger", str(tmp_path / "a"), "--malkan", str(tmp_path / "b"),
                    "--t06", str(tmp_path / "c"), "--c30", str(tmp_path / "d")]) == 0
    assert sum(1 for l in capsys.readouterr().out.splitlines() if l.startswith("| ")) == 5  # header + four slots
