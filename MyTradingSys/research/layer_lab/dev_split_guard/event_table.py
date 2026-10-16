"""Pure timestamp guards for keeping layer-lab rows inside the DEV window."""
from datetime import datetime, timezone
from numbers import Real

DEV_START_MS = 1640995200000       # 2022-01-01T00:00:00Z, inclusive
DEV_END_EXCLUSIVE_MS = 1719792000000  # 2024-07-01T00:00:00Z


def _timestamp_ms(value, key):
    """Parse an epoch-millisecond number or an ISO-8601 timestamp as UTC."""
    if isinstance(value, bool) or value is None:
        raise ValueError("missing or invalid timestamp for key %r: %r" % (key, value))
    if isinstance(value, Real):
        return int(value)
    if isinstance(value, str):
        raw = value.strip()
        if not raw:
            raise ValueError("missing or invalid timestamp for key %r: %r" % (key, value))
        try:
            return int(float(raw))
        except ValueError:
            pass
        if raw.endswith("Z"):
            raw = raw[:-1] + "+00:00"
        try:
            parsed = datetime.fromisoformat(raw)
        except ValueError as exc:
            raise ValueError("invalid timestamp for key %r: %r" % (key, value)) from exc
        if parsed.tzinfo is None:
            parsed = parsed.replace(tzinfo=timezone.utc)
        return int(parsed.timestamp() * 1000)
    raise ValueError("invalid timestamp for key %r: %r" % (key, value))


def dev_only(rows, t_key):
    """Return (DEV rows, dropped count); fail closed if any row lacks a valid timestamp."""
    kept = []
    dropped = 0
    for row in rows:
        try:
            value = row[t_key]
        except (KeyError, TypeError) as exc:
            raise ValueError("missing timestamp key %r in row %r" % (t_key, row)) from exc
        stamp = _timestamp_ms(value, t_key)
        if DEV_START_MS <= stamp < DEV_END_EXCLUSIVE_MS:
            kept.append(row)
        else:
            dropped += 1
    return kept, dropped


def assert_dev(rows, t_key):
    """Raise ValueError naming the first missing, invalid, or out-of-DEV timestamp."""
    for row in rows:
        try:
            value = row[t_key]
        except (KeyError, TypeError) as exc:
            raise ValueError("missing timestamp key %r in row %r" % (t_key, row)) from exc
        stamp = _timestamp_ms(value, t_key)
        if not DEV_START_MS <= stamp < DEV_END_EXCLUSIVE_MS:
            raise ValueError("timestamp outside DEV window: %s" % value)
