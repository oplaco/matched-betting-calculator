"""
Abstract interfaces for the matched betting calculator.

This module defines interfaces that follow the Dependency Inversion Principle,
allowing different implementations to be swapped without changing client code.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from matched_betting_calculator.bet import Bet, BackLayGroup, DutchingGroup


class BetValidatorInterface(ABC):
    """Interface for bet validation strategies."""

    @abstractmethod
    def validate_bet(self, bet: Bet) -> None:
        """
        Validate a bet according to specific rules.

        Args:
            bet: The bet to validate

        Raises:
            ValidationError: If validation fails
        """
        pass

    @abstractmethod
    def validate_bet_group(self, bet_group: Any) -> None:
        """
        Validate a group of bets.

        Args:
            bet_group: The bet group to validate

        Raises:
            ValidationError: If validation fails
        """
        pass


class ResultFormatterInterface(ABC):
    """Interface for formatting calculation results."""

    @abstractmethod
    def format_results(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """
        Format calculation results according to specific rules.

        Args:
            results: Raw calculation results

        Returns:
            Formatted results
        """
        pass


class CalculationStrategyInterface(ABC):
    """Interface for calculation strategies."""

    @abstractmethod
    def calculate(self, **kwargs: Any) -> Dict[str, Any]:
        """
        Perform calculation according to strategy.

        Args:
            **kwargs: Strategy-specific parameters

        Returns:
            Calculation results
        """
        pass


class MathBackendInterface(ABC):
    """Interface for mathematical computation backends."""

    @abstractmethod
    def solve_equation(self, equation: Any, variable: str) -> Any:
        """
        Solve an equation for a specific variable.

        Args:
            equation: The equation to solve
            variable: Variable to solve for

        Returns:
            Solution expression
        """
        pass

    @abstractmethod
    def evaluate_expression(
        self, expression: Any, substitutions: Dict[str, Any]
    ) -> float:
        """
        Evaluate an expression with substitutions.

        Args:
            expression: The expression to evaluate
            substitutions: Variable substitutions

        Returns:
            Numeric result
        """
        pass


class CacheInterface(ABC):
    """Interface for caching strategies."""

    @abstractmethod
    def get(self, key: str) -> Optional[Any]:
        """
        Get a cached value.

        Args:
            key: Cache key

        Returns:
            Cached value or None if not found
        """
        pass

    @abstractmethod
    def set(self, key: str, value: Any) -> None:
        """
        Set a cached value.

        Args:
            key: Cache key
            value: Value to cache
        """
        pass

    @abstractmethod
    def clear(self) -> None:
        """Clear all cached values."""
        pass


class LoggingInterface(ABC):
    """Interface for logging strategies."""

    @abstractmethod
    def log_calculation(
        self, calculator_type: str, inputs: Dict[str, Any], results: Dict[str, Any]
    ) -> None:
        """
        Log a calculation operation.

        Args:
            calculator_type: Type of calculator used
            inputs: Input parameters
            results: Calculation results
        """
        pass

    @abstractmethod
    def log_error(self, error: Exception, context: Dict[str, Any]) -> None:
        """
        Log an error.

        Args:
            error: The exception that occurred
            context: Additional context information
        """
        pass
