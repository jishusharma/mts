"""T01-F2: every loader that reads Dumps/backtest/raw_1d carries the mismatch label."""
import pathlib

ROOT = pathlib.Path(__file__).resolve().parents[2]
SEARCH = ROOT / "MyTradingSys"
AUDIT_SCRIPTS = "dsa_backtest_audit_2026-10-16"  # audit scripts measure the mismatch; they are not loaders
THIS_FILE = pathlib.Path(__file__).resolve()
LOADERS = [
    "research/candle_patterns_2026-10-04/pilot/cdata.py",
    "research/candle_patterns_2026-10-04/d19_4h_test.py",
    "research/volume_2026-10-09/vdata.py",
    "research/loose_code/oi_divergence_v2_2026-10-10.py",
    "research/loose_code/vpin_proxy_2026-10-10.py",
    "research/g3_marks_2026-10-16/g3_pack.py",
    "research/trendlines_2026-10-17/g3_pack/g3_pack.py",
    "research/setup_alpha_beta_2026-10-10/alpha_backtest.py",
    "backtest/layers/timeframe/tf_realdata_gate.py",
]


def _read(p):
    return p.read_text(encoding="utf-8", errors="replace")


def test_named_loaders_carry_label():
    missing = [f for f in LOADERS if "T01-F2" not in _read(SEARCH / f)]
    assert not missing, f"no T01-F2 label: {missing}"


def test_every_raw_1d_reader_carries_label():
    bad = []
    for p in SEARCH.rglob("*.py"):
        if p.resolve() == THIS_FILE or AUDIT_SCRIPTS in p.parts or "_archive" in p.parts:
            continue
        t = _read(p)
        if "raw_1d" in t and "T01-F2" not in t:
            bad.append(str(p.relative_to(SEARCH)))
    assert not bad, f"raw_1d readers without T01-F2 label: {bad}"
