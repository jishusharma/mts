"""Standard schema definitions for external analyst signals and call ledgers.

Labeling of numbers:
- All formula ratios and risk calculations: OURS
- Fee structures: SOURCED (MyTradingSys/backtest/layers/FORMULAS.md:s17)
"""
from dataclasses import dataclass, field, asdict
from enum import Enum
from typing import List, Optional, Dict, Any
import json
import re


class SignalDirection(str, Enum):
    LONG = "LONG"
    SHORT = "SHORT"


class SignalStatus(str, Enum):
    PENDING = "PENDING"
    NOT_FILLED = "NOT_FILLED"
    FILLED = "FILLED"
    STOPPED = "STOPPED"
    TARGET_HIT = "TARGET_HIT"
    TIMEOUT = "TIMEOUT"
    INVALIDATED = "INVALIDATED"


class ImbalanceConstruct(str, Enum):
    VOLUME_ABSORPTION = "VOLUME_ABSORPTION"      # Habib / Roman Trading (Construct 1)
    FVG_DISPLACEMENT = "FVG_DISPLACEMENT"        # Crypto Chase / Justin Bennett / TTrades (Construct 2)
    FOOTPRINT_ORDERFLOW = "FOOTPRINT_ORDERFLOW"  # TradingRiot / ByzGeneral (Construct 3)
    VOLUME_PROFILE_DEV = "VOLUME_PROFILE_DEV"    # Trader XO (Construct 4)
    S_R_LIQUIDITY_TRAP = "S_R_LIQUIDITY_TRAP"    # RLinda (Construct 4)


@dataclass
class AnalystSignal:
    call_id: str
    analyst: str
    source_platform: str
    source_url: str
    published_utc: str
    symbol: str
    direction: SignalDirection
    imbalance_construct: ImbalanceConstruct
    entry_price: float
    stop_loss: float
    targets: List[float]
    invalidation_condition: Optional[str] = None
    notes: Optional[str] = None
    status: SignalStatus = SignalStatus.PENDING

    def __post_init__(self):
        if self.entry_price <= 0:
            raise ValueError(f"entry_price must be > 0, got {self.entry_price}")
        if self.stop_loss <= 0:
            raise ValueError(f"stop_loss must be > 0, got {self.stop_loss}")
        if not self.targets:
            raise ValueError("targets list cannot be empty")
        for t in self.targets:
            if t <= 0:
                raise ValueError(f"target price must be > 0, got {t}")

        # Price geometry validation (OURS)
        if self.direction == SignalDirection.LONG:
            if self.stop_loss >= self.entry_price:
                raise ValueError(
                    f"For LONG, stop_loss ({self.stop_loss}) must be below entry_price ({self.entry_price})"
                )
            if any(t <= self.entry_price for t in self.targets):
                raise ValueError(
                    f"For LONG, all targets must be above entry_price ({self.entry_price})"
                )
        elif self.direction == SignalDirection.SHORT:
            if self.stop_loss <= self.entry_price:
                raise ValueError(
                    f"For SHORT, stop_loss ({self.stop_loss}) must be above entry_price ({self.entry_price})"
                )
            if any(t >= self.entry_price for t in self.targets):
                raise ValueError(
                    f"For SHORT, all targets must be below entry_price ({self.entry_price})"
                )

    @property
    def risk_amount(self) -> float:
        """Absolute dollar risk per unit (OURS)."""
        return abs(self.entry_price - self.stop_loss)

    @property
    def risk_reward_t1(self) -> float:
        """Reward to risk ratio targeting first take profit (OURS)."""
        reward = abs(self.targets[0] - self.entry_price)
        return reward / self.risk_amount if self.risk_amount > 0 else 0.0

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        d["direction"] = self.direction.value
        d["imbalance_construct"] = self.imbalance_construct.value
        d["status"] = self.status.value
        d["risk_amount"] = self.risk_amount
        d["risk_reward_t1"] = self.risk_reward_t1
        return d


@dataclass
class AnalystCallLedgerRow:
    call_id: str
    published_utc: str
    analyst: str
    platform: str
    symbol: str
    direction: str
    imbalance_construct: str
    entry: float
    stop: float
    targets_str: str
    status: str
    source_url: str
    exit_price: Optional[float] = None
    net_r: Optional[float] = None
    return_pct: Optional[float] = None
    notes: str = ""

    def to_csv_row(self) -> List[str]:
        return [
            self.call_id,
            self.published_utc,
            self.analyst,
            self.platform,
            self.symbol,
            self.direction,
            self.imbalance_construct,
            str(self.entry),
            str(self.stop),
            self.targets_str,
            self.status,
            self.source_url,
            str(self.exit_price) if self.exit_price is not None else "",
            f"{self.net_r:.3f}" if self.net_r is not None else "",
            f"{self.return_pct:.4f}" if self.return_pct is not None else "",
            self.notes,
        ]
