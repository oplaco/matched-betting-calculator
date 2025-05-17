"""
Simple calculators for back-lay betting strategies.

These calculators handle various types of bets in the back-lay strategy:
- Normal bets
- Free bets
- Reimbursement bets
- Rollover bets
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
import sympy as sp

from matched_betting_calculator.base import CalculatorBase
from matched_betting_calculator.bet import BackLayGroup
from matched_betting_calculator.constants import PercentageConstants
from matched_betting_calculator.errors import ValidationError, CalculationError
from matched_betting_calculator.utils import SymbolicMathHelper


class BackLayBaseCalculator(CalculatorBase, ABC):
    """Base class for all back-lay strategy calculators."""

    # Class variables to be set by _solve_expression
    _lay_stake_expr = None
    _back_balance_expr = None
    _lay_balance_expr = None

    def __init__(self, back_lay_group: BackLayGroup) -> None:
        """
        Initialize the calculator with a back-lay group.

        Args:
            back_lay_group: The back-lay group containing back and lay bets
        """
        self.back_bet = back_lay_group.back_bet
        self.lay_bet = back_lay_group.lay_bet

        # Create symbolic variables for this class if they don't exist yet
        if not hasattr(self.__class__, "back_bet_stake_symbol"):
            self.__class__.create_symbolic_variables()

    def get_subs(self) -> Dict[sp.Symbol, Any]:
        """
        Get substitution values for symbolic variables.

        Returns:
            Dictionary mapping symbolic variables to their numeric values
        """
        return {
            self.__class__.back_bet_stake_symbol: self.back_bet.stake,
            self.__class__.back_bet_odds_symbol: self.back_bet.odds,
            self.__class__.back_bet_fee_symbol: self.back_bet.fee,
            self.__class__.lay_bet_odds_symbol: self.lay_bet.odds,
            self.__class__.lay_bet_fee_symbol: self.lay_bet.fee,
        }

    @classmethod
    def create_symbolic_variables(cls) -> None:
        """Create symbolic variables for the equation system."""
        cls.back_bet_stake_symbol = sp.Symbol("back_bet_stake_symbol")
        cls.back_bet_odds_symbol = sp.Symbol("back_bet_odds_symbol")
        cls.back_bet_fee_symbol = sp.Symbol("back_bet_fee_symbol")
        cls.lay_bet_odds_symbol = sp.Symbol("lay_bet_odds_symbol")
        cls.lay_bet_fee_symbol = sp.Symbol("lay_bet_fee_symbol")
        cls.lay_stake_symbol = sp.Symbol("lay_stake_symbol")

    @classmethod
    def _solve_expression(cls) -> None:
        """
        Solve the equation system for the lay stake.

        This method is called once per subclass to solve the equation.
        It implements the Template Method pattern by calling the abstract methods
        build_back_balance_expr and build_lay_balance_expr that must be implemented
        by subclasses.
        """
        # Create a temporary instance to access instance methods
        obj = cls.__new__(cls)

        # Ensure symbols are created
        if not hasattr(cls, "back_bet_stake_symbol"):
            cls.create_symbolic_variables()

        # Build the expressions (Template Method pattern - calling abstract methods)
        cls._back_balance_expr = obj.build_back_balance_expr()
        cls._lay_balance_expr = obj.build_lay_balance_expr()

        # Create and solve the equation
        eq = sp.Eq(cls._back_balance_expr, cls._lay_balance_expr)
        solutions = SymbolicMathHelper.solve_equation(eq, obj.lay_stake_symbol)

        if solutions:
            cls._lay_stake_expr = solutions
        else:
            raise CalculationError("Failed to solve equation", "No solutions found")

    def _calculate_lay_stake(self) -> float:
        """
        Calculate the lay stake based on the solved expression.

        Returns:
            The calculated lay stake value

        Raises:
            CalculationError: If the expression cannot be solved
        """
        # Solve the expression if it hasn't been solved yet
        if self.__class__._lay_stake_expr is None:
            self.__class__._solve_expression()

        if self.__class__._lay_stake_expr is None:
            raise CalculationError(
                "Expression not solved", "Lay stake expression is None"
            )

        # Get substitution values
        subs = self.get_subs()

        try:
            # Substitute values and evaluate
            lay_stake_val = float(self.__class__._lay_stake_expr.subs(subs))
            return SymbolicMathHelper.round_numeric_value(lay_stake_val)
        except Exception as e:
            raise CalculationError("Failed to calculate lay stake", f"Error: {str(e)}")

    def _calculate_risk(self, lay_stake: float) -> float:
        """
        Calculate the risk (liability) based on the lay stake.

        Args:
            lay_stake: The calculated lay stake

        Returns:
            The calculated risk amount
        """
        return SymbolicMathHelper.round_numeric_value(
            lay_stake * (self.lay_bet.odds - 1)
        )

    def _calculate_balances(self, lay_stake: float) -> Dict[str, float]:
        """
        Calculate the back and lay balances based on the lay stake.

        Args:
            lay_stake: The calculated lay stake

        Returns:
            Dictionary with back_balance and lay_balance values

        Raises:
            CalculationError: If the expressions are not available
        """
        # Ensure expressions are solved
        if (
            self.__class__._back_balance_expr is None
            or self.__class__._lay_balance_expr is None
        ):
            self.__class__._solve_expression()

        if (
            self.__class__._back_balance_expr is None
            or self.__class__._lay_balance_expr is None
        ):
            raise CalculationError(
                "Balance expressions not available", "Balance expressions are None"
            )

        # Get substitution values and add lay stake
        subs = self.get_subs()
        subs[self.__class__.lay_stake_symbol] = lay_stake

        try:
            # Calculate balances
            back_balance = float(self.__class__._back_balance_expr.subs(subs))
            lay_balance = float(self.__class__._lay_balance_expr.subs(subs))

            # No special case handling needed - use mathematically correct values

            return {
                "back_balance": SymbolicMathHelper.round_numeric_value(back_balance),
                "lay_balance": SymbolicMathHelper.round_numeric_value(lay_balance),
            }
        except Exception as e:
            raise CalculationError("Failed to calculate balances", f"Error: {str(e)}")

    def calculate_stake(self, apply_result_to_bet: bool = True) -> Dict[str, Any]:
        """
        Calculate the optimal lay stake and return the results.

        Args:
            apply_result_to_bet: If True, updates self.lay_bet.stake with the calculated value.
                               If False, performs a pure calculation without side effects.

        Returns:
            Dictionary with lay_stake, risk, back_balance, and lay_balance

        Raises:
            CalculationError: If the calculation fails
        """
        try:
            # Calculate lay stake
            lay_stake = self._calculate_lay_stake()

            # Calculate risk
            risk = self._calculate_risk(lay_stake)

            # Calculate balances
            balances = self._calculate_balances(lay_stake)

            # Only apply the result to the bet if explicitly requested
            if apply_result_to_bet:
                self.lay_bet.stake = lay_stake

            # Prepare results
            results = {"lay_stake": lay_stake, "risk": risk, **balances}

            return self._format_results(results)
        except Exception as e:
            if isinstance(e, CalculationError):
                raise e
            raise CalculationError("Failed to calculate stake", f"Error: {str(e)}")

    @abstractmethod
    def build_back_balance_expr(self) -> sp.Expr:
        """
        Build sympy expression representing the balance if the back bet is won.

        Returns:
            A symbolic expression for the back balance
        """
        pass

    @abstractmethod
    def build_lay_balance_expr(self) -> sp.Expr:
        """
        Build sympy expression representing the balance if the lay bet is won.

        Returns:
            A symbolic expression for the lay balance
        """
        pass


class BackLayNormalCalculator(BackLayBaseCalculator):
    """Calculator for normal back-lay bets (no promotional offers)."""

    def build_back_balance_expr(self) -> sp.Expr:
        """Build expression for normal back-lay bet where back bet wins."""
        # Create a numeric symbol for percent divisor to avoid type issues
        percent_divisor = sp.Integer(PercentageConstants.PERCENT_DIVISOR)

        # Back bet winnings minus lay bet loss
        return self.back_bet_stake_symbol * (
            self.back_bet_odds_symbol * (1 - self.back_bet_fee_symbol / percent_divisor)
            - 1
        ) - self.lay_stake_symbol * (self.lay_bet_odds_symbol - 1)

    def build_lay_balance_expr(self) -> sp.Expr:
        """Build expression for normal back-lay bet where lay bet wins."""
        # Create a numeric symbol for percent divisor to avoid type issues
        percent_divisor = sp.Integer(PercentageConstants.PERCENT_DIVISOR)

        # Lay bet winnings minus back bet stake
        return (
            self.lay_stake_symbol * (1 - self.lay_bet_fee_symbol / percent_divisor)
            - self.back_bet_stake_symbol
        )


class BackLayFreebetCalculator(BackLayBaseCalculator):
    """Calculator for free bet offers in back-lay strategy."""

    def build_back_balance_expr(self) -> sp.Expr:
        """
        Build expression for free bet where back bet wins.
        The back bet fee only applies to the money returned
        (and the freebet amount is not returned by definition).
        """
        # Create a numeric symbol for percent divisor to avoid type issues
        percent_divisor = sp.Integer(PercentageConstants.PERCENT_DIVISOR)

        # Free bet winnings (odds-1) minus lay bet loss
        return self.back_bet_stake_symbol * (self.back_bet_odds_symbol - 1) * (
            1 - self.back_bet_fee_symbol / percent_divisor
        ) - self.lay_stake_symbol * (self.lay_bet_odds_symbol - 1)

    def build_lay_balance_expr(self) -> sp.Expr:
        """Build expression for free bet where lay bet wins."""
        # Create a numeric symbol for percent divisor to avoid type issues
        percent_divisor = sp.Integer(PercentageConstants.PERCENT_DIVISOR)

        # Lay bet winnings (free bet stake is not lost)
        return self.lay_stake_symbol * (1 - self.lay_bet_fee_symbol / percent_divisor)


class BackLayReimbursementCalculator(BackLayBaseCalculator):
    """Calculator for reimbursement promotions in back-lay strategy."""

    def __init__(self, back_lay_group: BackLayGroup, reimbursement: float) -> None:
        """
        Initialize a reimbursement calculator.

        Args:
            back_lay_group: The back-lay bet group
            reimbursement: Amount that will be received if the back bet is lost.
                           For example, a FB 10€ will result in 7.5€ (assuming 75%
                           freebet retention) therefore reimbursement=7.5

        Raises:
            ValidationError: If reimbursement is negative or exceeds the back bet stake
        """
        if reimbursement < 0:
            raise ValidationError(
                "Reimbursement must be non-negative", f"Provided value: {reimbursement}"
            )

        # Initialize the parent class first to set up self.back_bet
        super().__init__(back_lay_group)

        # Now validate that reimbursement doesn't exceed the original back bet stake
        if self.back_bet.stake is None:
            raise ValidationError(
                "Back bet stake must be set when using reimbursement calculator",
                "Back bet stake cannot be None",
            )

        if reimbursement > self.back_bet.stake:
            raise ValidationError(
                "Reimbursement cannot exceed the original back bet stake",
                f"Reimbursement: {reimbursement}, Back bet stake: {self.back_bet.stake}",
            )

        self.reimbursement = reimbursement

        # Ensure the reimbursement symbol is created
        if not hasattr(self.__class__, "reimbursement_symbol"):
            self.__class__.create_symbolic_variables()

    @classmethod
    def create_symbolic_variables(cls) -> None:
        """Create symbolic variables including reimbursement."""
        super().create_symbolic_variables()
        cls.reimbursement_symbol = sp.Symbol("reimbursement_symbol")

    def get_subs(self) -> Dict[sp.Symbol, Any]:
        """Get substitution values including reimbursement."""
        base_subs = super().get_subs()
        base_subs[self.__class__.reimbursement_symbol] = self.reimbursement
        return base_subs

    def build_back_balance_expr(self) -> sp.Expr:
        """Build expression for reimbursement offer where back bet wins."""
        # Create a numeric symbol for percent divisor to avoid type issues
        percent_divisor = sp.Integer(PercentageConstants.PERCENT_DIVISOR)

        # Back bet winnings minus lay bet loss
        return self.back_bet_stake_symbol * (
            self.back_bet_odds_symbol * (1 - self.back_bet_fee_symbol / percent_divisor)
            - 1
        ) - self.lay_stake_symbol * (self.lay_bet_odds_symbol - 1)

    def build_lay_balance_expr(self) -> sp.Expr:
        """
        Build expression for reimbursement offer where lay bet wins.
        When the lay bet is won, the reimbursement is received.
        """
        # Create a numeric symbol for percent divisor to avoid type issues
        percent_divisor = sp.Integer(PercentageConstants.PERCENT_DIVISOR)

        # Lay bet winnings plus reimbursement minus back bet stake
        return (
            self.lay_stake_symbol * (1 - self.lay_bet_fee_symbol / percent_divisor)
            - self.back_bet_stake_symbol
            + self.reimbursement_symbol
        )


class BackLayRolloverCalculator(BackLayBaseCalculator):
    """Calculator for rollover promotions in back-lay strategy."""

    def __init__(
        self,
        back_lay_group: BackLayGroup,
        bonus_amount: float,
        remaining_rollover: float,
        expected_rating: float,
    ) -> None:
        """
        Initialize a rollover calculator.

        Args:
            back_lay_group: The back-lay bet group
            bonus_amount: Amount of the back bet stake made of bonus balance
            remaining_rollover: Remaining rollover (not taking into account back bet stake
                               and bonus amount stake)
            expected_rating: Expected rating at which the remaining rollover
                           will be freed (e.g., 95.06%)

        Raises:
            ValidationError: If parameters are invalid
        """
        if not (0 <= expected_rating <= 100):
            raise ValidationError(
                "Expected rating must be between 0 and 100",
                f"Provided value: {expected_rating}",
            )

        if bonus_amount < 0:
            raise ValidationError(
                "Bonus amount must be non-negative", f"Provided value: {bonus_amount}"
            )

        if remaining_rollover < 0:
            raise ValidationError(
                "Remaining rollover must be non-negative",
                f"Provided value: {remaining_rollover}",
            )

        self.bonus_amount = bonus_amount
        self.remaining_rollover = remaining_rollover
        self.expected_rating = expected_rating

        # Call parent init after setting attributes
        super().__init__(back_lay_group)

        # Ensure the rollover symbols are created
        if not hasattr(self.__class__, "bonus_amount_symbol"):
            self.__class__.create_symbolic_variables()

    @classmethod
    def create_symbolic_variables(cls) -> None:
        """Create symbolic variables for rollover calculations."""
        super().create_symbolic_variables()
        cls.bonus_amount_symbol = sp.Symbol("bonus_amount_symbol")
        cls.remaining_rollover_symbol = sp.Symbol("remaining_rollover_symbol")
        cls.expected_rating_symbol = sp.Symbol("expected_rating_symbol")

    def get_subs(self) -> Dict[sp.Symbol, Any]:
        """Get substitution values including rollover parameters."""
        subs = super().get_subs()
        subs[self.__class__.remaining_rollover_symbol] = self.remaining_rollover
        subs[self.__class__.bonus_amount_symbol] = self.bonus_amount
        subs[self.__class__.expected_rating_symbol] = self.expected_rating
        return subs

    def build_back_balance_expr(self) -> sp.Expr:
        """Build expression for rollover offer where back bet wins."""
        # Create a numeric symbol for percent divisor to avoid type issues
        percent_divisor = sp.Integer(PercentageConstants.PERCENT_DIVISOR)

        # Calculate potential rollover amount that needs to be factored
        remaining_after_bet_and_bonus = (
            self.remaining_rollover_symbol
            - self.back_bet_stake_symbol
            - self.bonus_amount_symbol
        )

        # Calculate rollover penalty, ensuring it's never negative
        # If remaining_rollover < (stake + bonus), then max(remaining_after_bet_and_bonus, 0) = 0
        # which makes the penalty 0 (no penalty when rollover is already cleared)
        rollover_penalty = sp.Max(remaining_after_bet_and_bonus, sp.Integer(0)) * (
            1 - self.expected_rating_symbol / percent_divisor
        )

        # Back bet winnings (including bonus) minus lay bet loss minus rollover penalty
        return (
            (self.back_bet_stake_symbol + self.bonus_amount_symbol)
            * self.back_bet_odds_symbol
            * (1 - self.back_bet_fee_symbol / percent_divisor)
            - self.back_bet_stake_symbol
            - self.lay_stake_symbol * (self.lay_bet_odds_symbol - 1)
            - rollover_penalty
        )

    def build_lay_balance_expr(self) -> sp.Expr:
        """Build expression for rollover offer where lay bet wins."""
        # Create a numeric symbol for percent divisor to avoid type issues
        percent_divisor = sp.Integer(PercentageConstants.PERCENT_DIVISOR)

        # Lay bet winnings minus back bet stake
        return (
            self.lay_stake_symbol * (1 - self.lay_bet_fee_symbol / percent_divisor)
            - self.back_bet_stake_symbol
        )
