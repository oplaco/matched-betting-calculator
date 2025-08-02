"""
Comprehensive tests for error handling across the matched betting calculator.

This module tests error conditions that were previously untested,
improving overall test coverage and reliability.
"""

import unittest
from matched_betting_calculator.bet import Bet, BackLayGroup, DutchingGroup
from matched_betting_calculator.factory import CalculatorFactory
from matched_betting_calculator.utils import SymbolicMathHelper
from matched_betting_calculator.registry import get_registry, register_calculators
from matched_betting_calculator.errors import (
    ValidationError,
    CalculationError,
    ConfigurationError,
    MatchedBettingError,
)
import sympy as sp


class TestValidationErrors(unittest.TestCase):
    """Test validation error scenarios."""

    def test_bet_negative_odds(self):
        """Test that negative odds raise ValidationError."""
        with self.assertRaises(ValidationError) as context:
            Bet(odds=-1.5, stake=100)

        self.assertIn("Odds must be greater than or equal to 1", str(context.exception))

    def test_bet_zero_odds(self):
        """Test that zero odds raise ValidationError."""
        with self.assertRaises(ValidationError) as context:
            Bet(odds=0, stake=100)

        self.assertIn("Odds must be greater than or equal to 1", str(context.exception))

    def test_bet_negative_stake(self):
        """Test that negative stake raises ValidationError."""
        with self.assertRaises(ValidationError) as context:
            Bet(odds=2.0, stake=-10)

        self.assertIn("Stake must be greater than 0", str(context.exception))

    def test_bet_zero_stake(self):
        """Test that zero stake raises ValidationError."""
        with self.assertRaises(ValidationError) as context:
            Bet(odds=2.0, stake=0)

        self.assertIn("Stake must be greater than 0", str(context.exception))

    def test_bet_invalid_fee_negative(self):
        """Test that negative fee raises ValidationError."""
        with self.assertRaises(ValidationError) as context:
            Bet(odds=2.0, stake=100, fee=-5)

        self.assertIn("Fee must be between 0 and 100", str(context.exception))

    def test_bet_invalid_fee_over_100(self):
        """Test that fee over 100 raises ValidationError."""
        with self.assertRaises(ValidationError) as context:
            Bet(odds=2.0, stake=100, fee=150)

        self.assertIn("Fee must be between 0 and 100", str(context.exception))

    def test_reimbursement_negative_value(self):
        """Test that negative reimbursement raises ValidationError."""
        back_bet = Bet(odds=2.0, stake=100, fee=5)
        lay_bet = Bet(odds=2.1, fee=2)
        back_lay_group = BackLayGroup(back_bet, lay_bet)

        with self.assertRaises(ValidationError) as context:
            CalculatorFactory.create_back_lay_calculator(
                "reimbursement", back_lay_group, reimbursement=-10
            )

        self.assertIn("Reimbursement must be non-negative", str(context.exception))

    def test_reimbursement_exceeds_stake(self):
        """Test that reimbursement exceeding stake raises ValidationError."""
        back_bet = Bet(odds=2.0, stake=100, fee=5)
        lay_bet = Bet(odds=2.1, fee=2)
        back_lay_group = BackLayGroup(back_bet, lay_bet)

        with self.assertRaises(ValidationError) as context:
            CalculatorFactory.create_back_lay_calculator(
                "reimbursement", back_lay_group, reimbursement=150
            )

        self.assertIn(
            "Reimbursement cannot exceed the original back bet stake",
            str(context.exception),
        )

    def test_rollover_invalid_expected_rating_negative(self):
        """Test that negative expected rating raises ValidationError."""
        back_bet = Bet(odds=2.0, stake=100, fee=5)
        lay_bet = Bet(odds=2.1, fee=2)
        back_lay_group = BackLayGroup(back_bet, lay_bet)

        with self.assertRaises(ValidationError) as context:
            CalculatorFactory.create_back_lay_calculator(
                "rollover",
                back_lay_group,
                bonus_amount=50,
                remaining_rollover=200,
                expected_rating=-5,
            )

        self.assertIn(
            "Expected rating must be between 0 and 100", str(context.exception)
        )

    def test_rollover_invalid_expected_rating_over_100(self):
        """Test that expected rating over 100 raises ValidationError."""
        back_bet = Bet(odds=2.0, stake=100, fee=5)
        lay_bet = Bet(odds=2.1, fee=2)
        back_lay_group = BackLayGroup(back_bet, lay_bet)

        with self.assertRaises(ValidationError) as context:
            CalculatorFactory.create_back_lay_calculator(
                "rollover",
                back_lay_group,
                bonus_amount=50,
                remaining_rollover=200,
                expected_rating=110,
            )

        self.assertIn(
            "Expected rating must be between 0 and 100", str(context.exception)
        )


