"""STUB (fail-first): Bybit v5 public klines for MAL-R03/R04, 1h and 4h. Implemented in the next commit."""
COINS = []
IV_MS = {"60": 3600000, "240": 14400000}


def clean_bars(rows, iv_ms, now_ms):
    raise NotImplementedError


def find_gaps(rows, iv_ms):
    raise NotImplementedError
