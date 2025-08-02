"""
Calculator registry for the matched betting calculator.

This module implements the registry pattern to improve extensibility
and adherence to the Open/Closed Principle. New calculator types can
be registered without modifying existing code.
"""

from typing import Dict, Type, List, Callable, Any
from matched_betting_calculator.base import CalculatorBase
from matched_betting_calculator.errors import ConfigurationError


class CalculatorRegistry:
    """
    Registry for calculator types supporting multiple strategies.

    This class implements the Registry pattern to allow dynamic registration
    of calculator types without modifying existing code, following the
    Open/Closed Principle.
    """

    def __init__(self):
        """Initialize empty registries for each strategy type."""
        self._back_lay_calculators: Dict[str, Type[CalculatorBase]] = {}
        self._dutching_calculators: Dict[str, Type[CalculatorBase]] = {}
        self._accumulated_calculators: Dict[str, Type[CalculatorBase]] = {}

        # Store required parameters for each calculator type
        self._back_lay_params: Dict[str, List[str]] = {}
        self._dutching_params: Dict[str, List[str]] = {}
        self._accumulated_params: Dict[str, List[str]] = {}

    def register_back_lay_calculator(
        self,
        calculator_type: str,
        calculator_class: Type[CalculatorBase],
        required_params: List[str] = None,
    ) -> None:
        """
        Register a back-lay calculator type.

        Args:
            calculator_type: String identifier for the calculator type
            calculator_class: The calculator class to register
            required_params: List of required parameter names for this calculator

        Raises:
            ConfigurationError: If calculator_type is already registered
        """
        if calculator_type in self._back_lay_calculators:
            raise ConfigurationError(
                f"Back-lay calculator type '{calculator_type}' already registered",
                f"Existing class: {self._back_lay_calculators[calculator_type].__name__}",
            )

        self._back_lay_calculators[calculator_type] = calculator_class
        self._back_lay_params[calculator_type] = required_params or []

    def register_dutching_calculator(
        self,
        calculator_type: str,
        calculator_class: Type[CalculatorBase],
        required_params: List[str] = None,
    ) -> None:
        """
        Register a dutching calculator type.

        Args:
            calculator_type: String identifier for the calculator type
            calculator_class: The calculator class to register
            required_params: List of required parameter names for this calculator

        Raises:
            ConfigurationError: If calculator_type is already registered
        """
        if calculator_type in self._dutching_calculators:
            raise ConfigurationError(
                f"Dutching calculator type '{calculator_type}' already registered",
                f"Existing class: {self._dutching_calculators[calculator_type].__name__}",
            )

        self._dutching_calculators[calculator_type] = calculator_class
        self._dutching_params[calculator_type] = required_params or []

    def register_accumulated_calculator(
        self,
        calculator_type: str,
        calculator_class: Type[CalculatorBase],
        required_params: List[str] = None,
    ) -> None:
        """
        Register an accumulated calculator type.

        Args:
            calculator_type: String identifier for the calculator type
            calculator_class: The calculator class to register
            required_params: List of required parameter names for this calculator

        Raises:
            ConfigurationError: If calculator_type is already registered
        """
        if calculator_type in self._accumulated_calculators:
            raise ConfigurationError(
                f"Accumulated calculator type '{calculator_type}' already registered",
                f"Existing class: {self._accumulated_calculators[calculator_type].__name__}",
            )

        self._accumulated_calculators[calculator_type] = calculator_class
        self._accumulated_params[calculator_type] = required_params or []

    def get_back_lay_calculator(self, calculator_type: str) -> Type[CalculatorBase]:
        """
        Get a registered back-lay calculator class.

        Args:
            calculator_type: String identifier for the calculator type

        Returns:
            The registered calculator class

        Raises:
            ConfigurationError: If calculator_type is not registered
        """
        if calculator_type not in self._back_lay_calculators:
            valid_types = ", ".join(self._back_lay_calculators.keys())
            raise ConfigurationError(
                f"Back-lay calculator type '{calculator_type}' not registered",
                f"Valid types: {valid_types}",
            )

        return self._back_lay_calculators[calculator_type]

    def get_dutching_calculator(self, calculator_type: str) -> Type[CalculatorBase]:
        """
        Get a registered dutching calculator class.

        Args:
            calculator_type: String identifier for the calculator type

        Returns:
            The registered calculator class

        Raises:
            ConfigurationError: If calculator_type is not registered
        """
        if calculator_type not in self._dutching_calculators:
            valid_types = ", ".join(self._dutching_calculators.keys())
            raise ConfigurationError(
                f"Dutching calculator type '{calculator_type}' not registered",
                f"Valid types: {valid_types}",
            )

        return self._dutching_calculators[calculator_type]

    def get_accumulated_calculator(self, calculator_type: str) -> Type[CalculatorBase]:
        """
        Get a registered accumulated calculator class.

        Args:
            calculator_type: String identifier for the calculator type

        Returns:
            The registered calculator class

        Raises:
            ConfigurationError: If calculator_type is not registered
        """
        if calculator_type not in self._accumulated_calculators:
            valid_types = ", ".join(self._accumulated_calculators.keys())
            raise ConfigurationError(
                f"Accumulated calculator type '{calculator_type}' not registered",
                f"Valid types: {valid_types}",
            )

        return self._accumulated_calculators[calculator_type]

    def get_required_params(self, strategy: str, calculator_type: str) -> List[str]:
        """
        Get required parameters for a calculator type and strategy.

        Args:
            strategy: Strategy type ('back_lay', 'dutching', or 'accumulated')
            calculator_type: String identifier for the calculator type

        Returns:
            List of required parameter names

        Raises:
            ConfigurationError: If strategy or calculator_type is invalid
        """
        if strategy == "back_lay":
            if calculator_type not in self._back_lay_params:
                raise ConfigurationError(
                    f"Back-lay calculator type '{calculator_type}' not registered"
                )
            return self._back_lay_params[calculator_type]
        elif strategy == "dutching":
            if calculator_type not in self._dutching_params:
                raise ConfigurationError(
                    f"Dutching calculator type '{calculator_type}' not registered"
                )
            return self._dutching_params[calculator_type]
        elif strategy == "accumulated":
            if calculator_type not in self._accumulated_params:
                raise ConfigurationError(
                    f"Accumulated calculator type '{calculator_type}' not registered"
                )
            return self._accumulated_params[calculator_type]
        else:
            raise ConfigurationError(
                f"Invalid strategy type: {strategy}",
                "Valid strategies: back_lay, dutching, accumulated",
            )

    def list_available_calculators(self) -> Dict[str, List[str]]:
        """
        List all available calculator types by strategy.

        Returns:
            Dictionary mapping strategy names to lists of calculator types
        """
        return {
            "back_lay": list(self._back_lay_calculators.keys()),
            "dutching": list(self._dutching_calculators.keys()),
            "accumulated": list(self._accumulated_calculators.keys()),
        }


