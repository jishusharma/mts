"""cbp.query + scripts/dev/cbp_run.py: window logic, 5-day filter, dedupe, fabricated quote, empty store."""
import json
import subprocess
import sys
import copy
import pytest
from datetime import datetime, timedelta, timezone
from pathlib import Path

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "MyTradingSys"))
sys.path.insert(0, str(ROOT / "scripts" / "dev"))

import cbp  # noqa: E402
import cbp_run  # noqa: E402

NOW = datetime(2026, 10, 24, 10, 0, tzinfo=timezone.utc)
BODY = "[00:00:01] so bitcoin needs to hold 80K\n[00:00:09] and then we target 87K with stop under 79K\n"


def at(h, m=0):
    return datetime(2026, 10, 24, h, m, tzinfo=timezone.utc)


def row(vid, pub, analyst="Krown", sym="BTC", trades=()):
    return {"analyst": analyst, "video_id": vid, "published": pub, "bias": "BULLISH", "quotes": [], "trades": list(trades),
            "pointers": [], "symbols": [sym], "quote_verified": True, "expires_at": (datetime.fromisoformat(pub) + timedelta(days=5)).strftime("%Y-%m-%dT00:00:00Z")}


def test_query_empty_store(tmp_path):
    assert cbp.query(store=tmp_path / "none.json", now=NOW) == []
    (tmp_path / "bad.json").write_text("{not json", encoding="utf-8")
    assert cbp.query(store=tmp_path / "bad.json", now=NOW) == []


def test_query_five_day_filter_and_filters(tmp_path):
    st = tmp_path / "s.json"
    cbp.save({"rows": [row("a" * 11, "2026-10-23"), row("b" * 11, "2026-10-19"), row("c" * 11, "2026-10-18"),
                       row("d" * 11, "2026-10-22", analyst="Rekt", sym="ETH")]}, st)
    ids = [r["video_id"][0] for r in cbp.query(store=st, now=NOW)]
    assert ids == ["a", "d"]  # 10-19 expires 10-24T00:00Z (published+5d) so it is out at NOW; 10-18 out; newest first
    assert [r["video_id"][0] for r in cbp.query(analyst="krown", store=st, now=NOW)] == ["a"]
    assert [r["video_id"][0] for r in cbp.query(symbol="eth", store=st, now=NOW)] == ["d"]
    assert len(cbp.query(since_days=2, store=st, now=NOW)) == 2


def test_window_logic_injected_clock():
    assert cbp_run.open_window(at(9)) == "EU" and cbp_run.open_window(at(10, 59)) == "EU"
    assert cbp_run.open_window(at(11)) == "EU" and cbp_run.open_window(at(8, 59)) is None
    assert cbp_run.open_window(at(12, 59)) == "EU" and cbp_run.open_window(at(13)) == "PRE_US"
    assert cbp_run.open_window(at(23, 59)) == "PRE_US"
    assert cbp_run.is_due(at(10), {}) == "EU"
    assert cbp_run.is_due(at(10), {"done": ["2026-10-24:EU"]}) is None  # done in this window today
    assert cbp_run.is_due(at(13), {"done": ["2026-10-24:EU"]}) == "PRE_US"
    assert cbp_run.is_due(at(10), {"done": ["2026-10-23:EU"]}) == "EU"  # yesterday's run does not count
    assert cbp_run.is_due(at(8), {}) is None


def test_main_due_and_force(tmp_path, monkeypatch):
    monkeypatch.setenv("CBP_STAMP", str(tmp_path / "stamp.json"))
    monkeypatch.setenv("CBP_STORE", str(tmp_path / "s.json"))
    calls = []
    monkeypatch.setattr(cbp_run, "run_once", lambda now: calls.append(now) or (0, 0, 0))
    assert cbp_run.main(["--due"], now=at(8)) == 0 and calls == []  # no window open
    cbp_run.main(["--due"], now=at(10))
    cbp_run.main(["--due"], now=at(10, 30))  # same window, already done
    assert len(calls) == 1
    cbp_run.main(["--force"], now=at(15))  # operator ask runs anywhere
    assert len(calls) == 2


def _setup(tmp_path, monkeypatch, pub="2026-10-23", vid="V" * 11):
    tr = tmp_path / "tr"
    tr.mkdir()
    (tr / (vid + "_timed.txt")).write_text(
        "# Video ID: %s\n# Title: T\n# Published: %s\n# Analyst: Krown\n# ---\n%s" % (vid, pub, BODY), encoding="utf-8")
    monkeypatch.setattr(cbp_run, "TRANSCRIPTS", tr)
    return tmp_path / "s.json"


GOOD = {"bias": "BULLISH", "symbols": ["btc"], "quotes": ["bitcoin needs to hold 80K"],
        "trades": [{"asset": "BTC", "direction": "LONG", "entry": "80K hold", "target": "87K",
                    "invalidation": "79K", "quote": "we target 87K with stop under 79K"}], "pointers": ["80K"]}


