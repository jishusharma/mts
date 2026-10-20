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

        # Identify which tine P2 originated from (invariant to pitchfork variant or inversion)
        self.p2_is_lower = (self.offset_p2 <= 0.0)

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
            elif self.p2_is_lower and (close >= ml or high >= ml):
                self.has_reached_ml = True
            elif not self.p2_is_lower and (close <= ml or low <= ml):
                self.has_reached_ml = True

        # Track approach ratio towards ML from P2 tine
        if not self.has_reached_ml and self.channel_width > 0:
            if self.p2_is_lower:
                # Started at P2 (lower tine / LML), moving upwards towards ML
                dist_traveled = close - lml
                ratio = max(0.0, min(1.0, dist_traveled / max(1e-9, self.half_width)))
            else:
                # Started at P2 (upper tine / UML), moving downwards towards ML
                dist_traveled = uml - close
                ratio = max(0.0, min(1.0, dist_traveled / max(1e-9, self.half_width)))
            if ratio > self.max_ml_approach_ratio:
                self.max_ml_approach_ratio = ratio

        # Check breach of outer boundaries
        breached_uml = close > uml
        breached_lml = close < lml

        # Hagopian Failure evaluation:
        # If price reversed before reaching ML (approached at least 15% towards ML then rolled over)
        # and closes beyond the tine it originated from (P2 tine):
        # - If P2 originated on lower tine: price fails to reach ML and closes below LML.
        # - If P2 originated on upper tine: price fails to reach ML and closes above UML.
        hagopian = False
        if not self.has_reached_ml and not self.hagopian_triggered:
            if self.p2_is_lower and breached_lml and self.max_ml_approach_ratio >= 0.15:
                self.hagopian_triggered = True
                hagopian = True
            elif not self.p2_is_lower and breached_uml and self.max_ml_approach_ratio >= 0.15:
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


class LogPitchforkChannel:
    """Wrapper that evaluates a PitchforkChannel in log space (ln(price)).

    Eliminates linear slope collapse and distortion across multi-year Bitcoin expansions.
    Internal geometry operates on ln(price); query methods return exponentiated dollar levels.
    """

    def __init__(
        self,
        p0: PitchforkPivot,
        p1: PitchforkPivot,
        p2: PitchforkPivot,
        variant: PitchforkVariant = PitchforkVariant.STANDARD,
    ):
        p0_log = PitchforkPivot(index=p0.index, price=math.log(max(1e-9, p0.price)), is_high=p0.is_high, timestamp=p0.timestamp)
        p1_log = PitchforkPivot(index=p1.index, price=math.log(max(1e-9, p1.price)), is_high=p1.is_high, timestamp=p1.timestamp)
        p2_log = PitchforkPivot(index=p2.index, price=math.log(max(1e-9, p2.price)), is_high=p2.is_high, timestamp=p2.timestamp)

        self._inner = PitchforkChannel(p0_log, p1_log, p2_log, variant=variant)
        self.variant = variant
        self.slope_log = self._inner.slope
        self.channel_width_pct = math.exp(self._inner.channel_width) - 1.0

    def get_ml(self, t: float) -> float:
        return math.exp(self._inner.get_ml(t))

    def get_uml(self, t: float) -> float:
        return math.exp(self._inner.get_uml(t))

    def get_lml(self, t: float) -> float:
        return math.exp(self._inner.get_lml(t))

    def get_upper_warning_line(self, t: float, level: int = 1) -> float:
        return math.exp(self._inner.get_upper_warning_line(t, level=level))

    def get_lower_warning_line(self, t: float, level: int = 1) -> float:
        return math.exp(self._inner.get_lower_warning_line(t, level=level))

    def get_upper_quarter_line(self, t: float) -> float:
        return math.exp(self._inner.get_upper_quarter_line(t))

    def get_lower_quarter_line(self, t: float) -> float:
        return math.exp(self._inner.get_lower_quarter_line(t))

    def is_ascending(self) -> bool:
        return self._inner.is_ascending()

    @property
    def has_reached_ml(self) -> bool:
        return self._inner.has_reached_ml

    @property
    def hagopian_triggered(self) -> bool:
        return self._inner.hagopian_triggered

    def eval_bar(self, t: int, high: float, low: float, close: float) -> PitchforkBarResult:
        res = self._inner.eval_bar(
            t,
            high=math.log(max(1e-9, high)),
            low=math.log(max(1e-9, low)),
            close=math.log(max(1e-9, close)),
        )
        return PitchforkBarResult(
            bar_index=t,
            close_price=close,
            ml_value=math.exp(res.ml_value),
            uml_value=math.exp(res.uml_value),
            lml_value=math.exp(res.lml_value),
            reached_ml=res.reached_ml,
            breached_uml=res.breached_uml,
            breached_lml=res.breached_lml,
            hagopian_triggered=res.hagopian_triggered,
            status=res.status,
        )


def construct_pitchfork(
    p0: PitchforkPivot,
    p1: PitchforkPivot,
    p2: PitchforkPivot,
    variant: PitchforkVariant = PitchforkVariant.STANDARD,
    auto_schiff: bool = True,
    max_slope_bars_ratio: float = 1.0,
    log_scale: bool = False,
) -> Any:
    """Constructs a PitchforkChannel (or LogPitchforkChannel) with optional auto-switch
    to Modified Schiff if the raw standard slope is excessively steep.
    """
    if log_scale:
        return LogPitchforkChannel(p0, p1, p2, variant=variant)

    pf = PitchforkChannel(p0, p1, p2, variant=variant)

    if auto_schiff and variant == PitchforkVariant.STANDARD:
        dt = max(1.0, float(p2.index - p1.index))
        steepness = abs(pf.slope) * dt / max(1e-9, pf.half_width)
        if steepness > max_slope_bars_ratio:
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
    Accurately tracks extending legs by updating peaks/troughs until reversal gating triggers.
    """
    n = len(highs)
    if n < lookback * 2 + 1:
        return []

    pivots: List[PitchforkPivot] = []
    last_type: Optional[bool] = None  # True for high, False for low

    for i in range(lookback, n - lookback):
        is_local_high = all(highs[i] >= highs[j] for j in range(i - lookback, i + lookback + 1) if j != i)
        is_local_low = all(lows[i] <= lows[j] for j in range(i - lookback, i + lookback + 1) if j != i)

        if last_type is None:
            if is_local_high:
                pivots.append(PitchforkPivot(index=i, price=highs[i], is_high=True))
                last_type = True
            elif is_local_low:
                pivots.append(PitchforkPivot(index=i, price=lows[i], is_high=False))
                last_type = False
        elif last_type is True:
            # Currently tracking an upswing / swing high
            if is_local_high and highs[i] > pivots[-1].price:
                # Higher high extends current swing high
                pivots[-1] = PitchforkPivot(index=i, price=highs[i], is_high=True)
            elif is_local_low and (pivots[-1].price - lows[i]) / max(1e-9, pivots[-1].price) >= min_change_pct:
                # Confirmed reversal to swing low
                pivots.append(PitchforkPivot(index=i, price=lows[i], is_high=False))
                last_type = False
        elif last_type is False:
            # Currently tracking a downswing / swing low
            if is_local_low and lows[i] < pivots[-1].price:
                # Lower low extends current swing low
                pivots[-1] = PitchforkPivot(index=i, price=lows[i], is_high=False)
            elif is_local_high and (highs[i] - pivots[-1].price) / max(1e-9, pivots[-1].price) >= min_change_pct:
                # Confirmed reversal to swing high
                pivots.append(PitchforkPivot(index=i, price=highs[i], is_high=True))
                last_type = True

    return pivots
