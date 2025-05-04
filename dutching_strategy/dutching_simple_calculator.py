from abc import ABC, abstractmethod
from typing import Dict, Any
from base import CalculatorBase
from bet import DutchingGroup
import sympy as sp


class DutchingSimpleCalculator(CalculatorBase, ABC):
    """Base class for Back-Back Dutching strategy calculators.
    The equations are solved assuming all the bets are equal to the same overall balance """

    def __init__(self, dutching_group: DutchingGroup):
        self.back_bet = dutching_group.back_bet
        self.dutching_bets = dutching_group.dutching_bets
        self.n_bets = len(self.dutching_bets)
        self.create_symbolic_variables()

    def create_symbolic_variables(self):
        """Create symbolic variables for back bet and dutching bet's odds, fee, and stake."""
        # For the overall balance.
        self.balance_sym = sp.Symbol('balance')
        
        # For the back bet (i.e the bet in the bookmaker where the promotional offer lies).
        self.bb_odds, self.bb_fee, self.bb_stake = sp.symbols('bb_odds bb_fee bb_stake')
        
        # For each dutching bet.
        self.db_odds_syms = sp.symbols(f'db_odds0:{self.n_bets}')
        self.db_fee_syms = sp.symbols(f'db_fee0:{self.n_bets}')
        self.db_stake_syms = sp.symbols(f'db_stake0:{self.n_bets}')

    @abstractmethod
    def build_main_back_balance_expr(self):
        """Build the balance equation for the first back bet (the one done in the 
        bookmaker where the promotional offer lies.)"""
        pass

    @abstractmethod
    def build_back_balance_expr(self, i: int):
        """Build balance equation for the dutching bets (the bets done in order to 
        hedge againts the main back bet.)"""
        pass

    def get_subs(self) -> dict:
        """Return the substitutions values for odds, fees, and stakes."""
        subs = {self.bb_stake: self.back_bet.stake, self.bb_odds: self.back_bet.odds, self.bb_fee: self.back_bet.fee}
        
        for i, bet in enumerate(self.dutching_bets):
            subs.update({
                self.db_odds_syms[i]: bet.odds,
                self.db_fee_syms[i]: bet.fee
            })
        
        return subs

    def get_rest_dutching_stakes_expr(self, exclude_index: int = None) -> sp.Expr:
        """Return the sum of all dutching stake symbols, optionally excluding one by index."""
        return sum(
            stake for i, stake in enumerate(self.db_stake_syms)
            if exclude_index is None or i != exclude_index
        )
    
    def calculate_stake(self) -> Dict[str, Any]:
        """Calculate and return the stake for each back bet and dutching bet."""
        
        # List to store the equations for the backbet and all dutching bets (db_stake_0, db_stake_1, ..., db_stake_n).
        equations = []
        
        # Main back bet equation
        main_balance_eq = self.build_main_back_balance_expr()
        equations.append(main_balance_eq)
        
        # Build the equations for all dutching bets
        for i in range(self.n_bets):
            eq = self.build_back_balance_expr(i)
            equations.append(eq)

        # Solve the system of equations for all db_stake_i and self.balance_sym at once.
        solution = sp.solve(equations,  tuple(self.db_stake_syms) + (self.balance_sym,))

        # Substitute the symbolic variables with the actual values from the back bets
        subs = self.get_subs()

        # Evaluate the solutions and round them
        result = {}
        for i, stake_symbol in enumerate(self.db_stake_syms):
            # Evaluate the symbolic expression numerically
            stake_val_numeric = solution[stake_symbol].subs(subs).evalf() 
            stake_rounded = round(stake_val_numeric, 2)

            # Store the stake  in the result dictionary
            result[f'dutching_bet_{i}_stake'] = stake_rounded
            
            # Assign the calculated stake to each dutching bet
            self.dutching_bets[i].stake = stake_rounded

        # Add the overall balance (for all bets) to the result
        overall_balance_value = solution[self.balance_sym].subs(subs).evalf()
        result['overall_balance'] = round(overall_balance_value, 2)
        
        return result


