from typing import Dict, Any
from base import CalculatorBase
from bet import BackLeyGroup

class BackLayReimbursementCalculator(CalculatorBase):
    def __init__(self, back_ley_group:BackLeyGroup, reiumbursement:float):
        """Calculator for reimbursement promotions.

        Args:
            back_ley_group (BackLeyGroup): 
            reiumbursement (float): Amount that is going to be received if the back_bet is lost. For example a FB 10€ will result in 7.5€ (assuming 75% freebet retention)
        """
        self.back_ley_group = back_ley_group
        self.reiumbursement = reiumbursement

    def calculate_stake(self) -> Dict[str, Any]:
        bb = self.back_ley_group.back_bet
        lb = self.back_ley_group.lay_bet
        
        raw_lay_stake = (bb.stake*bb.odds*((100-bb.fee)/100)-self.reiumbursement)/(lb.odds-lb.fee/100)
        lb.stake = round(raw_lay_stake,2)
        self.risk = round(lb.stake*(lb.odds-1.0),2)

        return {"lay_stake": lb.stake,"risk":self.risk}
