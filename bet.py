from dataclasses import dataclass
from typing import Optional

@dataclass
class Bet:
    odds: float
    stake: Optional[float] = None
    fee: float = 0.0

    def __post_init__(self):
        if self.odds < 1:
            raise ValueError("Odds must be >= 1.")
        if self.stake is not None and self.stake <= 0:
            raise ValueError("Stake must be > 0 if provided.")
        if not (0 <= self.fee <= 100):
            raise ValueError("Fee must be between 0 and 100.")
