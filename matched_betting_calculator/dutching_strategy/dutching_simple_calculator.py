from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from matched_betting_calculator.base import CalculatorBase
from matched_betting_calculator.bet import DutchingGroup
from matched_betting_calculator.constants import PercentageConstants
from matched_betting_calculator.errors import CalculationError, ValidationError
import sympy as sp


class DutchingSimpleCalculator(CalculatorBase, ABC):
    """Base class for Back-Back Dutching strategy calculators.
    The equations are solved assuming all the bets are equal to the same overall balance
    """

    _cached_n_bets: Optional[int] = None
    _cached_solution: Optional[Dict[sp.Symbol, sp.Expr]] = None
    balance_sym = None
    bb_odds = bb_fee = bb_stake = None
    db_odds_syms = db_fee_syms = db_stake_syms = None

    def __init__(self, dutching_group: DutchingGroup):
        self.back_bet = dutching_group.back_bet
        self.dutching_bets = dutching_group.dutching_bets
        self.n_bets = len(self.dutching_bets)
        self.__class__._ensure_symbols(self.n_bets)

    @classmethod
    def _ensure_symbols(cls, n_bets: int) -> None:
        """Create symbolic variables once per calculator class and n_bets."""
        if cls._cached_n_bets == n_bets and cls.balance_sym is not None:
            return

        cls._cached_n_bets = n_bets
        cls._cached_solution = None
        cls.balance_sym = sp.Symbol("balance")
        cls.bb_odds, cls.bb_fee, cls.bb_stake = sp.symbols("bb_odds bb_fee bb_stake")
        cls.db_odds_syms = sp.symbols(f"db_odds0:{n_bets}")
        cls.db_fee_syms = sp.symbols(f"db_fee0:{n_bets}")
        cls.db_stake_syms = sp.symbols(f"db_stake0:{n_bets}")

    @classmethod
    def _get_solution(cls, n_bets: int) -> Dict[sp.Symbol, sp.Expr]:
        """Solve the equation system once per calculator class and n_bets."""
        cls._ensure_symbols(n_bets)
        if cls._cached_solution is not None:
            return cls._cached_solution

        obj = cls.__new__(cls)
        obj.n_bets = n_bets

        equations = [obj.build_main_back_balance_expr()]
        for i in range(n_bets):
            equations.append(obj.build_back_balance_expr(i))

        unknowns = tuple(cls.db_stake_syms) + (cls.balance_sym,)
        solution = sp.solve(equations, unknowns)
        if not solution:
            raise CalculationError(
                "Failed to solve dutching equation system", "No solutions found"
            )

        cls._cached_solution = solution
        return cls._cached_solution

    @abstractmethod
    def build_main_back_balance_expr(self):
        """Build the balance equation for the first back bet (the one done in the
        bookmaker where the promotional offer lies.)"""
        pass

    @abstractmethod
    def build_back_balance_expr(self, i: int):
        """Build balance equation for the dutching bets (the bets done in order to
        hedge against the main back bet.)"""
        pass

    def get_subs(self) -> dict:
        """Return the substitutions values for odds, fees, and stakes."""
        subs = {
            self.bb_stake: self.back_bet.stake,
            self.bb_odds: self.back_bet.odds,
            self.bb_fee: self.back_bet.fee,
        }

        for i, bet in enumerate(self.dutching_bets):
            subs.update({self.db_odds_syms[i]: bet.odds, self.db_fee_syms[i]: bet.fee})

        return subs

    def get_rest_dutching_stakes_expr(
        self, exclude_index: Optional[int] = None
    ) -> sp.Expr:
        """Return the sum of all dutching stake symbols, optionally excluding one by index."""
        return sum(
            stake
            for i, stake in enumerate(self.db_stake_syms)
            if exclude_index is None or i != exclude_index
        )

    def calculate_stake(self, apply_result_to_bet: bool = True) -> Dict[str, Any]:
        """Calculate and return the stake for each back bet and dutching bet.

        Args:
            apply_result_to_bet: If True, updates dutching bets' stakes with the calculated values.
                                If False, performs a pure calculation without side effects.

        Returns:
            Dictionary with calculated stakes and overall balance
        """
        solution = self.__class__._get_solution(self.n_bets)
        subs = self.get_subs()

        result = {}
        for i, stake_symbol in enumerate(self.db_stake_syms):
            stake_val_numeric = solution[stake_symbol].subs(subs).evalf()
            stake_rounded = round(stake_val_numeric, PercentageConstants.DECIMAL_PLACES)

            result[f"dutching_bet_{i}_stake"] = stake_rounded

            if apply_result_to_bet:
                self.dutching_bets[i].stake = stake_rounded

        overall_balance_value = solution[self.balance_sym].subs(subs).evalf()
        result["overall_balance"] = round(
            overall_balance_value, PercentageConstants.DECIMAL_PLACES
        )

        return self._format_results(result)


