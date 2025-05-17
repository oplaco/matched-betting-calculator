"""
Factory for creating calculator instances.
"""

from typing import Dict, Any, Union, List, Optional, Type

from matched_betting_calculator.base import CalculatorBase
from matched_betting_calculator.bet import BackLayGroup, DutchingGroup
from matched_betting_calculator.errors import ConfigurationError


class CalculatorFactory:
    """
    Factory class for creating calculator instances.

    This class provides a centralized way to create calculators based on
    bet groups and parameters, ensuring proper dependency injection.
    """

    @staticmethod
    def create_back_lay_calculator(
        calculator_type: str, back_lay_group: BackLayGroup, **kwargs: Any
    ) -> CalculatorBase:
        """
        Create a back-lay strategy calculator.

        Args:
            calculator_type: Type of calculator to create ('normal', 'freebet',
                            'reimbursement', or 'rollover')
            back_lay_group: The BackLayGroup for the calculation
            **kwargs: Additional parameters for specific calculator types

        Returns:
            An instance of the requested calculator

        Raises:
            ConfigurationError: If the calculator type is invalid or required parameters are missing
        """
        # Import here to avoid circular imports
        from matched_betting_calculator.back_lay_strategy.back_lay_simple_calculator import (
            BackLayNormalCalculator,
            BackLayFreebetCalculator,
            BackLayReimbursementCalculator,
            BackLayRolloverCalculator,
        )

        # Define a mapping from calculator type to (calculator class, required parameters)
        calculator_map = {
            "normal": (BackLayNormalCalculator, []),
            "freebet": (BackLayFreebetCalculator, []),
            "reimbursement": (BackLayReimbursementCalculator, ["reimbursement"]),
            "rollover": (
                BackLayRolloverCalculator,
                ["bonus_amount", "remaining_rollover", "expected_rating"],
            ),
        }

        # Check if the calculator type is valid
        if calculator_type not in calculator_map:
            valid_types = ", ".join(calculator_map.keys())
            raise ConfigurationError(
                f"Invalid calculator type: {calculator_type}",
                f"Valid types are: {valid_types}",
            )

        # Get calculator class and required parameters
        calculator_class, required_params = calculator_map[calculator_type]

        # Check if all required parameters are provided
        missing_params = [
            param for param in required_params if kwargs.get(param) is None
        ]
        if missing_params:
            missing_params_str = ", ".join(missing_params)
            raise ConfigurationError(
                f"Missing required parameters for {calculator_type} calculator",
                f"Required parameters: {missing_params_str}",
            )

        # Extract the needed parameters
        param_values = [kwargs[param] for param in required_params]

        # Create and return calculator instance
        return calculator_class(back_lay_group, *param_values)

    @staticmethod
    def create_dutching_calculator(
        calculator_type: str, dutching_group: DutchingGroup, **kwargs: Any
    ) -> CalculatorBase:
        """
        Create a dutching strategy calculator.

        Args:
            calculator_type: Type of calculator to create ('normal', 'freebet',
                            'reimbursement', or 'rollover')
            dutching_group: The DutchingGroup for the calculation
            **kwargs: Additional parameters for specific calculator types

        Returns:
            An instance of the requested calculator

        Raises:
            ConfigurationError: If the calculator type is invalid or required parameters are missing
        """
        # Import here to avoid circular imports
        from matched_betting_calculator.dutching_strategy.dutching_simple_calculator import (
            DutchingNormalCalculator,
            DutchingFreebetCalculator,
            DutchingReimbursementCalculator,
            DutchingRolloverCalculator,
        )

        # Define a mapping from calculator type to (calculator class, required parameters)
        calculator_map = {
            "normal": (DutchingNormalCalculator, []),
            "freebet": (DutchingFreebetCalculator, []),
            "reimbursement": (DutchingReimbursementCalculator, ["reimbursement"]),
            "rollover": (
                DutchingRolloverCalculator,
                ["bonus_amount", "remaining_rollover", "expected_rating"],
            ),
        }

        # Check if the calculator type is valid
        if calculator_type not in calculator_map:
            valid_types = ", ".join(calculator_map.keys())
            raise ConfigurationError(
                f"Invalid calculator type: {calculator_type}",
                f"Valid types are: {valid_types}",
            )

        # Get calculator class and required parameters
        calculator_class, required_params = calculator_map[calculator_type]

        # Check if all required parameters are provided
        missing_params = [
            param for param in required_params if kwargs.get(param) is None
        ]
        if missing_params:
            missing_params_str = ", ".join(missing_params)
            raise ConfigurationError(
                f"Missing required parameters for {calculator_type} calculator",
                f"Required parameters: {missing_params_str}",
            )

        # Extract the needed parameters
        param_values = [kwargs[param] for param in required_params]

        # Create and return calculator instance
        return calculator_class(dutching_group, *param_values)

    @staticmethod
    def create_accumulated_calculator(
        calculator_type: str,
        combo_stake: float,
        combo_fee: float,
        back_lay_groups: List[BackLayGroup],
        **kwargs: Any,
    ) -> CalculatorBase:
        """
        Create an accumulated calculator for multi-event bets.

        Args:
            calculator_type: Type of calculator to create ('normal', 'freebet', 'reimbursement')
            combo_stake: The stake for the accumulated bet
            combo_fee: The fee percentage for the accumulated bet
            back_lay_groups: List of BackLayGroups for each leg of the accumulator
            **kwargs: Additional parameters for specific calculator types

        Returns:
            An instance of the requested calculator

        Raises:
            ConfigurationError: If the calculator type is invalid or required parameters are missing
        """
        # Import here to avoid circular imports
        from matched_betting_calculator.back_lay_strategy.back_lay_accumulated_calculator import (
            BackLayAccumulatedNormalCalculator,
            BackLayAccumulatedFreebetCalculator,
            BackLayAccumulatedReimbursementCalculator,
        )

        # Define a mapping from calculator type to (calculator class, required parameters)
        calculator_map = {
            "normal": (BackLayAccumulatedNormalCalculator, []),
            "freebet": (BackLayAccumulatedFreebetCalculator, []),
            "reimbursement": (
                BackLayAccumulatedReimbursementCalculator,
                ["reimbursement"],
            ),
        }

        # Check if the calculator type is valid
        if calculator_type not in calculator_map:
            valid_types = ", ".join(calculator_map.keys())
            raise ConfigurationError(
                f"Invalid calculator type: {calculator_type}",
                f"Valid types are: {valid_types}",
            )

        # Get calculator class and required parameters
        calculator_class, required_params = calculator_map[calculator_type]

        # Check if all required parameters are provided
        missing_params = [
            param for param in required_params if kwargs.get(param) is None
        ]
        if missing_params:
            missing_params_str = ", ".join(missing_params)
            raise ConfigurationError(
                f"Missing required parameters for {calculator_type} calculator",
                f"Required parameters: {missing_params_str}",
            )

        # Extract the needed parameters
        param_values = [kwargs[param] for param in required_params]

        # Create and return calculator instance with common parameters
        return calculator_class(combo_stake, combo_fee, back_lay_groups, *param_values)
