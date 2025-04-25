from typing import Dict, Any
from back_lay_strategy.back_lay_base_calculator import BackLayCalculator
from bet import Bet

class BackLayNormalCalculator(BackLayCalculator):
    def __init__(self, back_bet: Bet, lay_bet: Bet):
        super().__init__(back_bet, lay_bet)

    def calculate_stake(self) -> Dict[str, Any]:
        lb = self.lay_bet
        bb = self.back_bet
        
        raw_lay_stake = (bb.stake*bb.odds*((100-bb.fee)/100))/(lb.odds-lb.fee/100)
        lb.stake = round(raw_lay_stake,2)
        self.risk = round(lb.stake*(lb.odds-1),2)

        return {"lay_stake": lb.stake,"risk":self.risk}