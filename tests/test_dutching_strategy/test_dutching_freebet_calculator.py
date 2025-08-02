import unittest
from matched_betting_calculator.bet import Bet, DutchingGroup
from matched_betting_calculator.dutching_strategy.dutching_simple_calculator import (
    DutchingFreebetCalculator,
)


class TestDutchingFreebetCalculator(unittest.TestCase):

    def test_calculate_dutching_stakes_no_fees(self):
        main_back_bet = Bet(odds=3.0, stake=100.0)
        dutching_bet_0 = Bet(odds=1.7)
        dutching_bet_1 = Bet(odds=15)
        db = [dutching_bet_0, dutching_bet_1]

        dutching_group = DutchingGroup(main_back_bet, db)

        calc = DutchingFreebetCalculator(dutching_group)
        result = calc.calculate_stake()

        expected_dutching_stake = [117.65, 13.33]
        expected_overall_balance = 69.02

        for i in range(len(db)):
            self.assertAlmostEqual(
                result[f"dutching_bet_{i}_stake"],
                expected_dutching_stake[i],
                delta=0.01,
            )

        self.assertAlmostEqual(
            result["overall_balance"], expected_overall_balance, delta=0.01
        )

    def test_calculate_dutching_stakes_with_fees(self):
        main_back_bet = Bet(odds=3.0, stake=75.0, fee=5)
        dutching_bet_0 = Bet(odds=1.4, fee=5.3)

        db = [dutching_bet_0]

        dutching_group = DutchingGroup(main_back_bet, db)

        calc = DutchingFreebetCalculator(dutching_group)
        result = calc.calculate_stake()

        expected_dutching_stake = [107.48]
        expected_overall_balance = 35.02

        for i in range(len(db)):
            self.assertAlmostEqual(
                result[f"dutching_bet_{i}_stake"],
                expected_dutching_stake[i],
                delta=0.01,
            )

        self.assertAlmostEqual(
            result["overall_balance"], expected_overall_balance, delta=0.01
        )
