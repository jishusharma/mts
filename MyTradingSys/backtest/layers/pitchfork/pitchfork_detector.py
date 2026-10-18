"""Pitchfork Detector and Geometric Channel Engine for MTS.

Implements Andrews' Pitchfork, Schiff Pitchfork, and Modified Schiff Pitchfork
with non-repainting pivot confirmation, slope gating, median line reach tracking,
and Hagopian failure detection.

References:
- Alan H. Andrews, The Babson Action-Reaction Course (1960-1975)
- Jerome Schiff, Schiff Pitchfork Formulation
- Timothy Morge, Trading with Median Lines: Mapping the Markets (2002)
- Patrick Mikula, The Best Trendline Methods of Alan Andrews (2002)
- Mircea Dologa, Integrated Pitchfork Analysis (2007)
"""

from dataclasses import dataclass
from enum import Enum
import math
from typing import List, Optional, Tuple, Dict, Any


class PitchforkVariant(Enum):
    STANDARD = "standard"
    SCHIFF = "schiff"
    MODIFIED_SCHIFF = "modified_schiff"


@dataclass
class PitchforkPivot:
    index: int
    price: float
    is_high: bool
    timestamp: Optional[str] = None


@dataclass
class PitchforkBarResult:
    bar_index: int
    close_price: float
    ml_value: float
    uml_value: float
    lml_value: float
    reached_ml: bool
    breached_uml: bool
    breached_lml: bool
    hagopian_triggered: bool
    status: str  # "tracking", "reached_ml", "hagopian_failure", "invalidated"


class PitchforkChannel:
    """Represents a single 3-pivot Pitchfork channel."""

    def __init__(
        self,
        p0: PitchforkPivot,
        p1: PitchforkPivot,
        p2: PitchforkPivot,
        variant: PitchforkVariant = PitchforkVariant.STANDARD,
    ):
        self.p0_orig = p0
        self.p1 = p1
        self.p2 = p2
        self.variant = variant

        # Determine effective P0 based on variant
        if variant == PitchforkVariant.STANDARD:
            self.t0 = float(p0.index)
            self.p0 = float(p0.price)
        elif variant == PitchforkVariant.SCHIFF:
            # Shift 50% in time and 50% in price towards P1
            self.t0 = float(p0.index) + 0.5 * (float(p1.index) - float(p0.index))
            self.p0 = float(p0.price) + 0.5 * (float(p1.price) - float(p0.price))
        elif variant == PitchforkVariant.MODIFIED_SCHIFF:
            # Shift 50% in price only, keep original time
            self.t0 = float(p0.index)
            self.p0 = float(p0.price) + 0.5 * (float(p1.price) - float(p0.price))
        else:
            raise ValueError(f"Unknown variant {variant}")

        # Midpoint of P1 and P2
        self.t_m = (float(p1.index) + float(p2.index)) / 2.0
        self.p_m = (float(p1.price) + float(p2.price)) / 2.0

        # Time delta must be positive
        dt = self.t_m - self.t0
        if dt <= 0:
            raise ValueError(f"Invalid geometry: t_m ({self.t_m}) <= t0 ({self.t0})")

        # Slope of Median Line (price units per bar)
        self.slope = (self.p_m - self.p0) / dt

        # Intercepts: line equation p(t) = slope * (t - ref_t) + ref_p
        # For ML: p(t) = slope * (t - t0) + p0
        # For UML and LML: parallel lines passing through P1 and P2
        # UML passes through P1: p_uml(t) = slope * (t - t1) + p1
        # LML passes through P2: p_lml(t) = slope * (t - t2) + p2
        self.t1 = float(p1.index)
        self.p1_val = float(p1.price)
        self.t2 = float(p2.index)
        self.p2_val = float(p2.price)

        # Upper and lower vertical offsets from ML
        # ML at t1: p_ml(t1) = slope * (t1 - t0) + p0
        # Offset UML = p1 - p_ml(t1)
        ml_at_t1 = self.slope * (self.t1 - self.t0) + self.p0
        self.offset_p1 = self.p1_val - ml_at_t1

        ml_at_t2 = self.slope * (self.t2 - self.t0) + self.p0
        self.offset_p2 = self.p2_val - ml_at_t2

        # Order tines into UML (higher) and LML (lower)
        if self.offset_p1 >= self.offset_p2:
            self.offset_uml = self.offset_p1
            self.offset_lml = self.offset_p2
        else:
            self.offset_uml = self.offset_p2
            self.offset_lml = self.offset_p1

        self.channel_width = abs(self.offset_uml - self.offset_lml)
        self.half_width = self.channel_width / 2.0

        # State tracking
        self.has_reached_ml = False
        self.has_stalled_before_ml = False
        self.hagopian_triggered = False
        self.max_ml_approach_ratio = 0.0  # 0.0 = at tine, 1.0 = reached ML

    def get_ml(self, t: float) -> float:
        """Value of Median Line at bar index t."""
        return self.p0 + self.slope * (t - self.t0)

    def get_uml(self, t: float) -> float:
        """Value of Upper Median Line at bar index t."""
        return self.get_ml(t) + self.offset_uml

    def get_lml(self, t: float) -> float:
        """Value of Lower Median Line at bar index t."""
        return self.get_ml(t) + self.offset_lml

    def get_upper_warning_line(self, t: float, level: int = 1) -> float:
        """Warning Line above UML (spaced by half-width or full width)."""
        return self.get_uml(t) + level * self.half_width

    def get_lower_warning_line(self, t: float, level: int = 1) -> float:
        """Warning Line below LML."""
        return self.get_lml(t) - level * self.half_width

    def get_upper_quarter_line(self, t: float) -> float:
        """Quartile line between ML and UML (75% line)."""
        return self.get_ml(t) + 0.5 * self.offset_uml

    def get_lower_quarter_line(self, t: float) -> float:
        """Quartile line between ML and LML (25% line)."""
        return self.get_ml(t) + 0.5 * self.offset_lml

    def is_ascending(self) -> bool:
        """True if the median line slopes upwards."""
        return self.slope > 0.0

    def eval_bar(self, t: int, high: float, low: float, close: float) -> PitchforkBarResult:
        """Evaluate a single bar at index t against the pitchfork."""
        ml = self.get_ml(float(t))
        uml = self.get_uml(float(t))
        lml = self.get_lml(float(t))

        # Check reach of ML
        if not self.has_reached_ml:
            if low <= ml <= high:
                self.has_reached_ml = True
            elif self.is_ascending() and close >= ml:
                self.has_reached_ml = True
            elif not self.is_ascending() and close <= ml:
                self.has_reached_ml = True

        # Track approach ratio towards ML from P2
        if not self.has_reached_ml and self.channel_width > 0:
            if self.is_ascending():
                # Started at P2 (low tine / LML), moving towards ML
                dist_traveled = close - lml
                ratio = max(0.0, min(1.0, dist_traveled / max(1e-9, self.half_width)))
            else:
                # Started at P2 (high tine / UML), moving towards ML
                dist_traveled = uml - close
                ratio = max(0.0, min(1.0, dist_traveled / max(1e-9, self.half_width)))
            if ratio > self.max_ml_approach_ratio:
                self.max_ml_approach_ratio = ratio

        # Check breach of outer boundaries
        breached_uml = close > uml
        breached_lml = close < lml

        # Hagopian Failure evaluation:
        # If price reversed before reaching ML (approached at least 15% towards ML then rolled over)
        # and now closes beyond the opposing outer tine:
        # In an ascending pitchfork: price failed to reach ML and closes below LML.
        # In a descending pitchfork: price failed to reach ML and closes above UML.
        hagopian = False
        if not self.has_reached_ml and not self.hagopian_triggered:
            if self.is_ascending() and breached_lml and self.max_ml_approach_ratio >= 0.15:
                self.hagopian_triggered = True
                hagopian = True
            elif not self.is_ascending() and breached_uml and self.max_ml_approach_ratio >= 0.15:
                self.hagopian_triggered = True
                hagopian = True

        if self.hagopian_triggered:
            status = "hagopian_failure"
        elif self.has_reached_ml:
            status = "reached_ml"
        elif breached_uml or breached_lml:
            status = "breached_boundary"
        else:
            status = "tracking"

        return PitchforkBarResult(
            bar_index=t,
            close_price=close,
            ml_value=ml,
            uml_value=uml,
            lml_value=lml,
            reached_ml=self.has_reached_ml,
            breached_uml=breached_uml,
            breached_lml=breached_lml,
            hagopian_triggered=hagopian,
            status=status,
        )


