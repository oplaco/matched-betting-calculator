from abc import abstractmethod
from typing import Dict, Any, List, Optional
from matched_betting_calculator.base import CalculatorBase
from matched_betting_calculator.bet import BackLayGroup
from matched_betting_calculator.constants import PercentageConstants
from matched_betting_calculator.errors import CalculationError
import sympy as sp


class BackLayAccumulatedBaseCalculator(CalculatorBase):
    _cached_combo_size: Optional[int] = None
    _cached_solution: Optional[Dict[sp.Symbol, sp.Expr]] = None

    def __init__(
        self, combo_stake: float, combo_fee: float, back_ley_groups: list[BackLayGroup]
    ):
        self.combo_stake = combo_stake
        self.combo_fee = combo_fee
        self.back_ley_groups = back_ley_groups
        self.combo_size = len(back_ley_groups)
        self.__class__._ensure_symbols(self.combo_size)

    @classmethod
    def _ensure_symbols(cls, combo_size: int) -> None:
        """Create symbolic variables once per calculator class and combo size."""
        if cls._cached_combo_size == combo_size and hasattr(cls, "combo_stake_sym"):
            return

        cls._cached_combo_size = combo_size
        cls._cached_solution = None
        cls.combo_stake_sym = sp.Symbol("combo_stake")
        cls.combo_fee_sym = sp.Symbol("combo_fee")
        cls.lay_stake_syms = [sp.Symbol(f"lb{i+1}") for i in range(combo_size)]
        cls.balance_sym = sp.Symbol("balance")
        cls.lay_odds_syms = sp.symbols(f"lay_odds0:{combo_size}")
        cls.lay_fee_syms = sp.symbols(f"lay_fee0:{combo_size}")
        cls.back_odds_syms = sp.symbols(f"back_odds0:{combo_size}")

    @classmethod
    def _get_solution(cls, combo_size: int) -> Dict[sp.Symbol, sp.Expr]:
        """Solve the equation system once per calculator class and combo size."""
        cls._ensure_symbols(combo_size)
        if cls._cached_solution is not None:
            return cls._cached_solution

        obj = cls.__new__(cls)
        obj.combo_size = combo_size
        equations = obj._build_equations(combo_size)
        unknowns = cls.lay_stake_syms + [cls.balance_sym]
        solution = sp.solve(equations, unknowns)
        if not solution:
            raise CalculationError(
                "Failed to solve accumulated equation system", "No solutions found"
            )

        cls._cached_solution = solution
        return cls._cached_solution

    def _build_equations(self, n: int) -> List[sp.Expr]:
        lay_stakes = self.__class__.lay_stake_syms
        balance = self.__class__.balance_sym
        equations = []

        for i in range(n):
            equations.append(self.build_individual_equation(i, lay_stakes, balance))

        total_odds = 1
        for i in range(n):
            total_odds *= self.__class__.back_odds_syms[i]

        equations.append(self.build_final_equation(total_odds, lay_stakes, balance, n))
        return equations

    def get_subs(self) -> Dict[sp.Symbol, Any]:
        """Return substitution values for symbolic variables."""
        subs = {
            self.combo_stake_sym: self.combo_stake,
            self.combo_fee_sym: self.combo_fee,
        }
        for i, group in enumerate(self.back_ley_groups):
            subs[self.lay_odds_syms[i]] = group.lay_bet.odds
            subs[self.lay_fee_syms[i]] = group.lay_bet.fee
            subs[self.back_odds_syms[i]] = group.back_bet.odds
        return subs

    @abstractmethod
    def build_individual_equation(self, i, lay_stakes, balance):
        pass

    def build_final_equation(self, total_odds, lay_stakes, balance, n):
        pct = PercentageConstants.PERCENT_DIVISOR
        return (
            self.combo_stake_sym * (total_odds * (1 - self.combo_fee_sym / pct) - 1)
            - sum(
                lay_stakes[i] * (self.lay_odds_syms[i] - 1) for i in range(n)
            )
            - balance
        )

    def calculate_stake(self) -> Dict[str, Any]:
        solution = self.__class__._get_solution(self.combo_size)
        subs = self.get_subs()

        lay_stakes_solution = [
            round(
                float(solution[self.lay_stake_syms[i]].subs(subs).evalf()),
                PercentageConstants.DECIMAL_PLACES,
            )
            for i in range(self.combo_size)
        ]

        result = []
        current_back_return = self.combo_stake

        for i, group in enumerate(self.back_ley_groups):
            lb = group.lay_bet
            current_back_return *= group.back_bet.odds * (
                1 - group.back_bet.fee / PercentageConstants.PERCENT_DIVISOR
            )

            risk = round(
                lay_stakes_solution[i] * (lb.odds - 1),
                PercentageConstants.DECIMAL_PLACES,
            )

            result.append(
                {
                    "event_index": i,
                    "lay_stake": lay_stakes_solution[i],
                    "risk": risk,
                    "expected_back_return": round(
                        current_back_return, PercentageConstants.DECIMAL_PLACES
                    ),
                }
            )

        return self._format_results({"accumulated_lay_bets": result})


class BackLayAccumulatedNormalCalculator(BackLayAccumulatedBaseCalculator):
    def build_individual_equation(self, i, lay_stakes, balance):
        pct = PercentageConstants.PERCENT_DIVISOR
        return (
            lay_stakes[i] * (1 - self.lay_fee_syms[i] / pct)
            - sum(
                lay_stakes[j] * (self.lay_odds_syms[j] - 1) for j in range(i)
            )
            - self.combo_stake_sym
            - balance
        )


class BackLayAccumulatedFreebetCalculator(BackLayAccumulatedBaseCalculator):
    def build_individual_equation(self, i, lay_stakes, balance):
        pct = PercentageConstants.PERCENT_DIVISOR
        return (
            lay_stakes[i] * (1 - self.lay_fee_syms[i] / pct)
            - sum(
                lay_stakes[j] * (self.lay_odds_syms[j] - 1) for j in range(i)
            )
            - balance
        )

    def build_final_equation(self, total_odds, lay_stakes, balance, n):
        pct = PercentageConstants.PERCENT_DIVISOR
        return (
            self.combo_stake_sym * (total_odds - 1) * (1 - self.combo_fee_sym / pct)
            - sum(
                lay_stakes[i] * (self.lay_odds_syms[i] - 1) for i in range(n)
            )
            - balance
        )


class BackLayAccumulatedReimbursementCalculator(BackLayAccumulatedBaseCalculator):
    def __init__(
        self,
        combo_stake: float,
        combo_fee: float,
        back_ley_groups: list[BackLayGroup],
        reimbursement: float,
    ):
        self.reimbursement = reimbursement
        super().__init__(combo_stake, combo_fee, back_ley_groups)

    @classmethod
    def _ensure_symbols(cls, combo_size: int) -> None:
        super()._ensure_symbols(combo_size)
        if not hasattr(cls, "reimbursement_sym"):
            cls.reimbursement_sym = sp.Symbol("reimbursement")

    def get_subs(self) -> Dict[sp.Symbol, Any]:
        subs = super().get_subs()
        subs[self.reimbursement_sym] = self.reimbursement
        return subs

    def build_individual_equation(self, i, lay_stakes, balance):
        pct = PercentageConstants.PERCENT_DIVISOR
        return (
            lay_stakes[i] * (1 - self.lay_fee_syms[i] / pct)
            - sum(
                lay_stakes[j] * (self.lay_odds_syms[j] - 1) for j in range(i)
            )
            - balance
            - self.reimbursement_sym
        )
