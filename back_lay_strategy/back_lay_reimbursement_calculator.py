from typing import Dict, Any
from back_lay_strategy.back_lay_base_calculator import BackLayCalculator
from bet import Bet

class BackLayReimbursementCalculator(BackLayCalculator):
    def __init__(self, back_bet: Bet, lay_bet: Bet, reiumbursement:float):
        """_summary_

        Args:
            back_bet (Bet): 
            lay_bet (Bet): 
            reiumbursement (float): Amount that is going to be received if the back_bet is lost. For example a FB 10€ will result in 7.5€ (assuming 75% freebet retention)
        """
        super().__init__(back_bet, lay_bet)
        self.reiumbursement = reiumbursement

    def calculate_stake(self) -> Dict[str, Any]:
        lb = self.lay_bet
        bb = self.back_bet

        
        raw_lay_stake = (bb.stake*bb.odds*((100-bb.fee)/100)-self.reiumbursement)/(lb.odds-lb.fee/100)
        lb.stake = round(raw_lay_stake,2)
        self.risk = round(lb.stake*(lb.odds-1.0),2)

        return {"lay_stake": lb.stake,"risk":self.risk}
