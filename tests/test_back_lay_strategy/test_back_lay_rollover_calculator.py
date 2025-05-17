import unittest
from matched_betting_calculator.bet import Bet, BackLayGroup
from matched_betting_calculator.back_lay_strategy.back_lay_simple_calculator import (
    BackLayRolloverCalculator,
)


class TestBackLayRolloverCalculator(unittest.TestCase):

    def test_calculate_lay_stake_basic(self):
        back_bet = Bet(odds=2, stake=100, fee=5.0)
        lay_bet = Bet(odds=2.1, fee=2.0)
        back_lay_group = BackLayGroup(back_bet, lay_bet)
        bonus_amount = 100
        remaining_rollover = 1000
        expected_rating = 95

        calc = BackLayRolloverCalculator(
            back_lay_group, bonus_amount, remaining_rollover, expected_rating
        )
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
        back_lay_group = BackLayGroup(back_bet, lay_bet)
        bonus_amount = 150
        remaining_rollover = 2000
        expected_rating = 90

        calc = BackLayRolloverCalculator(
            back_lay_group, bonus_amount, remaining_rollover, expected_rating
        )
        result = calc.calculate_stake()

        expected_lay_stake = 354.76
        expected_risk = 390.24
        expected_balance = 54.76

        self.assertAlmostEqual(result["lay_stake"], expected_lay_stake, delta=0.01)
        self.assertAlmostEqual(result["risk"], expected_risk, delta=0.01)
        self.assertAlmostEqual(result["back_balance"], expected_balance, delta=0.01)

    def test_calculate_lay_stake_with_small_remaining_rollover(self):
        """Test when remaining_rollover is less than the sum of stake and bonus.
        This tests the fix to ensure rollover_penalty is never negative."""
        back_bet = Bet(odds=2, stake=100)
        lay_bet = Bet(odds=2.1)
        back_lay_group = BackLayGroup(back_bet, lay_bet)
        bonus_amount = 50
        # Remaining rollover is less than stake + bonus (100 + 50)
        remaining_rollover = 120
        expected_rating = 90

        calc = BackLayRolloverCalculator(
            back_lay_group, bonus_amount, remaining_rollover, expected_rating
        )
        result = calc.calculate_stake()

        # Since remaining_rollover (120) - stake (100) - bonus (50) = -30,
        # the rollover_penalty would have been negative without the fix.
        # With the fix, rollover_penalty should be 0, resulting in a higher back_balance.

        # Check that the back_balance reflects the correct calculation with no negative penalty
        # Also check the lay_stake is positive and correctly assigned
        self.assertGreaterEqual(
            result["back_balance"],
            0,
            msg="Back balance should not be negative with small remaining rollover",
        )
        self.assertGreater(
            result["lay_stake"], 0, msg="Lay stake should be a positive value"
        )
        self.assertAlmostEqual(
            lay_bet.stake,
            result["lay_stake"],
            delta=0.01,
            msg="Lay bet stake should match calculated lay stake",
        )