def test_run_adds_dedupes_and_skips_known(tmp_path, monkeypatch):
    st = _setup(tmp_path, monkeypatch)
    n = []
    ext = lambda v, b: n.append(v) or GOOD  # noqa: E731
    assert cbp_run.run_once(NOW, fetch=lambda *a: None, extract=ext, store=st) == (1, 1, 0)
    assert cbp_run.run_once(NOW, fetch=lambda *a: None, extract=ext, store=st) == (0, 1, 0)
    assert len(n) == 1  # known video: no second LLM pass
    r = cbp.query(store=st, now=NOW)[0]
    assert r["quote_verified"] and r["symbols"] == ["BTC"] and cbp.is_tradable(r)
    assert cbp.validate_row(r) == []


def test_fabricated_quote_rejected(tmp_path, monkeypatch):
    # A dummy model output with invented evidence must never reach the query store.
    st = _setup(tmp_path, monkeypatch)
    fake = dict(GOOD, quotes=["bitcoin will moon to 500K tomorrow"])
    assert cbp_run.run_once(NOW, fetch=lambda *a: None, extract=lambda v, b: fake, store=st) == (0, 0, 1)
    assert cbp.query(store=st, now=NOW) == []
    d = cbp.load(st)
    assert d["rejected"][0][0] == "V" * 11 and "quote not in transcript" in d["rejected"][0][2]
    fake_trade = dict(GOOD, trades=[dict(GOOD["trades"][0], quote="short it at 12K")])
    assert cbp_run.build_row(("V" * 11, "Krown", "2026-10-23", "T", None), fake_trade, BODY)[0] is None


def test_old_videos_never_extracted(tmp_path, monkeypatch):
    st = _setup(tmp_path, monkeypatch, pub="2026-10-18")
    called = []
    out = cbp_run.run_once(NOW, fetch=lambda *a: None, extract=lambda v, b: called.append(1) or GOOD, store=st)
    assert out == (0, 0, 0) and called == []


def test_fetch_failure_propagates(monkeypatch):
    monkeypatch.setattr(cbp_run, "analysts", lambda: ({"exclude_regex": ""},
                       [{"short": "Krown", "channel": "@x"}]))
    import pytest
    with pytest.raises(subprocess.CalledProcessError):
        cbp_run.fetch_new("2026-10-19", set(), run=lambda cmd, **kw: subprocess.CompletedProcess(cmd, 1))


def test_unavailable_extractor_does_not_stamp_success(tmp_path, monkeypatch):
    st = _setup(tmp_path, monkeypatch)
    monkeypatch.setenv("CBP_STAMP", str(tmp_path / "stamp.json"))
    monkeypatch.setenv("CBP_STORE", str(st))
    def unavailable(*args):
        raise OSError("extractor unavailable")
    original = cbp_run.run_once
    monkeypatch.setattr(cbp_run, "run_once", lambda now: original(
        now, fetch=lambda *a: None, extract=unavailable, store=st))
    assert cbp_run.main(["--due"], now=at(10)) != 0
    assert cbp_run.is_due(at(10), cbp_run.read_stamp()) == "EU"


def test_raw_canonical_transcript_is_read(tmp_path, monkeypatch):
    tr = tmp_path / "raw_transcripts_canonical"
    tr.mkdir()
    monkeypatch.setattr(cbp_run, "TRANSCRIPTS", tr)
    vid = "W" * 11
    (tr / (vid + "_raw.txt")).write_text(
        "# Video ID: %s\n# Published: 2026-10-23\n# Analyst: Krown\n# ---\n%s" % (vid, BODY), encoding="utf-8")
    st = tmp_path / "store.json"
    assert cbp_run.run_once(NOW, fetch=lambda *a: None, extract=lambda *a: GOOD, store=st) == (1, 1, 0)
    assert cbp.query(store=st, now=NOW)[0]["video_id"] == vid


