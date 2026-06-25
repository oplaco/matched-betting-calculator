import unittest
from matched_betting_calculator.bet import Bet, BackLayGroup
from matched_betting_calculator.back_lay_strategy.back_lay_simple_calculator import (
    BackLayWinBonusCalculator,
)


class TestBackLayWinBonusCalculator(unittest.TestCase):

    def test_calculate_lay_stake_basic(self):
        back_bet = Bet(odds=5.0, stake=50, fee=0)
        lay_bet = Bet(odds=5.5, fee=2.0)
        back_lay_group = BackLayGroup(back_bet, lay_bet)
        win_bonus = 18.75

        calc = BackLayWinBonusCalculator(back_lay_group, win_bonus)
        result = calc.calculate_stake()

        expected_lay_stake = 49.04
        expected_risk = 220.68
        expected_back_balance = -1.93
        expected_lay_balance = -1.94

        self.assertAlmostEqual(result["lay_stake"], expected_lay_stake, delta=0.01)
        self.assertAlmostEqual(result["risk"], expected_risk, delta=0.01)
        self.assertAlmostEqual(result["back_balance"], expected_back_balance, delta=0.01)
        self.assertAlmostEqual(result["lay_balance"], expected_lay_balance, delta=0.01)
        self.assertAlmostEqual(lay_bet.stake, expected_lay_stake, delta=0.01)

