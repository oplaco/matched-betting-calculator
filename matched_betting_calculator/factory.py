"""
Factory for creating calculator instances.

Updated to use the Registry pattern for better extensibility
and adherence to the Open/Closed Principle.
"""

from typing import Dict, Any, List, Type, Tuple

from matched_betting_calculator.base import CalculatorBase
from matched_betting_calculator.bet import BackLayGroup, DutchingGroup
from matched_betting_calculator.errors import ConfigurationError
from matched_betting_calculator.registry import get_registry, register_calculators


class CalculatorFactory:
    """
    Factory class for creating calculator instances.

    Updated to use the Registry pattern for better extensibility
    and adherence to the Open/Closed Principle. New calculator types
    can be added without modifying this factory.
    """

    @staticmethod
    def create_back_lay_calculator(
        calculator_type: str, back_lay_group: BackLayGroup, **kwargs: Any
    ) -> CalculatorBase:
        """
        Create a back-lay strategy calculator using the registry.

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
        # Ensure calculators are registered
        register_calculators()

        registry = get_registry()

        # Get calculator class from registry
        calculator_class = registry.get_back_lay_calculator(calculator_type)

        # Get required parameters from registry
        required_params = registry.get_required_params("back_lay", calculator_type)

        # Validate required parameters
        missing_params = [
            param for param in required_params if kwargs.get(param) is None
        ]
        if missing_params:
            missing_params_str = ", ".join(missing_params)
            raise ConfigurationError(
                f"Missing required parameters for {calculator_type} calculator",
                f"Required parameters: {missing_params_str}",
            )

        # Collect all parameters and instantiate
        param_values = [kwargs[param] for param in required_params]
        return calculator_class(back_lay_group, *param_values)

    @staticmethod
    def create_dutching_calculator(
        calculator_type: str, dutching_group: DutchingGroup, **kwargs: Any
    ) -> CalculatorBase:
        """
        Create a dutching strategy calculator using the registry.

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
        # Ensure calculators are registered
        register_calculators()

        registry = get_registry()

        # Get calculator class from registry
        calculator_class = registry.get_dutching_calculator(calculator_type)

        # Get required parameters from registry
        required_params = registry.get_required_params("dutching", calculator_type)

        # Validate required parameters
        missing_params = [
            param for param in required_params if kwargs.get(param) is None
        ]
        if missing_params:
            missing_params_str = ", ".join(missing_params)
            raise ConfigurationError(
                f"Missing required parameters for {calculator_type} calculator",
                f"Required parameters: {missing_params_str}",
            )

        # Collect all parameters and instantiate
        param_values = [kwargs[param] for param in required_params]
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
        Create an accumulated calculator for multi-event bets using the registry.

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
        # Ensure calculators are registered
        register_calculators()

        registry = get_registry()

        # Get calculator class from registry
        calculator_class = registry.get_accumulated_calculator(calculator_type)

        # Get required parameters from registry
        required_params = registry.get_required_params("accumulated", calculator_type)

        # Validate required parameters
        missing_params = [
            param for param in required_params if kwargs.get(param) is None
        ]
        if missing_params:
            missing_params_str = ", ".join(missing_params)
            raise ConfigurationError(
                f"Missing required parameters for {calculator_type} calculator",
                f"Required parameters: {missing_params_str}",
            )

        # Collect all parameters and instantiate
        param_values = [kwargs[param] for param in required_params]
        return calculator_class(combo_stake, combo_fee, back_lay_groups, *param_values)
