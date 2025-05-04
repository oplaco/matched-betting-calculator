import unittest
from matched_betting_calculator.bet import Bet, DutchingGroup
from matched_betting_calculator.dutching_strategy.dutching_simple_calculator import DutchingReimbursementCalculator

class TestDutchingReimbursementCalculator(unittest.TestCase):

    def test_calculate_dutching_stakes_no_fees(self):
        reimbursement = 75
        main_back_bet = Bet(odds=3.0, stake=100.0)
        dutching_bet_0 = Bet(odds=1.7)
        dutching_bet_1 = Bet(odds=15)
        db = [dutching_bet_0,dutching_bet_1]
        
        dutching_group = DutchingGroup(main_back_bet,db)
        
        calc = DutchingReimbursementCalculator(dutching_group,reimbursement)
        result = calc.calculate_stake()

        expected_dutching_stake = [132.35,15]
        expected_overall_balance = 52.65
        
        for i in range(len(db)):
            self.assertAlmostEqual(result[f"dutching_bet_{i}_stake"], expected_dutching_stake[i], delta=0.01)
    
        self.assertAlmostEqual(result["overall_balance"], expected_overall_balance, delta=0.01)
        
    def test_calculate_dutching_stakes_with_fees(self):
        reimbursement = 75
        main_back_bet = Bet(odds=3.0, stake=75.0,fee=5)
        dutching_bet_0 = Bet(odds=1.4,fee=5.3)
        
        db = [dutching_bet_0]
        
        dutching_group = DutchingGroup(main_back_bet,db)
        
        calc = DutchingReimbursementCalculator(dutching_group,reimbursement)
        result = calc.calculate_stake()

        expected_dutching_stake = [104.65]
        expected_overall_balance = 34.1
        
        for i in range(len(db)):
            self.assertAlmostEqual(result[f"dutching_bet_{i}_stake"], expected_dutching_stake[i], delta=0.01)
    
        self.assertAlmostEqual(result["overall_balance"], expected_overall_balance, delta=0.01)
    
