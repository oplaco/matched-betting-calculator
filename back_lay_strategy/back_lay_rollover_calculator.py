from typing import Dict, Any
from base import CalculatorBase
from bet import BackLeyGroup

class BackLayRolloverCalculator(CalculatorBase):
    def __init__(self, back_ley_group:BackLeyGroup, bonus_amount:float, remaining_rollover:float,expected_rating:float):
        """_summary_

        Args:
            back_ley_group (BackLeyGroup): 
            bonus_amount (float): Ammount of the Back Bet stake made of bonus_amount balance.
            remaining_rollover (float): Remaining rollover (not taking into account back_bet_real stake and back_bet_bonus_amount stake).
            expected_rating (float): Expected rating at which the remaining rollover will be freed (e.g 95.06%).
        """

        if not (0 <= expected_rating <= 100):
            raise ValueError("Expected rating must be between 0 and 100.")
        
        self.back_ley_group = back_ley_group
        self.bonus_amount = bonus_amount
        self.remaining_rollover = remaining_rollover
        self.expected_rating = expected_rating

    def calculate_stake(self) -> Dict[str, Any]:
        bbr = self.back_ley_group.back_bet
        lb = self.back_ley_group.lay_bet
        bonus_amount = self.bonus_amount
        rr = self.remaining_rollover
        er = self.expected_rating

        
        raw_lay_stake = ((bbr.stake+bonus_amount)*bbr.odds*((100-bbr.fee)/100)-((rr-bbr.stake-bonus_amount)*(1-er/100)))/(lb.odds-lb.fee/100)
        lb.stake = round(raw_lay_stake,2)
        self.risk = round(lb.stake*(lb.odds-1.0),2)

        return {"lay_stake": lb.stake,"risk":self.risk}
