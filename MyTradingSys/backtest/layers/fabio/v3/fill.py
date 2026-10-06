"""Fabio v3 fills (FABIO_V3_SPEC.md section 5.1; BP:50-51, fixes FBR:43-46).

A limit at P placed at the close of bar i is live from bar i+1. Buy fills in bar j iff l[j] <= P - TICK; sell fills iff
h[j] >= P + TICK (1e-9 tolerance). Fill price = P (no price improvement). Provenance: P41 SIM (fills, TICK); the
3-bar validity of B / D rest orders is P36 / P39 NS-fixed and is applied by models.py (end_idx), not here.
"""
from .costs import EPS, TICK


def fills_in_bar(bar, s, price, tick=TICK):
    """True iff a resting limit at `price` (buy for s=+1, sell for s=-1) fills inside this bar (fill-through rule)."""
    if s > 0:
        return bar["l"] <= price - tick + EPS
    return bar["h"] >= price + tick - EPS


def find_fill(bars, i, s, price, tick=TICK, end_idx=None):
    """First bar j in [i+1, end_idx] where the limit placed at the close of bar i fills -> (j, price), else None.

    The arming bar i itself never fills the order (spec 5.1, T28). end_idx is inclusive and defaults to the last bar.
    """
    end = len(bars) - 1 if end_idx is None else min(end_idx, len(bars) - 1)
    for j in range(i + 1, end + 1):
        if fills_in_bar(bars[j], s, price, tick):
            return (j, price)
    return None


def taker_fill(bars, j):
    """Taker entry at the open of bar j -> (j, o[j]). Bar j becomes the fill bar (spec 5.1)."""
    return (j, bars[j]["o"])


def missed_winner(bars, s, price, D, from_idx, end_idx=None):
    """Spec 5.1: an armed order that never fills while price later reaches P + s*2D before the window ends.

    Scans bars [from_idx, end_idx] (from_idx = arming bar + 1). The caller only asks for orders that never filled.
    """
    end = len(bars) - 1 if end_idx is None else min(end_idx, len(bars) - 1)
    reach = price + s * 2.0 * D
    for j in range(from_idx, end + 1):
        if s > 0 and bars[j]["h"] >= reach - EPS:
            return True
        if s < 0 and bars[j]["l"] <= reach + EPS:
            return True
    return False
