from typing import Dict, Any
from base import CalculatorBase
from bet import BackLeyGroup

class BackLayNormalCalculator(CalculatorBase):
    def __init__(self,back_ley_group:BackLeyGroup):
        self.back_ley_group = back_ley_group

    def calculate_stake(self) -> Dict[str, Any]:
        bb = self.back_ley_group.back_bet
        lb = self.back_ley_group.lay_bet
        
        raw_lay_stake = (bb.stake*bb.odds*((100-bb.fee)/100))/(lb.odds-lb.fee/100)
        lb.stake = round(raw_lay_stake,2)
        self.risk = round(lb.stake*(lb.odds-1),2)

        return {"lay_stake": lb.stake,"risk":self.risk}