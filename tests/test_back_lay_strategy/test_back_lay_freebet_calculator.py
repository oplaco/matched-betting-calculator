import unittest
from matched_betting_calculator.bet import Bet, BackLayGroup
from matched_betting_calculator.back_lay_strategy.back_lay_simple_calculator import BackLayFreebetCalculator

class TestBackLayFreebetCalculator(unittest.TestCase):

    def test_calculate_lay_stake_basic(self):
        back_bet = Bet(odds=5.0, stake=100, fee=5.0)
        lay_bet = Bet(odds=5.5, fee=2.0)
        back_lay_group = BackLayGroup(back_bet,lay_bet)

        calc = BackLayFreebetCalculator(back_lay_group)
        result = calc.calculate_stake()

        expected_lay_stake = 69.34
        expected_risk = 312.03
        expected_balance = 67.96
        
        self.assertAlmostEqual(result["lay_stake"], expected_lay_stake,delta=0.01)
        self.assertAlmostEqual(result["risk"], expected_risk, delta=0.01)
        self.assertAlmostEqual(result["back_balance"], expected_balance, delta=0.01)
        self.assertAlmostEqual(lay_bet.stake, expected_lay_stake, delta=0.01)

    def test_calculate_lay_stake_no_fees(self):
        back_bet = Bet(odds=3.0, stake=50, fee=0.0)
        lay_bet = Bet(odds=2.8, fee=0.0)
        back_lay_group = BackLayGroup(back_bet,lay_bet)

        calc = BackLayFreebetCalculator(back_lay_group)
        result = calc.calculate_stake()

        expected = 35.71
        expected_risk = 64.28
        expected_balance = 35.71
        
        self.assertAlmostEqual(result["lay_stake"], expected, delta=0.01)
        self.assertAlmostEqual(result["risk"], expected_risk, delta=0.01)
        self.assertAlmostEqual(result["back_balance"], expected_balance, delta=0.01)
        self.assertAlmostEqual(lay_bet.stake, expected, delta=0.01)
