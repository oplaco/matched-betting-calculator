from typing import Dict, Any
from base import CalculatorBase
from bet import BackLeyGroup

class BackLayFrebetCalculator(CalculatorBase):
    def __init__(self,back_ley_group:BackLeyGroup):
        self.back_ley_group = back_ley_group

    def calculate_stake(self) -> Dict[str, Any]:
        bb = self.back_ley_group.back_bet
        lb = self.back_ley_group.lay_bet
        
        raw_lay_stake = (bb.stake * (bb.odds - 1.0) * (100.0 - bb.fee)) / (100.0 * lb.odds - lb.fee)
        lb.stake = round(raw_lay_stake,2)
        self.risk = round(lb.stake*(lb.odds-1.0),2)

        return {"lay_stake": lb.stake,"risk":self.risk}
