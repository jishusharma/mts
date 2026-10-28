"""Deribit fee model (spec conventions). All option fees are per contract (1 contract = 1 BTC notional), in BTC."""
import datetime
import os
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
if _HERE not in sys.path:
    sys.path.insert(0, _HERE)

from instruments import weekday_of_ms  # noqa: E402

TRADE_FEE_CAP_BTC = 0.0003
TRADE_FEE_PREMIUM_FRAC = 0.125
OLD_TRADE_FEE_CAP_BTC = 0.0004
OLD_FEE_CUTOFF_MS = int(datetime.datetime(2020, 8, 24, tzinfo=datetime.timezone.utc).timestamp() * 1000)
DELIVERY_FEE_CAP_BTC = 0.00015
PERP_TAKER_RATE = 0.0005  # 0.05 % of notional per fill (taker; maker not assumed)
FRIDAY = 4


def trade_fee_btc(price_btc, ts_ms=None):
    """min(0.0003, 0.125*price) BTC per contract per leg; cap is 0.0004 before 2020-08-24 UTC."""
    cap = OLD_TRADE_FEE_CAP_BTC if (ts_ms is not None and ts_ms < OLD_FEE_CUTOFF_MS) else TRADE_FEE_CAP_BTC
    return min(cap, TRADE_FEE_PREMIUM_FRAC * price_btc)


def delivery_fee_btc(payoff_btc, expiry_ms=None, *, weekday=None):
    """Only when ITM (payoff > 0) AND the expiry weekday is Friday (non-daily): min(0.00015, 0.125*payoff).
    Mon-Thu, Sat, Sun expiries are treated as daily => 0."""
    if weekday is None:
        if expiry_ms is None:
            return 0.0
        weekday = weekday_of_ms(expiry_ms)
    if payoff_btc is None or not payoff_btc > 0.0 or weekday != FRIDAY:
        return 0.0
    return min(DELIVERY_FEE_CAP_BTC, TRADE_FEE_PREMIUM_FRAC * payoff_btc)


def perp_fee_usd(notional_usd):
    return PERP_TAKER_RATE * abs(notional_usd)


def perp_fee_btc(notional_usd, price_usd):
    return perp_fee_usd(notional_usd) / price_usd