class DutchingNormalCalculator(DutchingSimpleCalculator):
    def build_main_back_balance_expr(self):
        percent_divisor = sp.Integer(PercentageConstants.PERCENT_DIVISOR)
        rest_dutching_stakes = self.get_rest_dutching_stakes_expr()
        return (
            self.bb_stake * (self.bb_odds * (1 - self.bb_fee / percent_divisor) - 1)
            - rest_dutching_stakes
            - self.balance_sym
        )

    def build_back_balance_expr(self, i: int):
        percent_divisor = sp.Integer(PercentageConstants.PERCENT_DIVISOR)
        rest_dutching_stakes = self.get_rest_dutching_stakes_expr(i)
        return (
            self.db_stake_syms[i]
            * (self.db_odds_syms[i] * (1 - self.db_fee_syms[i] / percent_divisor) - 1)
            - self.bb_stake
            - rest_dutching_stakes
            - self.balance_sym
        )


class DutchingFreebetCalculator(DutchingSimpleCalculator):
    def build_main_back_balance_expr(self):
        percent_divisor = sp.Integer(PercentageConstants.PERCENT_DIVISOR)
        rest_dutching_stakes = self.get_rest_dutching_stakes_expr()
        return (
            self.bb_stake * (self.bb_odds - 1) * (1 - self.bb_fee / percent_divisor)
            - rest_dutching_stakes
            - self.balance_sym
        )

    def build_back_balance_expr(self, i: int):
        percent_divisor = sp.Integer(PercentageConstants.PERCENT_DIVISOR)
        rest_dutching_stakes = self.get_rest_dutching_stakes_expr(i)
        return (
            self.db_stake_syms[i]
            * (self.db_odds_syms[i] * (1 - self.db_fee_syms[i] / percent_divisor) - 1)
            - rest_dutching_stakes
            - self.balance_sym
        )


class DutchingReimbursementCalculator(DutchingSimpleCalculator):
    def __init__(self, dutching_group: DutchingGroup, reimbursement: float):
        """Calculator for reimbursement promotions.

        Args:
            dutching_group (DutchingGroup):
            reimbursement (float): Amount that is going to be received if the back_bet is lost.
            For example a FB 10€ will result in 7.5€ (assuming 75% freebet retention) therefore reimbursement=7.5
        """
        self.reimbursement = reimbursement
        super().__init__(dutching_group)

    @classmethod
    def _ensure_symbols(cls, n_bets: int) -> None:
        super()._ensure_symbols(n_bets)
        if not hasattr(cls, "reimbursement_sym"):
            cls.reimbursement_sym = sp.Symbol("reimbursement_sym")

    def get_subs(self) -> dict:
        subs = super().get_subs()
        subs[self.reimbursement_sym] = self.reimbursement
        return subs

    def build_main_back_balance_expr(self):
        percent_divisor = sp.Integer(PercentageConstants.PERCENT_DIVISOR)
        rest_dutching_stakes = self.get_rest_dutching_stakes_expr()
        return (
            self.bb_stake * (self.bb_odds * (1 - self.bb_fee / percent_divisor) - 1)
            - rest_dutching_stakes
            - self.balance_sym
        )

    def build_back_balance_expr(self, i: int):
        percent_divisor = sp.Integer(PercentageConstants.PERCENT_DIVISOR)
        rest_dutching_stakes = self.get_rest_dutching_stakes_expr(i)
        return (
            self.db_stake_syms[i]
            * (self.db_odds_syms[i] * (1 - self.db_fee_syms[i] / percent_divisor) - 1)
            - self.bb_stake
            - rest_dutching_stakes
            - self.balance_sym
            + self.reimbursement_sym
        )


