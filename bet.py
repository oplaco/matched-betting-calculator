from dataclasses import dataclass
from typing import Optional

@dataclass
class Bet:
    odds: float
    stake: Optional[float] = None # Must be optional as the stake might need to be calculated.
    fee: float = 0.0

    def __post_init__(self):
        if self.odds < 1:
            raise ValueError("Odds must be >= 1.")
        if self.stake is not None and self.stake <= 0:
            raise ValueError("Stake must be > 0 if provided.")
        if not (0 <= self.fee <= 100):
            raise ValueError("Fee must be between 0 and 100.")
    
class BackLeyGroup:
    """Represents the Back bet - Lay Bet group used in the Back-Ley strategy.
    """
    def __init__(self,back_bet:Bet,lay_bet:Bet):
        self.back_bet = back_bet
        self.lay_bet = lay_bet
        
class DutchingGroup:
    """Represents the dutching group of n bets used in the dutching strategy.
    """
    def __init__(self,back_bets:list[Bet]):
        self.back_bets = back_bets
        
