"""Binance DoH resolver (ISP DNS block fix). Pure unit tests: DoH transport and system DNS are injected, no network."""
from __future__ import annotations

import ssl
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from MyTradingSys.runtime import binance_doh as bd  # noqa: E402

GOOD = "54.192.142.53"
BLOCK = "49.44.79.236"


@pytest.fixture(autouse=True)
def _clean():
    bd.clear_cache()
    yield
    bd.clear_cache()


def _doh(answers):
    """answers: {provider_name: list[(ip, ttl)] | Exception}"""
    calls = []

    def fetch(provider, host):
        calls.append(provider)
        r = answers[provider]
        if isinstance(r, Exception):
            raise r
        return r
    fetch.calls = calls
    return fetch


def test_is_binance_host():
    assert bd.is_binance_host("fapi.binance.com")
    assert bd.is_binance_host("fstream.binance.com")
    assert bd.is_binance_host("data.binance.vision")
    assert not bd.is_binance_host("api.deribit.com")
    assert not bd.is_binance_host("evilbinance.com")


def test_cloudflare_answer_used():
    f = _doh({"cloudflare": [(GOOD, 60)], "google": [("1.2.3.4", 60)]})
    assert bd.resolve("fapi.binance.com", fetch=f) == [GOOD]
    assert f.calls == ["cloudflare"]


def test_block_ip_rejected_then_google_fallback():
    f = _doh({"cloudflare": [(BLOCK, 60)], "google": [(GOOD, 60)]})
    assert bd.resolve("fapi.binance.com", fetch=f) == [GOOD]
    assert f.calls == ["cloudflare", "google"]


@pytest.mark.parametrize("bad", ["10.0.0.5", "192.168.1.1", "127.0.0.1", "169.254.1.1", "0.0.0.0", "172.16.0.9"])
def test_private_answers_rejected(bad):
    f = _doh({"cloudflare": [(bad, 60)], "google": [(bad, 60)]})
    with pytest.raises(bd.DohError):
        bd.resolve("fapi.binance.com", fetch=f, system=lambda h: [])


def test_doh_fallback_on_error():
    f = _doh({"cloudflare": OSError("down"), "google": [(GOOD, 60)]})
    assert bd.resolve("fapi.binance.com", fetch=f) == [GOOD]


def test_doh_down_fails_closed_even_if_system_returns_block_ip():
    f = _doh({"cloudflare": OSError("down"), "google": OSError("down")})
    with pytest.raises(bd.DohError):
        bd.resolve("fapi.binance.com", fetch=f, system=lambda h: [BLOCK])


def test_doh_down_system_dns_clean_is_accepted():
    f = _doh({"cloudflare": OSError("down"), "google": OSError("down")})
    assert bd.resolve("fapi.binance.com", fetch=f, system=lambda h: [GOOD]) == [GOOD]


def test_ttl_cache_hit_and_expiry():
    f = _doh({"cloudflare": [(GOOD, 30)], "google": []})
    t = [1000.0]
    bd.resolve("fapi.binance.com", fetch=f, now=lambda: t[0])
    bd.resolve("fapi.binance.com", fetch=f, now=lambda: t[0] + 29)
    assert len(f.calls) == 1
    bd.resolve("fapi.binance.com", fetch=f, now=lambda: t[0] + 31)
    assert len(f.calls) == 2


def test_cache_reset_forces_fresh_lookup():  # restart/reset state
    f = _doh({"cloudflare": [(GOOD, 600)], "google": []})
    bd.resolve("fapi.binance.com", fetch=f)
    bd.clear_cache()
    bd.resolve("fapi.binance.com", fetch=f)
    assert len(f.calls) == 2


def test_failure_not_cached():
    f = _doh({"cloudflare": OSError("x"), "google": OSError("x")})
    for _ in range(2):
        with pytest.raises(bd.DohError):
            bd.resolve("fapi.binance.com", fetch=f, system=lambda h: [])
    assert len(f.calls) == 4


