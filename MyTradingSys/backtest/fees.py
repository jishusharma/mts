"""Single source of truth for exchange fees. Bug B081.

Every backtest imports from here. No file defines its own fee
constant. Fees are safety limits; the trader-source rule does not
apply.

Profiles, per side, as a fraction of price:
  DERIBIT_TAKER / DERIBIT_MAKER: Deribit BTC-PERPETUAL.
    Verified 2026-09-26 via public/get_instrument. maker 0.0,
    taker 0.0005 (5 bps per side, 10 bps round trip).
  BINANCE_TAKER / BINANCE_MAKER: Binance USDT-M perpetual,
    default tier. maker 0.0002 (4 bps RT), taker 0.0005 (10 bps RT).
    Source: T055b_PROVEN_SETUPS.md L22-23.
  LEGACY_FABIO_TAKER / LEGACY_FABIO_MAKER: pre-B081 value used by
    MyTradingSys/backtest/layers/fabio/fabio_of_model.py.
    Derived from T055b_PROVEN_SETUPS.md L22-23 read as Deribit
    taker 7 bps RT, maker -3 bps RT rebate. Pending review: the
    API-verified Deribit schedule above says maker 0 / taker 5 bps.
    Do not use for new code. Kept so existing fabio tests pass
    until the operator decides which number fabio should carry.

Change rule: edit this file. Then run:
  python -m pytest MyTradingSys/tests MyTradingSys/backtest -q
"""
import sys
sys.dont_write_bytecode = True

# --- Deribit BTC-PERPETUAL (API-verified 2026-09-26) ---
DERIBIT_TAKER = 0.0005
DERIBIT_MAKER = 0.0

# --- Binance USDT-M perpetual (T055b L22-23) ---
BINANCE_TAKER = 0.0005
BINANCE_MAKER = 0.0002

# --- Fabio layer (pre-B081; pending review) ---
LEGACY_FABIO_TAKER = 0.00035
LEGACY_FABIO_MAKER = -0.00015


def fees_dict(entry, target, stop, timeout):
    """tom_bt.py / sim.py shape: per-leg fee fraction."""
    return {"entry": entry, "target": target, "stop": stop, "timeout": timeout}


# --- tom_bt.py style profiles ---
FEES_DERIBIT = fees_dict(entry=DERIBIT_MAKER, target=DERIBIT_MAKER, stop=DERIBIT_TAKER, timeout=DERIBIT_TAKER)
FEES_ALL_TAKER = fees_dict(entry=DERIBIT_TAKER, target=DERIBIT_TAKER, stop=DERIBIT_TAKER, timeout=DERIBIT_TAKER)