def test_cbp_run_works_without_fixed_machine_paths(tmp_path, monkeypatch):
    """bug-youtube-gemini-only-rule-is-a-preference: CBP must not assume one machine. With CBP_HOME unset
    and no legacy F:/CryptoScrapper, the default falls back under this checkout, never a dead drive path."""
    monkeypatch.delenv("CBP_HOME", raising=False)
    home = cbp_run.default_cbp_home(exists=lambda p: False)
    assert home == cbp_run.ROOT / "runtime_data" / "cbp"
    assert not str(home).startswith("F:")
    legacy_present = cbp_run.default_cbp_home(exists=lambda p: True)
    assert legacy_present == Path("F:/CryptoScrapper")  # still honored when actually present
    monkeypatch.setenv("CBP_HOME", str(tmp_path / "other_machine_home"))
    assert cbp_run.default_cbp_home() == tmp_path / "other_machine_home"  # explicit override always wins

    # End-to-end on a per-machine CBP_HOME (no F:/CryptoScrapper read anywhere): fetch, extract, store.
    home2 = tmp_path / "cbp_home"
    tr = home2 / "raw_transcripts_canonical"
    tr.mkdir(parents=True)
    vid = "Z" * 11
    (tr / (vid + "_timed.txt")).write_text(
        "# Video ID: %s\n# Title: T\n# Published: 2026-10-23\n# Analyst: Krown\n# ---\n%s" % (vid, BODY),
        encoding="utf-8")
    monkeypatch.setattr(cbp_run, "CBP_HOME", home2)
    monkeypatch.setattr(cbp_run, "TRANSCRIPTS", tr)
    st = tmp_path / "s2.json"
    ext = lambda v, b: GOOD  # noqa: E731
    assert cbp_run.run_once(NOW, fetch=lambda *a: None, extract=ext, store=st) == (1, 1, 0)


def test_extractor_nonzero_json_is_failure():
    import pytest
    video = ("V" * 11, "Krown", "2026-10-23", "T", None)
    with pytest.raises(subprocess.CalledProcessError):
        cbp_run.llm_extract(video, BODY, run=lambda *a, **kw: subprocess.CompletedProcess(
            a, 1, stdout=json.dumps(GOOD), stderr="failed"))


# Planted-row audit: synthetic data only, never the CBP store or external transcripts.
def test_planted_trade_without_quote_is_rejected():
    got = copy.deepcopy(GOOD)
    got["trades"][0]["quote"] = ""
    built, reason = cbp_run.build_row(("P" * 11, "Krown", "2026-10-23", "fixture", None), got, BODY)
    assert built is None and "empty quote" in reason


def test_planted_wrong_direction_is_rejected():
    got = copy.deepcopy(GOOD)
    got["trades"][0]["direction"] = "SIDEWAYS"  # schema allows only LONG or SHORT
    built, _ = cbp_run.build_row(("P" * 11, "Krown", "2026-10-23", "fixture", None), got, BODY)
    assert built is None


def test_planted_expired_row_is_not_returned(tmp_path):
    built, _ = cbp_run.build_row(("P" * 11, "Krown", "2026-10-23", "fixture", None), GOOD, BODY)
    built["expires_at"] = "2026-10-24T09:00:00Z"  # publication recent; explicit expiry already passed
    st = tmp_path / "synthetic.json"
    cbp.save({"rows": [built]}, st)
    assert cbp.query(store=st, now=NOW) == []


def test_planted_duplicate_video_id_is_not_extracted_again(tmp_path, monkeypatch):
    st = _setup(tmp_path, monkeypatch, vid="P" * 11)
    built, _ = cbp_run.build_row(("P" * 11, "Krown", "2026-10-23", "fixture", None), GOOD, BODY)
    cbp.save({"rows": [built]}, st)

    def must_not_extract(*args):
        pytest.fail("duplicate video must be stopped before extraction")

    assert cbp_run.run_once(NOW, fetch=lambda *a: None, extract=must_not_extract, store=st) == (0, 1, 0)
    assert len(cbp.load(st)["rows"]) == 1


def test_planted_missing_expiry_is_not_returned(tmp_path):
    built, _ = cbp_run.build_row(("P" * 11, "Krown", "2026-10-23", "fixture", None), GOOD, BODY)
    del built["expires_at"]
    assert "missing expires_at" in cbp.validate_row(built)  # gate 1 knows it is invalid
    st = tmp_path / "synthetic.json"
    cbp.save({"rows": [built]}, st)
    assert cbp.query(store=st, now=NOW) == []  # read path must not trust a malformed stored row


def _stored(tmp_path, expires):
    built, _ = cbp_run.build_row(("P" * 11, "Krown", "2026-10-23", "fixture", None), GOOD, BODY)
    built["expires_at"] = expires
    st = tmp_path / "synthetic.json"
    cbp.save({"rows": [built]}, st)
    return st


def test_valid_row_is_returned(tmp_path):
    assert len(cbp.query(store=_stored(tmp_path, "2026-10-28T00:00:00Z"), now=NOW)) == 1


def test_expiry_boundary_is_expired(tmp_path):
    st = _stored(tmp_path, "2026-10-24T10:00:00Z")
    assert cbp.query(store=st, now=NOW) == []
    assert len(cbp.query(store=st, now=datetime(2026, 10, 24, 9, 59, 59, tzinfo=timezone.utc))) == 1


@pytest.mark.parametrize("bad", ["tomorrow", "", None, 5, "2026-10-28", "2026-10-28T00:00:00+00:00"])
def test_malformed_expiry_is_not_returned(tmp_path, bad):
    assert cbp.query(store=_stored(tmp_path, bad), now=NOW) == []
