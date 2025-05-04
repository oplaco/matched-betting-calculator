import unittest
from matched_betting_calculator.bet import Bet, BackLayGroup
from matched_betting_calculator.back_lay_strategy.back_lay_simple_calculator import BackLayNormalCalculator

class TestBackLayNormalCalculator(unittest.TestCase):

    def test_calculate_lay_stake_basic(self):
        back_bet = Bet(odds=2.0, stake=100.0, fee=5.0)
        lay_bet = Bet(odds=2.1, fee=20.0)
        back_lay_group = BackLayGroup(back_bet,lay_bet)
        
        calc = BackLayNormalCalculator(back_lay_group)
        result = calc.calculate_stake()

        expected_lay_stake = 100
        expected_risk = 110
        expected_balance = -20
        
        self.assertAlmostEqual(result["lay_stake"], expected_lay_stake, delta=0.01)
        self.assertAlmostEqual(result["risk"], expected_risk, delta=0.01)
        self.assertAlmostEqual(result["back_balance"], expected_balance, delta=0.01)
        self.assertAlmostEqual(lay_bet.stake, expected_lay_stake, delta=0.01)
        

    def test_calculate_lay_stake_no_fees(self):
        back_bet = Bet(odds=3.0, stake=50, fee=0.0)
        lay_bet = Bet(odds=2.8, fee=0.0)
        back_lay_group = BackLayGroup(back_bet,lay_bet)

        calc = BackLayNormalCalculator(back_lay_group)
        result = calc.calculate_stake()

        expected_lay_stake = 53.57
        expected_risk = 96.43
        expected_balance = 3.57
        
        self.assertAlmostEqual(result["lay_stake"], expected_lay_stake, delta=0.01)
        self.assertAlmostEqual(result["risk"], expected_risk, delta=0.01)
        self.assertAlmostEqual(result["back_balance"], expected_balance, delta=0.01)
        self.assertAlmostEqual(lay_bet.stake, expected_lay_stake, delta=0.01)
