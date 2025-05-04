import unittest
from bet import Bet, DutchingGroup
from dutching_strategy.dutching_simple_calculator import DutchingRolloverCalculator

class TestDutchingRolloverCalculator(unittest.TestCase):

    def test_calculate_dutching_stakes_no_fees(self):
        main_back_bet = Bet(odds=3.0, stake=100.0,fee=5)
        dutching_bet_0 = Bet(odds=1.4,fee=3)
        db = [dutching_bet_0]
        
        dutching_group = DutchingGroup(main_back_bet,db)
        bonus_amount = 75
        remaining_rollover = 800 
        expected_rating = 92
        
        calc = DutchingRolloverCalculator(dutching_group, bonus_amount,remaining_rollover,expected_rating)
        result = calc.calculate_stake()

        expected_dutching_stake = [330.45]
        expected_overall_balance = 18.3
        
        for i in range(len(db)):
            self.assertAlmostEqual(result[f"dutching_bet_{i}_stake"], expected_dutching_stake[i], delta=0.01)
    
        self.assertAlmostEqual(result["overall_balance"], expected_overall_balance, delta=0.01)
        