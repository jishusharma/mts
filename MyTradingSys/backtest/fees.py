"""Single source of truth for exchange fees. Bug B081.

Every backtest imports from here. No file defines its own fee
constant. Fees are safety limits; the trader-source rule does not
apply.

Profiles, per side, as a fraction of price:
  DERIBIT_TAKER / DERIBIT_MAKER: Deribit BTC-PERPETUAL.
    Verified 2026-09-26 via public/get_instrument. maker 0.0,
    taker 0.0005 (5 bps per side, 10 bps round trip).
  FDAX (Eurex DAX future, Tom's home market; DAX probe PRE_REG_DAX.md): see FEES_FDAX below.
  BINANCE_TAKER / BINANCE_MAKER: Binance USDT-M perpetual,
    default tier. maker 0.0002 (4 bps RT), taker 0.0005 (10 bps RT).
    Source: T055b_PROVEN_SETUPS.md L22-23.

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

# --- Eurex FDAX (symbol GER40), research replays only: ~0.1 point per round turn on ~24000 -> 0.000005 per side ---


def fees_dict(entry, target, stop, timeout):
    """tom_bt.py / sim.py shape: per-leg fee fraction."""
    return {"entry": entry, "target": target, "stop": stop, "timeout": timeout}


# --- tom_bt.py style profiles ---
FEES_DERIBIT = fees_dict(entry=DERIBIT_MAKER, target=DERIBIT_MAKER, stop=DERIBIT_TAKER, timeout=DERIBIT_TAKER)
FEES_ALL_TAKER = fees_dict(entry=DERIBIT_TAKER, target=DERIBIT_TAKER, stop=DERIBIT_TAKER, timeout=DERIBIT_TAKER)

# --- Eurex FDAX (DAX probe, research/tom_transfer_2026-10-11/PRE_REG_DAX.md "Fees") ---
# Source: the pre-registration. Round turn about EUR 2.5 per contract against EUR 25 per index point = 0.1 point round
# turn (0.05 point per side, about 2.1e-6 of price at DAX 24000). The frozen figure is 0.000005 of price per side on
# every leg, maker and taker alike (0.12 point per side at 24000): about 2.4 times the arithmetic above, i.e. on the
# conservative side. The EUR 2.5 is an order-of-magnitude retail figure, not a fetched fee schedule. Stress (+ 1 point on
# stop and timeout legs) is `slip_pts` in tom_bt.sim_limit_trade, not a fee.
FDAX_PER_SIDE = 0.000005
FEES_FDAX = fees_dict(entry=FDAX_PER_SIDE, target=FDAX_PER_SIDE, stop=FDAX_PER_SIDE, timeout=FDAX_PER_SIDE)
FDAX_FEE_PER_SIDE = FDAX_PER_SIDE  # alias mirrored by ExecutionMathConstants.FDAX_FEE_PER_SIDE (test_b070_fee_parity)
