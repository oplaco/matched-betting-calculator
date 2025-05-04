from abc import ABC, abstractmethod
from typing import List, Dict, Any
from matched_betting_calculator.bet import Bet

class CalculatorBase(ABC):
    @abstractmethod
    def calculate_stake(self) -> Dict[str, Any]:
        """
        Perform the strategy-specific calculation and return a dictionary with results.
        """
        pass