"""Targeted unit tests for scripts/dev/indicator_audit_sample.py (no network).

Covers pure helpers (window_sha256, _section, _scrub, definition_text), seeded
sampling via draw(), monkeypatched fetch_pool(), and the draw CLI entrypoint.

Scratch-copy mutation check:
- Copied scripts/dev/indicator_audit_sample.py to scratch dir and mutated line 92
  from `closes = row["closes"][end - WINDOW + 1:end + 1]` to
  `closes = row["closes"][end - WINDOW:end]`.
- Re-running pytest against the broken scratch copy failed:
  `test_draw_seeded_determinism_and_exact_window_slice` (and `test_main_draw_cli_writes_packets_and_manifest`).
"""
import hashlib
import io
import json
import pathlib
import sys

import pytest

_REPO_ROOT = next(
    p
    for p in pathlib.Path(__file__).resolve().parents
    if (p / "scripts" / "dev" / "indicator_audit_sample.py").is_file()
)
if str(_REPO_ROOT) not in sys.path:
    sys.path.append(str(_REPO_ROOT))
_SCRIPTS_DEV = str(_REPO_ROOT / "scripts" / "dev")
if _SCRIPTS_DEV not in sys.path:
    sys.path.append(_SCRIPTS_DEV)

import indicator_audit_sample as smp  # noqa: E402


def _seeded_pool(n_bars=500):
    """Build a deterministic 6-series pool (2 symbols x 3 timeframes) with n_bars each."""
    pool = {}
    for sym_idx, sym in enumerate(smp.SYMBOLS):
        for tf_idx, tf in enumerate(smp.TFS):
            base = (sym_idx + 1) * 1000.0 + tf_idx * 100.0
            open_times = [1_700_000_000_000 + i * 60_000 for i in range(n_bars)]
            closes = [base + float(i) for i in range(n_bars)]
            pool[f"{sym}|{tf}"] = {
                "symbol": sym,
                "tf": tf,
                "open_times": open_times,
                "closes": closes,
            }
    return pool


def test_window_sha256_hand_computed():
    # Hand-computed: json.dumps([100.5, 101.25, 99.0], separators=(",", ":")) == "[100.5,101.25,99.0]"
    expected = "53f578964e0015d53db1f53356a43dfa386c87c77f886959b0c6c9b04a0b83df"
    assert expected == hashlib.sha256(b"[100.5,101.25,99.0]").hexdigest()
    assert smp.window_sha256([100.5, 101.25, 99.0]) == expected
    assert smp.window_sha256([100.5, 101.25, 99.1]) != expected


def test_section_and_scrub_pure_helpers():
    doc = (
        "## 1. RSI\n"
        "Line A; CoinGlass shows the same pair, verified chart by chart with `chart_verify.py --seen`.\n"
        "## 2. Other\n"
        "Ignored\n"
        "## Verification note\n"
        "Tail\n"
    )
    sec1 = smp._section(doc, 1)
    assert sec1.startswith("Line A;")
    assert "Ignored" not in sec1

    with pytest.raises(SystemExit):
        smp._section(doc, 99)

    assert smp._scrub(sec1) == "Line A."
    checked = "Checked 2026-10-17 against `foo_bar.py` lines 10-20: it divides by n (population), so the two agree. Keep."
    assert smp._scrub(checked) == "Keep."

    with pytest.raises(SystemExit):
        smp._scrub("still mentions other_file.py")

    with pytest.raises(ValueError):
        smp.definition_text("UNKNOWN")


def test_draw_seeded_determinism_and_exact_window_slice():
    pool_500 = _seeded_pool(n_bars=500)
    pk_a = smp.draw(pool_500, seed=42)
    pk_b = smp.draw(pool_500, seed=42)
    assert pk_a == pk_b
    assert len(pk_a) == len(smp.INDICATORS) * smp.PER_INDICATOR  # 3 * 7 = 21

    # With n_bars == WINDOW (500), randrange(499, 500) is always 499: full 0..499 slice.
    expected_open_time = 1_700_000_000_000 + 499 * 60_000
    for ind in smp.INDICATORS:
        ind_packets = [p for p in pk_a if p["indicator"] == ind]
        assert len(ind_packets) == 7
        assert len({(p["symbol"], p["tf"]) for p in ind_packets}) == 6

    for p in pk_a:
        series = pool_500[f"{p['symbol']}|{p['tf']}"]
        assert p["n_closes"] == 500
        assert p["closes"] == series["closes"]
        assert p["last_close_open_time_ms"] == expected_open_time
        assert p["sha256"] == smp.window_sha256(p["closes"])
        assert p["answer_keys"] == smp.ANSWER_KEYS[p["indicator"]]

    # With n_bars == 505, different seeds produce different draws while preserving 500-bar windows.
    pool_505 = _seeded_pool(n_bars=505)
    pk_s1 = smp.draw(pool_505, seed=1)
    pk_s2 = smp.draw(pool_505, seed=2)
    assert [(p["id"], p["last_close_open_time_ms"]) for p in pk_s1] != [
        (p["id"], p["last_close_open_time_ms"]) for p in pk_s2
    ]
    for p in pk_s1:
        series = pool_505[f"{p['symbol']}|{p['tf']}"]
        end_idx = series["open_times"].index(p["last_close_open_time_ms"])
        assert p["n_closes"] == 500
        assert p["closes"] == series["closes"][end_idx - 499 : end_idx + 1]


def test_fetch_pool_drops_forming_bar_no_network(monkeypatch, tmp_path):
    seen_urls = []

    def fake_urlopen(url, timeout=30):
        seen_urls.append((url, timeout))
        # 4 kline rows: [open_time, o, h, l, close, ...]; last row is the still-forming bar.
        rows = [
            [1000, "10", "11", "9", "10.5"],
            [2000, "10.5", "12", "10", "11.25"],
            [3000, "11.25", "13", "11", "12.5"],
            [4000, "12.5", "14", "12", "999.9"],
        ]
        return io.BytesIO(json.dumps(rows).encode("utf-8"))

    monkeypatch.setattr(smp, "_doh_urlopen", fake_urlopen)
    out_file = tmp_path / "pool.json"
    pool = smp.fetch_pool(out_file)

    assert len(seen_urls) == len(smp.SYMBOLS) * len(smp.TFS)
    assert all(timeout == 30 for _, timeout in seen_urls)
    assert set(pool.keys()) == {f"{s}|{t}" for s in smp.SYMBOLS for t in smp.TFS}
    for key, row in pool.items():
        assert row["open_times"] == [1000, 2000, 3000], key
        assert row["closes"] == [10.5, 11.25, 12.5], key

    persisted = json.loads(out_file.read_text(encoding="utf-8"))
    assert persisted == pool


def test_main_draw_cli_writes_packets_and_manifest(tmp_path):
    pool_file = tmp_path / "pool.json"
    out_dir = tmp_path / "packets"
    pool_file.write_text(json.dumps(_seeded_pool(n_bars=500)), encoding="utf-8")

    rc = smp.main(["draw", "--pool", str(pool_file), "--seed", "7", "--out", str(out_dir)])
    assert rc == 0

    manifest = json.loads((out_dir / "manifest.json").read_text(encoding="utf-8"))
    assert manifest["seed"] == 7
    assert len(manifest["packets"]) == 21
    for entry in manifest["packets"]:
        pkt = json.loads((out_dir / f"{entry['id']}.json").read_text(encoding="utf-8"))
        assert pkt["sha256"] == entry["sha256"]
        assert pkt["last_close_open_time_ms"] == entry["last_close_open_time_ms"]
        assert pkt["n_closes"] == 500