class DutchingNormalCalculator(DutchingSimpleCalculator):
    def build_main_back_balance_expr(self):
        rest_dutching_stakes = self.get_rest_dutching_stakes_expr()
        return self.bb_stake * (self.bb_odds * (1 - self.bb_fee / 100)- 1) \
            - rest_dutching_stakes - self.balance_sym

    def build_back_balance_expr(self, i: int):
        rest_dutching_stakes = self.get_rest_dutching_stakes_expr(i)     
        return self.db_stake_syms[i] * (self.db_odds_syms[i] * (1 - self.db_fee_syms[i] / 100) - 1) \
            - self.bb_stake - rest_dutching_stakes- self.balance_sym

class DutchingFreebetCalculator(DutchingSimpleCalculator):
    def build_main_back_balance_expr(self):
        rest_dutching_stakes = self.get_rest_dutching_stakes_expr()
        return self.bb_stake * (self.bb_odds - 1) * (1 - self.bb_fee / 100) \
            - rest_dutching_stakes - self.balance_sym

    def build_back_balance_expr(self, i: int):
        rest_dutching_stakes = self.get_rest_dutching_stakes_expr(i)     
        return self.db_stake_syms[i] * (self.db_odds_syms[i] * (1 - self.db_fee_syms[i] / 100) - 1) \
            - rest_dutching_stakes- self.balance_sym
    
class DutchingReimbursementCalculator(DutchingSimpleCalculator):
    def __init__(self, dutching_group: DutchingGroup, reimbursement:float):
        """Calculator for reimbursement promotions.

        Args:
            dutching_group (DutchingGroup): 
            reimbursement (float): Amount that is going to be received if the back_bet is lost. 
            For example a FB 10€ will result in 7.5€ (assuming 75% freebet retention) therefore reimbursement=7.5
        """
        self.reimbursement = reimbursement
        super().__init__(dutching_group)
        
    def create_symbolic_variables(self):
        super().create_symbolic_variables()
        self.reimbursement_sym = sp.Symbol('reimbursement_sym')
        
    def get_subs(self) -> dict:
        subs = super().get_subs()
        subs[self.reimbursement_sym] = self.reimbursement
        return subs
        
    def build_main_back_balance_expr(self):
        rest_dutching_stakes = self.get_rest_dutching_stakes_expr()
        return self.bb_stake * (self.bb_odds * (1 - self.bb_fee / 100)- 1) - rest_dutching_stakes - self.balance_sym

    def build_back_balance_expr(self, i: int):
        rest_dutching_stakes = self.get_rest_dutching_stakes_expr(i)     
        return self.db_stake_syms[i] * (self.db_odds_syms[i] * (1 - self.db_fee_syms[i] / 100) - 1) \
            - self.bb_stake - rest_dutching_stakes- self.balance_sym \
            + self.reimbursement_sym
            
            
class DutchingRolloverCalculator(DutchingSimpleCalculator):
    def __init__(self, dutching_group: DutchingGroup, bonus_amount:float, remaining_rollover:float,expected_rating:float):
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
        
    def create_symbolic_variables(self):
        super().create_symbolic_variables()
        self.bonus_amount_sym = sp.Symbol('bonus_amount_sym')
        self.remaining_rollover_sym = sp.Symbol('remaining_rollover_sym')
        self.expected_rating_sym = sp.Symbol('expected_rating_sym')
        
    def get_subs(self) -> dict:
        subs = super().get_subs()
        subs[self.bonus_amount_sym] = self.bonus_amount
        subs[self.remaining_rollover_sym] = self.remaining_rollover
        subs[self.expected_rating_sym] = self.expected_rating
        return subs
        
    def build_main_back_balance_expr(self):
        rollover_penalty = (self.remaining_rollover_sym-self.bb_stake-self.bonus_amount_sym)*(1-self.expected_rating_sym/100)
        rest_dutching_stakes = self.get_rest_dutching_stakes_expr()
        return (self.bb_stake +self.bonus_amount_sym)* self.bb_odds * (1-self.bb_fee / 100) \
            - self.bb_stake - rest_dutching_stakes - rollover_penalty- self.balance_sym 

    def build_back_balance_expr(self, i: int):
        rest_dutching_stakes = self.get_rest_dutching_stakes_expr(i)     
        return self.db_stake_syms[i] * (self.db_odds_syms[i] * (1 - self.db_fee_syms[i] / 100) - 1) \
            - self.bb_stake - rest_dutching_stakes- self.balance_sym
