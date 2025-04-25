from typing import Dict, Any
from back_lay_strategy.back_lay_base_calculator import BackLayCalculator
from bet import Bet

class BackLayRolloverCalculator(BackLayCalculator):
    def __init__(self, back_bet_real: Bet, lay_bet: Bet, bonus:float, remaining_rollover:float,expected_rating:float):
        """_summary_

        Args:
            back_bet_real (Bet): Back bet with total balance.
            lay_bet (Bet): Lay bet.
            bonus (Bet): Ammount of the Back Bet stake made of bonus balance.
            remaining_rollover (float): Remaining rollover (not taking into account back_bet_real stake and back_bet_bonus stake).
            expected_rating (float): Expected rating at which the remaining rollover will be freed (e.g 95.06%).
        """
        super().__init__(back_bet_real, lay_bet)
        self.bonus = bonus
        self.remaining_rollover = remaining_rollover
        self.expected_rating = expected_rating

    def calculate_stake(self) -> Dict[str, Any]:
        lb = self.lay_bet
        bbr = self.back_bet
        bonus = self.bonus
        rr = self.remaining_rollover
        er = self.expected_rating

        
        raw_lay_stake = ((bbr.stake+bonus)*bbr.odds*((100-bbr.fee)/100)-((rr-bbr.stake-bonus)*(1-er/100)))/(lb.odds-lb.fee/100)
        lb.stake = round(raw_lay_stake,2)
        self.risk = round(lb.stake*(lb.odds-1.0),2)

        return {"lay_stake": lb.stake,"risk":self.risk}