def test_parse_cloudflare_json_ignores_cname_and_clamps_ttl():
    body = {"Status": 0, "Answer": [{"type": 5, "data": "x.cloudfront.net.", "TTL": 5},
                                    {"type": 1, "data": GOOD, "TTL": 1}]}
    assert bd.parse_dns_json(body) == [(GOOD, bd.MIN_TTL)]


def test_parse_nxdomain_or_garbage_is_empty():
    assert bd.parse_dns_json({"Status": 3}) == []
    assert bd.parse_dns_json({"Answer": "oops"}) == []
    assert bd.parse_dns_json("nope") == []


def test_non_binance_host_uses_system_resolver_untouched():
    assert bd.resolve("api.deribit.com", fetch=_doh({}), system=lambda h: ["1.1.1.1"]) == ["1.1.1.1"]


def test_tls_hostname_check_kept():
    ctx = bd.make_ssl_context()
    assert ctx.check_hostname is True
    assert ctx.verify_mode == ssl.CERT_REQUIRED


def test_connection_uses_ip_but_sni_is_real_name(monkeypatch):
    seen = {}

    class FakeSock:
        pass

    def fake_cc(addr, timeout=None, source_address=None):
        seen["addr"] = addr
        return FakeSock()

    class FakeCtx:
        def wrap_socket(self, sock, server_hostname=None):
            seen["sni"] = server_hostname
            return sock
    monkeypatch.setattr(bd.socket, "create_connection", fake_cc)
    monkeypatch.setattr(bd, "resolve", lambda host, **k: [GOOD])
    c = bd.DohHTTPSConnection("fapi.binance.com", 443, context=FakeCtx())
    c.connect()
    assert seen["addr"][0] == GOOD and seen["addr"][1] == 443
    assert seen["sni"] == "fapi.binance.com"


def test_connection_fails_closed_when_resolve_fails(monkeypatch):
    def boom(host, **k):
        raise bd.DohError("no safe answer")
    monkeypatch.setattr(bd, "resolve", boom)
    c = bd.DohHTTPSConnection("fapi.binance.com", 443)
    with pytest.raises(OSError):
        c.connect()


def test_urlopen_passes_non_binance_to_stock_urllib(monkeypatch):
    got = {}
    monkeypatch.setattr(bd.urllib.request, "urlopen", lambda u, timeout=None, **k: got.setdefault("u", u) or "stock")
    bd.urlopen("https://api.deribit.com/x", timeout=3)
    assert got["u"] == "https://api.deribit.com/x"


def test_api_error_http_400_propagates_as_httperror(monkeypatch):
    import urllib.error

    class Op:
        def open(self, req, timeout=None):
            raise urllib.error.HTTPError(req.full_url, 400, "bad", {}, None)
    monkeypatch.setattr(bd, "_opener", lambda: Op())
    with pytest.raises(urllib.error.HTTPError) as e:
        bd.urlopen("https://fapi.binance.com/fapi/v1/klines?symbol=X", timeout=3)
    assert e.value.code == 400


def test_every_python_caller_is_wired():
    root = Path(__file__).resolve().parents[3]
    callers = """MyTradingSys/backtest/fetch_bars.py MyTradingSys/backtest/layers/alerts/live_layers.py
MyTradingSys/backtest/layers/alerts/live_runner_cli.py MyTradingSys/backtest/layers/fabio/htf_context_live.py
MyTradingSys/backtest/layers/fabio/orderflow_live.py MyTradingSys/backtest/layers/wlow_bounce/status.py
MyTradingSys/runtime/kline_archiver.py MyTradingSys/runtime/oi_live/oi_recorder.py MyTradingSys/tools/live_aid/news_study.py
scripts/dev/chart_verify.py scripts/dev/indicator_audit_sample.py scripts/dev/market_guide.py scripts/dev/us_prep.py""".split()
    missing = [c for c in callers if "binance_doh" not in (root / c).read_text(encoding="utf-8")]
    assert not missing, missing
