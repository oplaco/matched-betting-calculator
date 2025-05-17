from abc import ABC, abstractmethod
from typing import Dict, Any
from matched_betting_calculator.constants import PercentageConstants
from matched_betting_calculator.errors import MatchedBettingError


class CalculatorBase(ABC):
    """
    Base abstract class for all matched betting calculators.

    Each calculator must implement a calculate_stake method that performs
    the strategy-specific calculation and returns a dictionary with results.
    """

    @abstractmethod
    def calculate_stake(self) -> Dict[str, Any]:
        """
        Perform the strategy-specific calculation and return a dictionary with results.

        Returns:
            A dictionary containing the calculated stake values and other relevant data

        Raises:
            MatchedBettingError: If the calculation cannot be performed
        """
        pass

    def _format_results(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """
        Format the calculation results into a standard format.

        Args:
            results: Raw calculation results

        Returns:
            Formatted results with proper rounding applied
        """
        return {
            key: (
                round(value, PercentageConstants.DECIMAL_PLACES)
                if isinstance(value, (int, float))
                else value
            )
            for key, value in results.items()
        }
