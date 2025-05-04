from abc import ABC, abstractmethod
from typing import Dict, Any
from matched_betting_calculator.base import CalculatorBase
from matched_betting_calculator.bet import BackLayGroup
import sympy as sp

class BackLayBaseCalculator(CalculatorBase):
    # To be set in each subclass
    _lay_stake_expr = None 
    _back_balance_expr = None
    _lay_balance_expr = None
     
    def __init__(self,back_ley_group:BackLayGroup):
        self.bb =back_ley_group.back_bet
        self.lb =back_ley_group.lay_bet
    
    def get_subs(self) -> dict:
        return {
            self.__class__.bb_stake: self.bb.stake,
            self.__class__.bb_odds: self.bb.odds,
            self.__class__.bb_fee: self.bb.fee,
            self.__class__.lb_odds: self.lb.odds,
            self.__class__.lb_fee: self.lb.fee
        }
    
    @classmethod
    def create_symbolic_variables(cls):
        cls.bb_stake, cls.bb_odds, cls.bb_fee = sp.symbols('bb_stake bb_odds bb_fee')
        cls.lb_odds, cls.lb_fee = sp.symbols('lb_odds lb_fee')
        cls.lay_stake = sp.Symbol('lay_stake')
        
    @classmethod
    def _solve_expression(cls):
        """Called once per subclass to solve the equation."""
        obj = cls.__new__(cls)
        obj.create_symbolic_variables()
        cls._back_balance_expr = obj.build_back_balance_expr()
        cls._lay_balance_expr = obj.build_lay_balance_expr()
        eq = sp.Eq( cls._back_balance_expr, cls._lay_balance_expr)
        cls._lay_stake_expr = sp.solve(eq, obj.lay_stake)[0]
    
    def calculate_stake(self) -> Dict[str, Any]:

        if self._lay_stake_expr is None:
            self._solve_expression()
        
        # 5. Substitute numeric values
        subs = self.get_subs()

        lay_stake_val = self._lay_stake_expr.subs(self.get_subs())

        # 6. Evaluate balances with lay_stake plugged in
        back_val =  round(self._back_balance_expr.subs(subs | {self.lay_stake: lay_stake_val}),2)
        lay_val =  round(self._lay_balance_expr.subs(subs | {self.lay_stake: lay_stake_val}),2)

        # 7. Return
        self.lb.stake = round(lay_stake_val,2)
        self.risk = round(self.lb.stake*(self.lb.odds-1),2)
        

        return {"lay_stake": self.lb.stake,"risk":self.risk, "back_balance":back_val,"lay_balance":lay_val}
    
    @abstractmethod
    def build_back_balance_expr(self):
        """Build sympy expression representing the balance if the back bet is won.
        """
        pass
    
    @abstractmethod
    def build_lay_balance_expr(self):
        """Build sympy expression representing the balance if the lay bet is won.
        """
        pass

class BackLayNormalCalculator(BackLayBaseCalculator):
    def build_back_balance_expr(self):
        return self.bb_stake * (self.bb_odds * (1 - self.bb_fee / 100) - 1)- self.lay_stake * (self.lb_odds - 1)

    def build_lay_balance_expr(self):
        return self.lay_stake * (1 - self.lb_fee / 100) - self.bb_stake


class BackLayFreebetCalculator(BackLayBaseCalculator):
    def build_back_balance_expr(self):
        # The back bet fee only applys to the money returned (and the freebet amount is not returned by definition.)
        return self.bb_stake * (self.bb_odds-1) * (1 - self.bb_fee / 100)- self.lay_stake * (self.lb_odds - 1)
    
    def build_lay_balance_expr(self):
        return self.lay_stake * (1 - self.lb_fee / 100) 
    
class BackLayReimbursementCalculator(BackLayBaseCalculator):
    def __init__(self, back_ley_group:BackLayGroup, reimbursement:float):
        """Calculator for reimbursement promotions.

        Args:
            back_ley_group (BackLayGroup): 
            reimbursement (float): Amount that is going to be received if the back_bet is lost. 
            For example a FB 10€ will result in 7.5€ (assuming 75% freebet retention) therefore reimbursement=7.5
        """
        self.reimbursement = reimbursement
        super().__init__(back_ley_group)
        
    @classmethod
    def create_symbolic_variables(cls):
        super().create_symbolic_variables()
        cls.reimbursement_sy = sp.Symbol('reimbursement_sy')
        
    def get_subs(self) -> dict:
        base_subs = super().get_subs()
        base_subs[self.__class__.reimbursement_sy] = self.reimbursement
        return base_subs

    def build_back_balance_expr(self):
        return self.bb_stake * (self.bb_odds * (1 - self.bb_fee / 100) - 1)- self.lay_stake * (self.lb_odds - 1)
    
    def build_lay_balance_expr(self):
        """When the lay bet is won the reimbursement is received.
        """
        return self.lay_stake * (1 - self.lb_fee / 100) - self.bb_stake + self.reimbursement_sy
    
class BackLayRolloverCalculator(BackLayBaseCalculator):
    def __init__(self, back_ley_group:BackLayGroup, bonus_amount:float, remaining_rollover:float,expected_rating:float):
        """Calculator for rollover promotions.

        Args:
            back_ley_group (BackLayGroup): 
            bonus_amount (float): amount of the Back Bet stake made of bonus_amount balance.
            remaining_rollover (float): Remaining rollover (not taking into account back_bet_real stake and back_bet_bonus_amount stake).
            expected_rating (float): Expected rating at which the remaining rollover will be freed (e.g 95.06%).
        """
        if not (0 <= expected_rating <= 100):
            raise ValueError("Expected rating must be between 0 and 100.")
        
        self.back_ley_group = back_ley_group
        self.bonus_amount = bonus_amount
        self.remaining_rollover = remaining_rollover
        self.expected_rating = expected_rating
        super().__init__(back_ley_group)
        
    @classmethod
    def create_symbolic_variables(cls):
        super().create_symbolic_variables()
        cls.bonus_amount_sy = sp.symbols('bonus_amount')
        cls.remaining_rollover_sy = sp.symbols('remaining_rollover')
        cls.expected_rating_sy = sp.symbols('expected_rating')
        
    def get_subs(self) -> dict:
        subs = super().get_subs()
        subs[self.__class__.remaining_rollover_sy] = self.remaining_rollover
        subs[self.__class__.bonus_amount_sy] = self.bonus_amount
        subs[self.__class__.expected_rating_sy] = self.expected_rating
        return subs

    def build_back_balance_expr(self):

        rollover_penalty = (self.remaining_rollover_sy-self.bb_stake-self.bonus_amount_sy)*(1-self.expected_rating_sy/100)
        return (self.bb_stake +self.bonus_amount_sy)* self.bb_odds * (1-self.bb_fee / 100) \
                - self.bb_stake \
                - self.lay_stake * (self.lb_odds - 1) \
                - rollover_penalty
    
    def build_lay_balance_expr(self):
        return self.lay_stake * (1 - self.lb_fee / 100) - self.bb_stake 
