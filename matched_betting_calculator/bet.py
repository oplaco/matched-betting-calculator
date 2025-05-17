from dataclasses import dataclass
from typing import Optional, List
from matched_betting_calculator.errors import ValidationError


@dataclass
class Bet:
    """
    Represents a bet with odds, optional stake, and fee percentage.

    Attributes:
        odds: The odds of the bet (must be >= 1)
        stake: The stake amount (optional, can be calculated later)
        fee: The fee percentage (0-100)
    """

    odds: float
    stake: Optional[float] = None  # Optional as the stake might need to be calculated
    fee: float = 0.0

    def __post_init__(self) -> None:
        """
        Validate the bet parameters.

        Raises:
            ValidationError: If any parameter is invalid
        """
        if self.odds < 1:
            raise ValidationError(
                "Odds must be greater than or equal to 1", f"Provided odds: {self.odds}"
            )

        if self.stake is not None and self.stake <= 0:
            raise ValidationError(
                "Stake must be greater than 0 if provided",
                f"Provided stake: {self.stake}",
            )

        if not (0 <= self.fee <= 100):
            raise ValidationError(
                "Fee must be between 0 and 100", f"Provided fee: {self.fee}"
            )


class BackLayGroup:
    """
    Represents a Back bet - Lay Bet group used in the Back-Lay strategy.
    """

    def __init__(self, back_bet: Bet, lay_bet: Bet) -> None:
        """
        Initialize a back-lay group.

        Args:
            back_bet: The back bet
            lay_bet: The lay bet
        """
        self.back_bet = back_bet
        self.lay_bet = lay_bet


class DutchingGroup:
    """
    Represents a dutching group consisting of a main back bet and
    a group of bets used in the dutching strategy to hedge the main one.
    """

    def __init__(self, back_bet: Bet, dutching_bets: List[Bet]) -> None:
        """
        Initialize a dutching group.

        Args:
            back_bet: The main back bet
            dutching_bets: List of dutching bets used to hedge the main bet
        """
        self.back_bet = back_bet
        self.dutching_bets = dutching_bets
