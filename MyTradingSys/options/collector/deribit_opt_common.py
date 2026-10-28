"""Shared plumbing for the BTC options data collectors (options module, data collection only).

Public Deribit market data ONLY: every request is a GET on <host>/api/v2/public/<method>, no keys, no auth
headers, no private/* methods, no orders. The client refuses anything else (see DeribitPublic._check_method /
_check_base). Nothing here imports or touches the live trading system.

Contents
  * DeribitPublic    - rate limited (<= MAX_RATE req/s) client with exponential backoff on 10028 / 429 / 5xx / network
  * RateLimiter      - thread-safe request-start spacing
  * gz helpers       - append one gzip member per JSONL line with tail-integrity check + repair, tolerant reader
  * atomic writers   - tmp file + os.replace, LF newlines
Stdlib only (the repo uses urllib everywhere; `requests` is not a repo dependency).
"""
import gzip
import http.client
import json
import os
import random
import re
import threading
import time
import urllib.error
import urllib.parse
import urllib.request
import zlib
from pathlib import Path

LIVE_BASE = "https://www.deribit.com/api/v2"
HISTORY_BASE = "https://history.deribit.com/api/v2"  # Deribit's public historical-trades host, same API, no auth
ALLOWED_HOSTS = ("www.deribit.com", "history.deribit.com")
MAX_RATE = 5.0  # operator limit: <= 5 requests per second per process
RETRYABLE_CODES = (10028, 10040)  # too_many_requests, retry
RETRYABLE_STATUS = (429, 500, 502, 503, 504)
USER_AGENT = "MTS-options-collector/1.0 (public market data, read-only)"
METHOD_RE = re.compile(r"^public/[a-z_]+$")

DAY_MS = 86400000
HOUR_MS = 3600000


class DeribitError(RuntimeError):
    """Non-retryable API error, or retries exhausted."""

    def __init__(self, method, code, message, data=None):
        super().__init__("%s: [%s] %s%s" % (method, code, message, (" " + json.dumps(data)) if data else ""))
        self.method = method
        self.code = code
        self.message = message
        self.data = data


def now_ms():
    return int(time.time() * 1000)


def iso(ms):
    t = time.gmtime(ms / 1000.0)
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", t)


def utc_date(ms):
    return time.strftime("%Y-%m-%d", time.gmtime(ms / 1000.0))


def date_to_ms(date_str):
    """'YYYY-MM-DD' -> ms at 00:00:00 UTC."""
    import calendar
    y, m, d = (int(x) for x in date_str.split("-"))
    return calendar.timegm((y, m, d, 0, 0, 0)) * 1000


class RateLimiter:
    """Spaces request starts by 1/rate seconds across threads."""

    def __init__(self, rate, clock=time.monotonic, sleep=time.sleep):
        if rate <= 0 or rate > MAX_RATE:
            raise ValueError("rate must be in (0, %s] req/s, got %r" % (MAX_RATE, rate))
        self.interval = 1.0 / rate
        self.clock = clock
        self.sleep = sleep
        self._next = 0.0
        self._lock = threading.Lock()

    def acquire(self):
        with self._lock:
            now = self.clock()
            start = max(now, self._next)
            self._next = start + self.interval
        wait = start - now
        if wait > 0:
            self.sleep(wait)


def urllib_transport(url, timeout):
    """GET url -> (status, body_bytes, headers). HTTP errors are returned, network errors raise."""
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT, "Accept": "application/json",
                                               "Accept-Encoding": "gzip"})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            status, body, headers = r.status, r.read(), dict(r.headers)
    except urllib.error.HTTPError as e:
        status, body, headers = e.code, e.read(), dict(e.headers or {})
    enc = {k.lower(): v for k, v in headers.items()}.get("content-encoding", "")
    if enc.lower() == "gzip" and body:
        body = gzip.decompress(body)
    return status, body, headers