def construct_pitchfork(
    p0: PitchforkPivot,
    p1: PitchforkPivot,
    p2: PitchforkPivot,
    variant: PitchforkVariant = PitchforkVariant.STANDARD,
    auto_schiff: bool = True,
    max_slope_bars_ratio: float = 1.0,
) -> PitchforkChannel:
    """Constructs a PitchforkChannel with optional auto-switch to Modified Schiff
    if the raw standard slope is excessively steep.
    """
    pf = PitchforkChannel(p0, p1, p2, variant=variant)

    if auto_schiff and variant == PitchforkVariant.STANDARD:
        # Calculate slope magnitude normalized by channel width
        # If slope per bar exceeds channel half-width / dt, slope is steep
        dt = max(1.0, float(p2.index - p1.index))
        steepness = abs(pf.slope) * dt / max(1e-9, pf.half_width)
        if steepness > max_slope_bars_ratio:
            # Automatically promote to Modified Schiff to flatten the angle
            pf = PitchforkChannel(p0, p1, p2, variant=PitchforkVariant.MODIFIED_SCHIFF)

    return pf


def find_pivots_zigzag(
    highs: List[float],
    lows: List[float],
    lookback: int = 3,
    min_change_pct: float = 0.02,
) -> List[PitchforkPivot]:
    """Non-repainting pivot finder using local extrema with volatility/change gating.

    A pivot at index i is confirmed at index i + lookback.
    """
    n = len(highs)
    if n < lookback * 2 + 1:
        return []

    pivots: List[PitchforkPivot] = []
    last_type: Optional[bool] = None  # True for high, False for low

    for i in range(lookback, n - lookback):
        is_local_high = all(highs[i] >= highs[j] for j in range(i - lookback, i + lookback + 1) if j != i)
        is_local_low = all(lows[i] <= lows[j] for j in range(i - lookback, i + lookback + 1) if j != i)

        if is_local_high and (last_type is None or last_type is False):
            if not pivots or (highs[i] - pivots[-1].price) / max(1e-9, pivots[-1].price) >= min_change_pct:
                pivots.append(PitchforkPivot(index=i, price=highs[i], is_high=True))
                last_type = True
        elif is_local_low and (last_type is None or last_type is True):
            if not pivots or (pivots[-1].price - lows[i]) / max(1e-9, pivots[-1].price) >= min_change_pct:
                pivots.append(PitchforkPivot(index=i, price=lows[i], is_high=False))
                last_type = False

    return pivots