class TestConfigurationErrors(unittest.TestCase):
    """Test configuration error scenarios."""

    def test_invalid_calculator_type_back_lay(self):
        """Test that invalid back-lay calculator type raises ConfigurationError."""
        back_bet = Bet(odds=2.0, stake=100, fee=5)
        lay_bet = Bet(odds=2.1, fee=2)
        back_lay_group = BackLayGroup(back_bet, lay_bet)

        with self.assertRaises(ConfigurationError) as context:
            CalculatorFactory.create_back_lay_calculator("invalid_type", back_lay_group)

        self.assertIn(
            "Back-lay calculator type 'invalid_type' not registered",
            str(context.exception),
        )

    def test_invalid_calculator_type_dutching(self):
        """Test that invalid dutching calculator type raises ConfigurationError."""
        back_bet = Bet(odds=2.0, stake=100, fee=5)
        dutch_bet1 = Bet(odds=2.1, fee=2)
        dutch_bet2 = Bet(odds=2.2, fee=3)
        dutching_group = DutchingGroup(back_bet, [dutch_bet1, dutch_bet2])

        with self.assertRaises(ConfigurationError) as context:
            CalculatorFactory.create_dutching_calculator("invalid_type", dutching_group)

        self.assertIn(
            "Dutching calculator type 'invalid_type' not registered",
            str(context.exception),
        )

    def test_missing_required_parameters(self):
        """Test that missing required parameters raises ConfigurationError."""
        back_bet = Bet(odds=2.0, stake=100, fee=5)
        lay_bet = Bet(odds=2.1, fee=2)
        back_lay_group = BackLayGroup(back_bet, lay_bet)

        with self.assertRaises(ConfigurationError) as context:
            CalculatorFactory.create_back_lay_calculator(
                "reimbursement",
                back_lay_group,
                # Missing reimbursement parameter
            )

        self.assertIn("Missing required parameters", str(context.exception))
        self.assertIn("reimbursement", str(context.exception))


class TestCalculationErrors(unittest.TestCase):
    """Test calculation error scenarios."""

    def test_symbolic_math_helper_no_solution(self):
        """Test that SymbolicMathHelper handles no solution case."""
        # Create an equation with no solution
        x = sp.Symbol("x")
        impossible_equation = sp.Eq(x + 1, x)

        with self.assertRaises(MatchedBettingError) as context:
            SymbolicMathHelper.solve_equation(impossible_equation, x)

        self.assertIn("No solution found", str(context.exception))

    def test_symbolic_math_helper_system_no_solution(self):
        """Test that SymbolicMathHelper handles system with no solution."""
        # Create a system of equations with no solution
        x, y = sp.symbols("x y")
        equations = [x + y - 1, x + y - 2]  # Contradictory equations

        with self.assertRaises(MatchedBettingError) as context:
            SymbolicMathHelper.solve_equation_system(equations, (x, y))

        self.assertIn("No solution found", str(context.exception))


class TestRegistryErrors(unittest.TestCase):
    """Test registry error scenarios."""

    def setUp(self):
        """Set up test fixtures."""
        # Get a fresh registry for each test
        self.registry = get_registry()

    def test_double_registration_back_lay(self):
        """Test that double registration raises ConfigurationError."""
        from matched_betting_calculator.back_lay_strategy.back_lay_simple_calculator import (
            BackLayNormalCalculator,
        )

        # First registration should work
        self.registry.register_back_lay_calculator(
            "test_normal", BackLayNormalCalculator
        )

        # Second registration should fail
        with self.assertRaises(ConfigurationError) as context:
            self.registry.register_back_lay_calculator(
                "test_normal", BackLayNormalCalculator
            )

        self.assertIn("already registered", str(context.exception))

    def test_get_nonexistent_calculator(self):
        """Test that getting non-existent calculator raises ConfigurationError."""
        register_calculators()

        with self.assertRaises(ConfigurationError) as context:
            self.registry.get_back_lay_calculator("nonexistent")

        self.assertIn("not registered", str(context.exception))

    def test_get_required_params_invalid_strategy(self):
        """Test that invalid strategy raises ConfigurationError."""
        register_calculators()

        with self.assertRaises(ConfigurationError) as context:
            self.registry.get_required_params("invalid_strategy", "normal")

        self.assertIn("Invalid strategy type", str(context.exception))


class TestErrorDetailsPreservation(unittest.TestCase):
    """Test that error details are properly preserved."""

    def test_matched_betting_error_details(self):
        """Test that MatchedBettingError preserves details."""
        error = MatchedBettingError("Main message", "Additional details")

        self.assertEqual(str(error), "Main message")
        self.assertEqual(error.details, "Additional details")

    def test_validation_error_inheritance(self):
        """Test that ValidationError inherits from MatchedBettingError."""
        error = ValidationError("Validation failed", "Invalid input")

        self.assertIsInstance(error, MatchedBettingError)
        self.assertEqual(str(error), "Validation failed")
        self.assertEqual(error.details, "Invalid input")

    def test_calculation_error_inheritance(self):
        """Test that CalculationError inherits from MatchedBettingError."""
        error = CalculationError("Calculation failed", "Division by zero")

        self.assertIsInstance(error, MatchedBettingError)
        self.assertEqual(str(error), "Calculation failed")
        self.assertEqual(error.details, "Division by zero")

    def test_configuration_error_inheritance(self):
        """Test that ConfigurationError inherits from MatchedBettingError."""
        error = ConfigurationError("Configuration invalid", "Missing parameter")

        self.assertIsInstance(error, MatchedBettingError)
        self.assertEqual(str(error), "Configuration invalid")
        self.assertEqual(error.details, "Missing parameter")


if __name__ == "__main__":
    unittest.main()
