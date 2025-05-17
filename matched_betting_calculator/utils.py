"""
Utility functions for the matched betting calculator.
"""

from typing import Dict, Any, List, Tuple
import sympy as sp
from matched_betting_calculator.constants import PercentageConstants


class SymbolicMathHelper:
    """Helper class for symbolic math operations."""

    @staticmethod
    def round_numeric_value(value: float) -> float:
        """
        Round a numeric value to the specified number of decimal places.

        Args:
            value: The value to round

        Returns:
            The rounded value
        """
        return round(value, PercentageConstants.DECIMAL_PLACES)

    @staticmethod
    def evaluate_expression(
        expression: sp.Expr, substitutions: Dict[sp.Symbol, Any]
    ) -> float:
        """
        Evaluate a symbolic expression with the given substitutions.

        Args:
            expression: The symbolic expression to evaluate
            substitutions: Dictionary mapping symbols to their values

        Returns:
            The evaluated result as a float
        """
        result = expression.subs(substitutions).evalf()
        return SymbolicMathHelper.round_numeric_value(result)

    @staticmethod
    def solve_equation(equation: sp.Eq, symbol: sp.Symbol) -> sp.Expr:
        """
        Solve an equation for the given symbol.

        Args:
            equation: The equation to solve
            symbol: The symbol to solve for

        Returns:
            An expression representing the solution
        """
        solutions = sp.solve(equation, symbol)
        if not solutions:
            raise MatchedBettingError("No solution found for the equation")
        return solutions[0]

    @staticmethod
    def solve_equation_system(
        equations: List[sp.Expr], symbols: Tuple[sp.Symbol, ...]
    ) -> Dict[sp.Symbol, sp.Expr]:
        """
        Solve a system of equations for the given symbols.

        Args:
            equations: List of equations to solve
            symbols: Tuple of symbols to solve for

        Returns:
            Dictionary mapping symbols to their solutions
        """
        solutions = sp.solve(equations, symbols)
        if not solutions:
            raise MatchedBettingError("No solution found for the equation system")
        return solutions
