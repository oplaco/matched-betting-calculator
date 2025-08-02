"""
Calculation engine for matched betting calculations.

This module extracts the mathematical calculation logic from calculator classes
to improve Single Responsibility Principle adherence. The calculation engine
handles symbolic math operations while calculators focus on business logic.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List, Tuple
import sympy as sp
from matched_betting_calculator.utils import SymbolicMathHelper
from matched_betting_calculator.errors import CalculationError


class MathExpressionInterface(ABC):
    """
    Abstract interface for mathematical expressions.

    This interface follows the Dependency Inversion Principle by allowing
    different mathematical backends without coupling calculators to SymPy.
    """

    @abstractmethod
    def evaluate(self, substitutions: Dict[str, Any]) -> float:
        """
        Evaluate the expression with given substitutions.

        Args:
            substitutions: Variable substitutions

        Returns:
            Evaluated numeric result
        """
        pass

    @abstractmethod
    def solve_for(self, variable: str) -> "MathExpressionInterface":
        """
        Solve the expression for a specific variable.

        Args:
            variable: Variable to solve for

        Returns:
            New expression representing the solution
        """
        pass


class SymPyExpression(MathExpressionInterface):
    """
    SymPy implementation of mathematical expressions.

    This class encapsulates SymPy operations behind the MathExpressionInterface,
    allowing for potential replacement with other mathematical libraries.
    """

    def __init__(self, expression: sp.Expr):
        """
        Initialize with a SymPy expression.

        Args:
            expression: The SymPy expression to wrap
        """
        self._expression = expression

    def evaluate(self, substitutions: Dict[str, Any]) -> float:
        """Evaluate the SymPy expression with substitutions."""
        symbol_subs = {}
        for var_name, value in substitutions.items():
            symbol = sp.Symbol(var_name)
            symbol_subs[symbol] = value

        return SymbolicMathHelper.evaluate_expression(self._expression, symbol_subs)

    def solve_for(self, variable: str) -> "SymPyExpression":
        """Solve the SymPy expression for a variable."""
        symbol = sp.Symbol(variable)
        solution = SymbolicMathHelper.solve_equation(sp.Eq(self._expression, 0), symbol)
        return SymPyExpression(solution)

    @property
    def expression(self) -> sp.Expr:
        """Get the underlying SymPy expression."""
        return self._expression


class CalculationEngine:
    """
    Engine for performing matched betting calculations.

    This class is responsible for the mathematical aspects of calculations,
    separating concerns from business logic in calculator classes.
    """

    def __init__(self, math_backend: str = "sympy"):
        """
        Initialize the calculation engine.

        Args:
            math_backend: Mathematical backend to use ("sympy" for now)
        """
        self._math_backend = math_backend
        self._cached_solutions: Dict[str, MathExpressionInterface] = {}

    def create_equation_system(
        self,
        back_balance_expr: MathExpressionInterface,
        lay_balance_expr: MathExpressionInterface,
        variable_to_solve: str,
    ) -> MathExpressionInterface:
        """
        Create and solve an equation system for matched betting.

        Args:
            back_balance_expr: Expression for back bet balance
            lay_balance_expr: Expression for lay bet balance
            variable_to_solve: Variable to solve for (e.g., "lay_stake")

        Returns:
            Expression representing the solution

        Raises:
            CalculationError: If the equation cannot be solved
        """
        cache_key = (
            f"{id(back_balance_expr)}_{id(lay_balance_expr)}_{variable_to_solve}"
        )

        if cache_key in self._cached_solutions:
            return self._cached_solutions[cache_key]

        try:
            if isinstance(back_balance_expr, SymPyExpression) and isinstance(
                lay_balance_expr, SymPyExpression
            ):
                # Create equation: back_balance = lay_balance
                equation = back_balance_expr.expression - lay_balance_expr.expression
                equation_expr = SymPyExpression(equation)
                solution = equation_expr.solve_for(variable_to_solve)

                self._cached_solutions[cache_key] = solution
                return solution
            else:
                raise CalculationError(
                    "Unsupported expression types", f"Backend: {self._math_backend}"
                )
        except Exception as e:
            raise CalculationError(
                f"Failed to solve equation system for {variable_to_solve}",
                f"Error: {str(e)}",
            )

    def calculate_stake(
        self, solution_expr: MathExpressionInterface, variable_values: Dict[str, Any]
    ) -> float:
        """
        Calculate stake using a solved expression.

        Args:
            solution_expr: The solved expression for stake calculation
            variable_values: Values for all variables in the expression

        Returns:
            Calculated stake value

        Raises:
            CalculationError: If calculation fails
        """
        try:
            result = solution_expr.evaluate(variable_values)
            return SymbolicMathHelper.round_numeric_value(result)
        except Exception as e:
            raise CalculationError("Failed to calculate stake", f"Error: {str(e)}")

    def calculate_risk(self, lay_stake: float, lay_odds: float) -> float:
        """
        Calculate risk (liability) for a lay bet.

        Args:
            lay_stake: The lay stake amount
            lay_odds: The lay bet odds

        Returns:
            Calculated risk amount
        """
        return SymbolicMathHelper.round_numeric_value(lay_stake * (lay_odds - 1))

    def calculate_balances(
        self,
        back_balance_expr: MathExpressionInterface,
        lay_balance_expr: MathExpressionInterface,
        variable_values: Dict[str, Any],
    ) -> Dict[str, float]:
        """
        Calculate back and lay balances.

        Args:
            back_balance_expr: Expression for back balance
            lay_balance_expr: Expression for lay balance
            variable_values: Values for all variables

        Returns:
            Dictionary with back_balance and lay_balance

        Raises:
            CalculationError: If calculation fails
        """
        try:
            back_balance = back_balance_expr.evaluate(variable_values)
            lay_balance = lay_balance_expr.evaluate(variable_values)

            return {
                "back_balance": SymbolicMathHelper.round_numeric_value(back_balance),
                "lay_balance": SymbolicMathHelper.round_numeric_value(lay_balance),
            }
        except Exception as e:
            raise CalculationError("Failed to calculate balances", f"Error: {str(e)}")

    def clear_cache(self) -> None:
        """Clear the solution cache."""
        self._cached_solutions.clear()


class ExpressionBuilder:
    """
    Builder for creating mathematical expressions.

    This class provides a fluent interface for building complex mathematical
    expressions used in matched betting calculations.
    """

    def __init__(self, backend: str = "sympy"):
        """
        Initialize the expression builder.

        Args:
            backend: Mathematical backend to use
        """
        self._backend = backend

    def create_symbol(self, name: str) -> sp.Symbol:
        """
        Create a mathematical symbol.

        Args:
            name: Symbol name

        Returns:
            Mathematical symbol
        """
        if self._backend == "sympy":
            return sp.Symbol(name)
        else:
            raise ValueError(f"Unsupported backend: {self._backend}")

    def build_expression(self, expression: sp.Expr) -> MathExpressionInterface:
        """
        Build a mathematical expression.

        Args:
            expression: Raw mathematical expression

        Returns:
            Wrapped expression implementing the interface
        """
        if self._backend == "sympy":
            return SymPyExpression(expression)
        else:
            raise ValueError(f"Unsupported backend: {self._backend}")

    def build_normal_back_balance(
        self,
        back_stake_symbol: sp.Symbol,
        back_odds_symbol: sp.Symbol,
        back_fee_symbol: sp.Symbol,
        lay_stake_symbol: sp.Symbol,
        lay_odds_symbol: sp.Symbol,
        percent_divisor: int = 100,
    ) -> MathExpressionInterface:
        """
        Build expression for normal back bet balance.

        Returns expression for balance when back bet wins.
        """
        expression = back_stake_symbol * (
            back_odds_symbol * (1 - back_fee_symbol / percent_divisor) - 1
        ) - lay_stake_symbol * (lay_odds_symbol - 1)
        return self.build_expression(expression)

    def build_normal_lay_balance(
        self,
        lay_stake_symbol: sp.Symbol,
        lay_fee_symbol: sp.Symbol,
        back_stake_symbol: sp.Symbol,
        percent_divisor: int = 100,
    ) -> MathExpressionInterface:
        """
        Build expression for normal lay bet balance.

        Returns expression for balance when lay bet wins.
        """
        expression = (
            lay_stake_symbol * (1 - lay_fee_symbol / percent_divisor)
            - back_stake_symbol
        )
        return self.build_expression(expression)
