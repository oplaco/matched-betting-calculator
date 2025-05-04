import unittest
from bet import Bet, BackLeyGroup
from back_lay_strategy.back_lay_simple_calculator import BackLayRolloverCalculator

class TestBackLayRolloverCalculator(unittest.TestCase):

    def test_calculate_lay_stake_basic(self):
        back_bet = Bet(odds=2, stake=100, fee=5.0)
        lay_bet = Bet(odds=2.1, fee=2.0)
        back_lay_group = BackLeyGroup(back_bet,lay_bet)
        bonus_amount = 100
        remaining_rollover = 1000
        expected_rating = 95

        calc = BackLayRolloverCalculator(back_lay_group,bonus_amount,remaining_rollover,expected_rating)
        result = calc.calculate_stake()

        expected_lay_stake = 163.46
        expected_risk = 179.81
        expected_balance = 60.19
        
        self.assertAlmostEqual(result["lay_stake"], expected_lay_stake, delta=0.01)
        self.assertAlmostEqual(result["risk"], expected_risk, delta=0.01)
        self.assertAlmostEqual(result["back_balance"], expected_balance, delta=0.01)
        self.assertAlmostEqual(lay_bet.stake, expected_lay_stake, delta=0.01)
        
    def test_calculate_lay_stake_no_fees(self):
        back_bet = Bet(odds=2, stake=300)
        lay_bet = Bet(odds=2.1)
        back_lay_group = BackLeyGroup(back_bet,lay_bet)
        bonus_amount = 150
        remaining_rollover = 2000
        expected_rating = 90

        calc = BackLayRolloverCalculator(back_lay_group,bonus_amount,remaining_rollover,expected_rating)
        result = calc.calculate_stake()

        expected_lay_stake = 354.76
        expected_risk = 390.24
        expected_balance = 54.76
        
        self.assertAlmostEqual(result["lay_stake"], expected_lay_stake, delta=0.01)
        self.assertAlmostEqual(result["risk"], expected_risk, delta=0.01)
        self.assertAlmostEqual(result["back_balance"], expected_balance, delta=0.01)
        self.assertAlmostEqual(lay_bet.stake, expected_lay_stake, delta=0.01)