from abc import abstractmethod
from typing import Dict, Any
from matched_betting_calculator.base import CalculatorBase
from matched_betting_calculator.bet import BackLayGroup
import sympy as sp

class BackLayAccumulatedBaseCalculator(CalculatorBase):
    def __init__(self, combo_stake: float, combo_fee: float, back_ley_groups: list[BackLayGroup]):
        self.combo_stake = combo_stake
        self.combo_fee = combo_fee
        self.back_ley_groups = back_ley_groups
        self.combo_size = len(back_ley_groups)
        
    @abstractmethod
    def build_individual_equation(self, i, lay_stakes, balance):
        pass
    
    def build_final_equation(self, total_odds, lay_stakes, balance, n):
        eq = self.combo_stake * (total_odds*(1-self.combo_fee/100) - 1)\
            - sum([lay_stakes[i] * (self.back_ley_groups[i].lay_bet.odds - 1) for i in range(n)]) \
            - balance       
        return eq
    
    def create_equations(self):
        # Number of bets in the combo
        n = len(self.back_ley_groups)

        # Symbols for lay stakes of each leg
        lay_stakes = [sp.symbols(f"lb{i+1}") for i in range(n)]

        # balance constant
        balance = sp.symbols('balance')

        # Create equations
        equations = []

        # Equation 1 to N-1: Case where the lay bets are won
        for i in range(0, n):
            group = self.back_ley_groups[i]
            bb = group.back_bet
            lb = group.lay_bet
            eq = self.build_individual_equation(i, lay_stakes, balance)
            equations.append(eq)

        # Equation N: Case where the accumulated bet is won
        total_odds = 1
        for group in self.back_ley_groups:
            total_odds *= group.back_bet.odds

        final_eq = self.build_final_equation(total_odds, lay_stakes, balance, n)
        equations.append(final_eq)

        return equations, lay_stakes, balance

    def calculate_stake(self) -> Dict[str, Any]:
        # Generate equations
        equations, lay_stakes, balance = self.create_equations()

        # Solve the system of equations
        solutions = sp.solve(equations, lay_stakes + [balance])

        # Return the results
        lay_stakes_solution = [solutions[lay_stakes[i]] for i in range(len(lay_stakes))]
        balance_solution = solutions[balance]

        result = []
        current_back_return = self.combo_stake

        for i, group in enumerate(self.back_ley_groups):
            lb = group.lay_bet
            current_back_return *= group.back_bet.odds * (1 - group.back_bet.fee / 100)

            risk = round(lay_stakes_solution[i] * (lb.odds - 1), 2)

            result.append({
                "event_index": i,
                "lay_stake": round(lay_stakes_solution[i], 2),
                "risk": risk,
                "expected_back_return": round(current_back_return, 2)
            })

        return {"accumulated_lay_bets": result}

class BackLayAccumulatedNormalCalculator(BackLayAccumulatedBaseCalculator):
    def build_individual_equation(self, i, lay_stakes, balance):
        group = self.back_ley_groups[i]
        lb = group.lay_bet
        eq = lay_stakes[i] * (1 - lb.fee / 100) \
            - sum([lay_stakes[j] * (self.back_ley_groups[j].lay_bet.odds - 1) for j in range(i)]) \
            - self.combo_stake - balance
             
        return eq
    
class BackLayAccumulatedFreebetCalculator(BackLayAccumulatedBaseCalculator):
    def build_individual_equation(self, i, lay_stakes, balance):
        group = self.back_ley_groups[i]
        lb = group.lay_bet
        eq = lay_stakes[i] * (1 - lb.fee / 100) \
            - sum([lay_stakes[j] * (self.back_ley_groups[j].lay_bet.odds - 1) for j in range(i)]) \
            - balance
             
        return eq
    
    def build_final_equation(self, total_odds, lay_stakes, balance, n):
        # On a freebet fees apply only to the net amount.
        eq = self.combo_stake * (total_odds - 1) * (1-self.combo_fee/100)\
            - sum([lay_stakes[i] * (self.back_ley_groups[i].lay_bet.odds - 1) for i in range(n)]) \
            - balance
            
        return eq
    
class BackLayAccumulatedReimbursementCalculator(BackLayAccumulatedBaseCalculator):
    def __init__(self, combo_stake: float, combo_fee: float, back_ley_groups: list[BackLayGroup], reimbursement: float):
        super().__init__(combo_stake, combo_fee, back_ley_groups)
        self.reimbursement = reimbursement
        
    def build_individual_equation(self, i, lay_stakes, balance):
        group = self.back_ley_groups[i]
        lb = group.lay_bet
        eq = lay_stakes[i] * (1 - lb.fee / 100) \
            - sum([lay_stakes[j] * (self.back_ley_groups[j].lay_bet.odds - 1) for j in range(i)]) \
            - balance - self.reimbursement
             
        return eq