class DutchingWinBonusCalculator(DutchingSimpleCalculator):
    def __init__(self, dutching_group: DutchingGroup, win_bonus: float):
        """Calculator for win-bonus promotions.

        Args:
            dutching_group (DutchingGroup):
            win_bonus (float): Extra amount received when the main back bet wins.
        """
        if win_bonus < 0:
            raise ValidationError(
                "Win bonus must be non-negative", f"Provided value: {win_bonus}"
            )

        self.win_bonus = win_bonus
        super().__init__(dutching_group)

    @classmethod
    def _ensure_symbols(cls, n_bets: int) -> None:
        super()._ensure_symbols(n_bets)
        if not hasattr(cls, "win_bonus_sym"):
            cls.win_bonus_sym = sp.Symbol("win_bonus_sym")

    def get_subs(self) -> dict:
        subs = super().get_subs()
        subs[self.win_bonus_sym] = self.win_bonus
        return subs

    def build_main_back_balance_expr(self):
        percent_divisor = sp.Integer(PercentageConstants.PERCENT_DIVISOR)
        rest_dutching_stakes = self.get_rest_dutching_stakes_expr()
        return (
            self.bb_stake * (self.bb_odds * (1 - self.bb_fee / percent_divisor) - 1)
            - rest_dutching_stakes
            + self.win_bonus_sym
            - self.balance_sym
        )

    def build_back_balance_expr(self, i: int):
        percent_divisor = sp.Integer(PercentageConstants.PERCENT_DIVISOR)
        rest_dutching_stakes = self.get_rest_dutching_stakes_expr(i)
        return (
            self.db_stake_syms[i]
            * (self.db_odds_syms[i] * (1 - self.db_fee_syms[i] / percent_divisor) - 1)
            - self.bb_stake
            - rest_dutching_stakes
            - self.balance_sym
        )


class DutchingRolloverCalculator(DutchingSimpleCalculator):
    def __init__(
        self,
        dutching_group: DutchingGroup,
        bonus_amount: float,
        remaining_rollover: float,
        expected_rating: float,
    ):
        """Calculator for reimbursement promotions.

        Args:
            dutching_group (DutchingGroup):
            bonus_amount (float): amount of the Back Bet stake made of bonus_amount balance.
            remaining_rollover (float): Remaining rollover (not taking into account back_bet_real stake and back_bet_bonus_amount stake).
            expected_rating (float): Expected rating at which the remaining rollover will be freed (e.g 95.06%).
        """
        self.bonus_amount = bonus_amount
        self.remaining_rollover = remaining_rollover
        self.expected_rating = expected_rating
        super().__init__(dutching_group)

    @classmethod
    def _ensure_symbols(cls, n_bets: int) -> None:
        super()._ensure_symbols(n_bets)
        if not hasattr(cls, "bonus_amount_sym"):
            cls.bonus_amount_sym = sp.Symbol("bonus_amount_sym")
            cls.remaining_rollover_sym = sp.Symbol("remaining_rollover_sym")
            cls.expected_rating_sym = sp.Symbol("expected_rating_sym")

    def get_subs(self) -> dict:
        subs = super().get_subs()
        subs[self.bonus_amount_sym] = self.bonus_amount
        subs[self.remaining_rollover_sym] = self.remaining_rollover
        subs[self.expected_rating_sym] = self.expected_rating
        return subs

    def build_main_back_balance_expr(self):
        percent_divisor = sp.Integer(PercentageConstants.PERCENT_DIVISOR)
        rollover_penalty = (
            self.remaining_rollover_sym - self.bb_stake - self.bonus_amount_sym
        ) * (1 - self.expected_rating_sym / percent_divisor)
        rest_dutching_stakes = self.get_rest_dutching_stakes_expr()
        return (
            (self.bb_stake + self.bonus_amount_sym)
            * self.bb_odds
            * (1 - self.bb_fee / percent_divisor)
            - self.bb_stake
            - rest_dutching_stakes
            - rollover_penalty
            - self.balance_sym
        )

    def build_back_balance_expr(self, i: int):
        percent_divisor = sp.Integer(PercentageConstants.PERCENT_DIVISOR)
        rest_dutching_stakes = self.get_rest_dutching_stakes_expr(i)
        return (
            self.db_stake_syms[i]
            * (self.db_odds_syms[i] * (1 - self.db_fee_syms[i] / percent_divisor) - 1)
            - self.bb_stake
            - rest_dutching_stakes
            - self.balance_sym
        )

