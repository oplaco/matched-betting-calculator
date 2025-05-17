"""
Custom exceptions for the matched betting calculator.
"""

from typing import Optional


class MatchedBettingError(Exception):
    """Base exception class for all matched betting calculator errors."""

    def __init__(self, message: str, details: Optional[str] = None):
        """
        Initialize a matched betting error.

        Args:
            message: A concise error message
            details: Optional additional details about the error context
        """
        self.details = details
        super().__init__(message)


class ValidationError(MatchedBettingError):
    """Exception raised for input validation errors."""

    pass


class CalculationError(MatchedBettingError):
    """Exception raised when a calculation cannot be performed."""

    pass


class ConfigurationError(MatchedBettingError):
    """Exception raised when the calculator is improperly configured."""

    pass