# Global registry instance
_registry = CalculatorRegistry()


def get_registry() -> CalculatorRegistry:
    """
    Get the global calculator registry instance.

    Returns:
        The global CalculatorRegistry instance
    """
    return _registry


# Global flag to track if calculators are registered
_calculators_registered = False


def register_calculators() -> None:
    """
    Register all built-in calculator types.

    This function is called once to populate the registry with
    all standard calculator implementations. It's idempotent -
    calling it multiple times won't cause errors.
    """
    global _calculators_registered

    if _calculators_registered:
        return  # Already registered, skip

    # Import here to avoid circular imports
    from matched_betting_calculator.back_lay_strategy.back_lay_simple_calculator import (
        BackLayNormalCalculator,
        BackLayFreebetCalculator,
        BackLayReimbursementCalculator,
        BackLayRolloverCalculator,
    )
    from matched_betting_calculator.dutching_strategy.dutching_simple_calculator import (
        DutchingNormalCalculator,
        DutchingFreebetCalculator,
        DutchingReimbursementCalculator,
        DutchingRolloverCalculator,
    )
    from matched_betting_calculator.back_lay_strategy.back_lay_accumulated_calculator import (
        BackLayAccumulatedNormalCalculator,
        BackLayAccumulatedFreebetCalculator,
        BackLayAccumulatedReimbursementCalculator,
    )

    registry = get_registry()

    # Register back-lay calculators
    registry.register_back_lay_calculator("normal", BackLayNormalCalculator)
    registry.register_back_lay_calculator("freebet", BackLayFreebetCalculator)
    registry.register_back_lay_calculator(
        "reimbursement", BackLayReimbursementCalculator, ["reimbursement"]
    )
    registry.register_back_lay_calculator(
        "rollover",
        BackLayRolloverCalculator,
        ["bonus_amount", "remaining_rollover", "expected_rating"],
    )

    # Register dutching calculators
    registry.register_dutching_calculator("normal", DutchingNormalCalculator)
    registry.register_dutching_calculator("freebet", DutchingFreebetCalculator)
    registry.register_dutching_calculator(
        "reimbursement", DutchingReimbursementCalculator, ["reimbursement"]
    )
    registry.register_dutching_calculator(
        "rollover",
        DutchingRolloverCalculator,
        ["bonus_amount", "remaining_rollover", "expected_rating"],
    )

    # Register accumulated calculators
    registry.register_accumulated_calculator(
        "normal", BackLayAccumulatedNormalCalculator
    )
    registry.register_accumulated_calculator(
        "freebet", BackLayAccumulatedFreebetCalculator
    )
    registry.register_accumulated_calculator(
        "reimbursement", BackLayAccumulatedReimbursementCalculator, ["reimbursement"]
    )

    _calculators_registered = True