class DeribitPublic:
    """Public-only Deribit JSON-RPC-over-GET client.

    transport(url, timeout) -> (status, body_bytes, headers) is injectable for tests; sleep/clock too.
    """

    def __init__(self, base=LIVE_BASE, rate=4.0, max_retries=6, backoff_base=1.0, backoff_cap=60.0, timeout=90,
                 transport=None, sleep=time.sleep, clock=time.monotonic, jitter=True, log=None):
        self._check_base(base)
        self.base = base.rstrip("/")
        self.max_retries = max_retries
        self.backoff_base = backoff_base
        self.backoff_cap = backoff_cap
        self.timeout = timeout
        self.transport = transport or urllib_transport
        self.sleep = sleep
        self.jitter = jitter
        self.log = log or (lambda msg: None)
        self.limiter = RateLimiter(rate, clock=clock, sleep=sleep)
        self.n_requests = 0
        self.n_retries = 0
        self._lock = threading.Lock()

    @staticmethod
    def _check_base(base):
        p = urllib.parse.urlparse(base)
        if p.scheme != "https" or p.hostname not in ALLOWED_HOSTS or not p.path.rstrip("/").endswith("/api/v2"):
            raise ValueError("base URL not allowed (public Deribit hosts only): %r" % base)

    @staticmethod
    def _check_method(method):
        if not METHOD_RE.match(method):
            raise ValueError("only public/* methods are allowed, got %r" % method)

    def _delay(self, attempt, retry_after):
        d = min(self.backoff_cap, self.backoff_base * (2 ** attempt))
        if self.jitter:
            d *= 1.0 + 0.25 * random.random()
        if retry_after:
            try:
                d = max(d, float(retry_after))
            except ValueError:
                pass
        return d

    def call(self, method, params=None):
        """GET public/<method>; returns payload['result']. Retries 10028/10040, HTTP 429/5xx, network errors."""
        self._check_method(method)
        url = "%s/%s" % (self.base, method)
        if params:
            url += "?" + urllib.parse.urlencode(params)
        attempt = 0
        while True:
            self.limiter.acquire()
            with self._lock:
                self.n_requests += 1
            reason = None
            retry_after = None
            try:
                status, body, headers = self.transport(url, self.timeout)
                lower = {k.lower(): v for k, v in (headers or {}).items()}
                retry_after = lower.get("retry-after")
                try:
                    payload = json.loads(body.decode("utf-8")) if body else None
                except ValueError:
                    payload = None
                if isinstance(payload, dict) and payload.get("error"):
                    err = payload["error"]
                    code = err.get("code") if isinstance(err, dict) else err
                    if code in RETRYABLE_CODES:
                        reason = "deribit_%s" % code
                    else:
                        msg = err.get("message") if isinstance(err, dict) else str(err)
                        raise DeribitError(method, code, msg, err.get("data") if isinstance(err, dict) else None)
                elif status in RETRYABLE_STATUS:
                    reason = "http_%d" % status
                elif status >= 400:
                    raise DeribitError(method, "http_%d" % status, "HTTP error")
                elif not isinstance(payload, dict) or "result" not in payload:
                    reason = "bad_body"
                else:
                    return payload["result"]
            except (urllib.error.URLError, TimeoutError, ConnectionError, http.client.HTTPException, OSError) as e:
                reason = "net_%s" % type(e).__name__
            if attempt >= self.max_retries:
                raise DeribitError(method, "retries_exhausted", "gave up after %d retries (last: %s)" % (attempt, reason))
            delay = self._delay(attempt, retry_after)
            with self._lock:
                self.n_retries += 1
            self.log("retry %s %s attempt=%d sleep=%.1fs" % (method, reason, attempt + 1, delay))
            self.sleep(delay)
            attempt += 1


# ---------------------------------------------------------------- file helpers

def atomic_write_text(path, text):
    """Write text with LF newlines via tmp file + os.replace (readers never see a half file)."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(path.name + ".tmp")
    with open(tmp, "w", encoding="utf-8", newline="\n") as f:
        f.write(text)
        f.flush()
        os.fsync(f.fileno())
    os.replace(tmp, path)


def atomic_write_json(path, obj):
    atomic_write_text(path, json.dumps(obj, indent=1, sort_keys=True) + "\n")


def read_json(path, default=None):
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except (OSError, ValueError):
        return default


def gz_scan(path):
    """Walk the gzip members of path. Returns (good_len, n_lines, clean).

    good_len = byte offset just after the last COMPLETE member; clean is False when the file has a truncated or
    corrupt tail (crash mid-write). n_lines counts newline bytes in the complete members.
    """
    data = Path(path).read_bytes()
    view = memoryview(data)
    pos = 0
    lines = 0
    while pos < len(data):
        d = zlib.decompressobj(wbits=31)
        try:
            out = d.decompress(view[pos:])
        except zlib.error:
            return pos, lines, False
        if not d.eof:
            return pos, lines, False
        lines += out.count(b"\n")
        pos = len(data) - len(d.unused_data)
    return pos, lines, True


def append_gz_line(path, text):
    """Append ONE line (text, '\\n' added if missing) as its own gzip member. Single write + fsync.

    A damaged tail left by an earlier crash is cut back to the last complete member first (the cut bytes are kept
    in <path>.badtail). Returns the number of bytes appended.
    """
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    if not text.endswith("\n"):
        text += "\n"
    if path.exists() and path.stat().st_size > 0:
        good, _, clean = gz_scan(path)
        if not clean:
            raw = path.read_bytes()
            with open(str(path) + ".badtail", "ab") as bt:
                bt.write(raw[good:])
            with open(path, "r+b") as f:
                f.truncate(good)
    member = gzip.compress(text.encode("utf-8"), compresslevel=6, mtime=0)
    with open(path, "ab") as f:
        f.write(member)
        f.flush()
        os.fsync(f.fileno())
    return len(member)


def read_gz_lines(path, strict=False):
    """Yield decoded lines of a (multi-member) gzip file. A truncated final member stops iteration silently
    unless strict=True (then it raises EOFError / zlib.error)."""
    path = Path(path)
    if strict:
        with gzip.open(path, "rt", encoding="utf-8") as f:
            for line in f:
                yield line
        return
    good, _, _ = gz_scan(path)
    data = path.read_bytes()[:good]
    text = gzip.decompress(data).decode("utf-8") if data else ""
    for line in text.splitlines(keepends=True):
        yield line


def count_gz_lines(path):
    """Count newline-terminated lines in a gzip file by streaming (does not parse JSON)."""
    n = 0
    with gzip.open(path, "rb") as f:
        while True:
            chunk = f.read(1 << 20)
            if not chunk:
                break
            n += chunk.count(b"\n")
    return n
