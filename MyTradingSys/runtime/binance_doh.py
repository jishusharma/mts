"""Resolve Binance hosts through DNS-over-HTTPS (ISP DNS block fix, d-fix-binance-dns-block-1109).

Some ISPs (Jio) answer fapi/fstream/api.binance.com with a block-page IP. This module resolves *.binance.com and
*.binance.vision via Cloudflare DoH, then Google DoH, caches by TTL, rejects the block IP and any private/loopback answer,
and connects to the resolved IP while keeping SNI and the TLS certificate hostname check on the REAL name.
Public market data only; no machine DNS/hosts setting is touched. Fail closed: no safe answer -> OSError (DohError).
Drop-in: `from MyTradingSys.runtime.binance_doh import urlopen` (same call shape as urllib.request.urlopen).
"""
from __future__ import annotations

import http.client
import ipaddress
import json
import socket
import ssl
import sys
import threading
import time
import urllib.request
from urllib.parse import urlparse

BLOCK_IPS = frozenset({"49.44.79.236"})   # Jio block page, measured 2026-11-09
MIN_TTL, MAX_TTL = 30, 300                # OURS: clamp so a 1 s TTL does not hammer DoH and a day-long TTL cannot pin a dead IP
DOH_TIMEOUT = 5.0
PROVIDERS = (  # IP literals: no DNS needed to reach the resolver; certs carry IP SANs, so verification stays on
    ("cloudflare", "https://1.1.1.1/dns-query?name={host}&type=A", {"accept": "application/dns-json"}),
    ("google", "https://8.8.8.8/resolve?name={host}&type=A", {"accept": "application/dns-json"}),
)
_SUFFIXES = (".binance.com", ".binance.vision")
_cache: dict[str, tuple[float, list[str]]] = {}
_lock = threading.Lock()


class DohError(OSError):
    """No safe address for a Binance host (all DoH providers failed or only block/private answers)."""


def log(msg: str) -> None:
    print(f"[binance_doh] {msg}", file=sys.stderr)


def is_binance_host(host: str) -> bool:
    h = (host or "").lower().rstrip(".")
    return h in ("binance.com", "binance.vision") or h.endswith(_SUFFIXES)


def clear_cache() -> None:
    with _lock:
        _cache.clear()


def _safe_ip(ip: str) -> bool:
    try:
        a = ipaddress.ip_address(ip)
    except ValueError:
        return False
    if ip in BLOCK_IPS:
        return False
    return not (a.is_private or a.is_loopback or a.is_link_local or a.is_unspecified or a.is_multicast or a.is_reserved)


def parse_dns_json(body) -> list[tuple[str, int]]:
    """(ip, ttl) of A records from an application/dns-json answer; CNAMEs and junk ignored."""
    if not isinstance(body, dict) or body.get("Status", 0) != 0 or not isinstance(body.get("Answer"), list):
        return []
    out = []
    for rec in body["Answer"]:
        if isinstance(rec, dict) and rec.get("type") == 1 and isinstance(rec.get("data"), str):
            try:
                ttl = int(rec.get("TTL", MIN_TTL))
            except (TypeError, ValueError):
                ttl = MIN_TTL
            out.append((rec["data"], max(MIN_TTL, min(MAX_TTL, ttl))))
    return out


def _doh_fetch(provider: str, host: str) -> list[tuple[str, int]]:
    for name, url, headers in PROVIDERS:
        if name == provider:
            req = urllib.request.Request(url.format(host=host), headers=headers)
            with urllib.request.urlopen(req, timeout=DOH_TIMEOUT) as r:
                return parse_dns_json(json.loads(r.read().decode("utf-8")))
    raise ValueError(provider)


def _system(host: str) -> list[str]:
    try:
        return sorted({i[4][0] for i in socket.getaddrinfo(host, 443, socket.AF_INET, socket.SOCK_STREAM)})
    except OSError:
        return []


def resolve(host: str, fetch=None, system=None, now=time.time) -> list[str]:
    """Safe IPv4 addresses for host. Non-Binance hosts use the system resolver untouched."""
    system = system or _system
    if not is_binance_host(host):
        return system(host)
    fetch = fetch or _doh_fetch
    t = now()
    with _lock:
        hit = _cache.get(host)
        if hit and hit[0] > t:
            return list(hit[1])
    why = []
    for name, _, _ in PROVIDERS:
        try:
            recs = fetch(name, host)
        except Exception as e:  # noqa: BLE001 - any transport/parse failure -> next provider
            why.append(f"{name}: {type(e).__name__}")
            continue
        good = [(ip, ttl) for ip, ttl in recs if _safe_ip(ip)]
        if not good:
            why.append(f"{name}: no safe answer ({[ip for ip, _ in recs]})")
            continue
        ips = [ip for ip, _ in good]
        with _lock:
            _cache[host] = (t + min(ttl for _, ttl in good), ips)
        return ips
    # both DoH providers failed: a clean system answer is acceptable, a block/private one never is
    sys_ips = [ip for ip in system(host) if _safe_ip(ip)]
    if sys_ips:
        log(f"DoH failed for {host} ({'; '.join(why)}); using validated system DNS {sys_ips}")
        return sys_ips
    msg = f"FAIL CLOSED: no safe address for {host} ({'; '.join(why)})"
    log(msg)
    raise DohError(msg)


def make_ssl_context() -> ssl.SSLContext:
    ctx = ssl.create_default_context()      # check_hostname=True, CERT_REQUIRED
    return ctx


class DohHTTPSConnection(http.client.HTTPSConnection):
    """Connects to the DoH-resolved IP; SNI + certificate hostname check use the real host name."""

    def connect(self):
        try:
            ips = resolve(self.host)
        except DohError:
            raise
        err = None
        for ip in ips:
            try:
                sock = socket.create_connection((ip, self.port), self.timeout, self.source_address)
                self.sock = self._context.wrap_socket(sock, server_hostname=self.host)
                return
            except OSError as e:
                err = e
        raise err or DohError(f"no address for {self.host}")


class _Handler(urllib.request.HTTPSHandler):
    def https_open(self, req):
        return self.do_open(lambda host, **kw: DohHTTPSConnection(host, context=make_ssl_context(), **kw), req)


_opener_cache = None


def _opener():
    global _opener_cache
    if _opener_cache is None:
        _opener_cache = urllib.request.build_opener(_Handler())
    return _opener_cache


def urlopen(url, timeout=None, **kw):
    """Drop-in for urllib.request.urlopen: Binance hosts go through DoH + IP connect, everything else is stock."""
    req = url if isinstance(url, urllib.request.Request) else urllib.request.Request(url)
    host = urlparse(req.full_url).hostname
    if not is_binance_host(host or ""):
        return urllib.request.urlopen(url, timeout=timeout, **kw)
    return _opener().open(req, timeout=timeout) if timeout is not None else _opener().open(req)


if __name__ == "__main__":  # smoke: python MyTradingSys/runtime/binance_doh.py fapi.binance.com
    for h in sys.argv[1:] or ["fapi.binance.com", "fstream.binance.com"]:
        print(h, resolve(h))
