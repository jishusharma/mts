"""Host-agnostic HTTPS GET through DNS-over-HTTPS with the IP pinned and SNI kept (live-aid-oi-poller-all-venues-1110).

Same idea as binance_doh.py (which stays untouched for the live runner): resolve the real host name via Cloudflare then
Google DoH, drop block-page / private / loopback answers, connect to the IP, and keep SNI + the certificate hostname check
on the REAL name. Public market data only; machine DNS, hosts file and browser settings are never touched.
Fail closed: no safe address -> DohError (an OSError).
"""
from __future__ import annotations

import http.client
import socket
import ssl
import threading
import time
import urllib.request
from urllib.parse import urlparse

from MyTradingSys.runtime import binance_doh as _b   # reuse the parser, the safe-IP rule and the provider list; nothing is changed there

DohError = _b.DohError
_cache: dict[str, tuple[float, list[str]]] = {}
_lock = threading.Lock()


def clear_cache() -> None:
    with _lock:
        _cache.clear()


def resolve_any(host: str, fetch=None, system=None, now=time.time) -> list[str]:
    """Safe IPv4 addresses for ANY host via DoH; a clean system answer is the fallback, a block/private one never is."""
    fetch = fetch or _b._doh_fetch
    system = system or _b._system
    t = now()
    with _lock:
        hit = _cache.get(host)
        if hit and hit[0] > t:
            return list(hit[1])
    why = []
    for name, _, _ in _b.PROVIDERS:
        try:
            recs = fetch(name, host)
        except Exception as e:  # noqa: BLE001 - any transport/parse failure -> next provider
            why.append(f"{name}: {type(e).__name__}")
            continue
        good = [(ip, ttl) for ip, ttl in recs if _b._safe_ip(ip)]
        if not good:
            why.append(f"{name}: no safe answer")
            continue
        ips = [ip for ip, _ in good]
        with _lock:
            _cache[host] = (t + min(ttl for _, ttl in good), ips)
        return ips
    sys_ips = [ip for ip in system(host) if _b._safe_ip(ip)]
    if sys_ips:
        return sys_ips
    raise DohError(f"FAIL CLOSED: no safe address for {host} ({'; '.join(why)})")


class _Conn(http.client.HTTPSConnection):
    def connect(self):
        err = None
        for ip in resolve_any(self.host):
            try:
                sock = socket.create_connection((ip, self.port), self.timeout, self.source_address)
                self.sock = self._context.wrap_socket(sock, server_hostname=self.host)
                return
            except OSError as e:
                err = e
        raise err or DohError(f"no address for {self.host}")


class _Handler(urllib.request.HTTPSHandler):
    def https_open(self, req):
        return self.do_open(lambda host, **kw: _Conn(host, context=ssl.create_default_context(), **kw), req)


_opener = None


def urlopen_pinned(url, timeout=10.0):
    """urlopen through DoH + pinned IP for any https host (stock cert verification, SNI on the real name)."""
    global _opener
    if _opener is None:
        _opener = urllib.request.build_opener(_Handler())
    req = url if isinstance(url, urllib.request.Request) else urllib.request.Request(url)
    if not req.has_header("User-agent"):
        req.add_header("User-Agent", "mts-live-aid-oi-poller/1")
    return _opener.open(req, timeout=timeout)
