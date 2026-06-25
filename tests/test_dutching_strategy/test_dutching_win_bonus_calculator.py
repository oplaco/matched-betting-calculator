import unittest

from matched_betting_calculator.bet import Bet, DutchingGroup
from matched_betting_calculator.dutching_strategy.dutching_simple_calculator import (
    DutchingWinBonusCalculator,
)
from matched_betting_calculator.errors import ValidationError
from matched_betting_calculator.factory import CalculatorFactory


class TestDutchingWinBonusCalculator(unittest.TestCase):

    def test_calculate_dutching_stakes_no_fees(self):
        win_bonus = 75
        main_back_bet = Bet(odds=3.0, stake=100.0)
        dutching_bet_0 = Bet(odds=1.7)
        dutching_bet_1 = Bet(odds=15)
        db = [dutching_bet_0, dutching_bet_1]

        dutching_group = DutchingGroup(main_back_bet, db)

        calc = DutchingWinBonusCalculator(dutching_group, win_bonus)
        result = calc.calculate_stake()

        expected_dutching_stake = [220.59, 25.0]
        expected_overall_balance = 29.41

        for i in range(len(db)):
            self.assertAlmostEqual(
                result[f"dutching_bet_{i}_stake"],
                expected_dutching_stake[i],
                delta=0.01,
            )
            self.assertAlmostEqual(db[i].stake, expected_dutching_stake[i], delta=0.01)

        self.assertAlmostEqual(
            result["overall_balance"], expected_overall_balance, delta=0.01
        )
        
    def test_calculate_dutching_stakes_no_fees_manually_validated(self):
        """Numbers were verified on paper for this test.
        """
        win_bonus = 18.75
        main_back_bet = Bet(odds=2.9, stake=50.0)
        dutching_bet_0 = Bet(odds=2.8)
        dutching_bet_1 = Bet(odds=2.95)
        db = [dutching_bet_0, dutching_bet_1]

        dutching_group = DutchingGroup(main_back_bet, db)

        calc = DutchingWinBonusCalculator(dutching_group, win_bonus)
        result = calc.calculate_stake()

        expected_dutching_stake = [58.48, 55.51]
        expected_overall_balance = -0.24

        for i in range(len(db)):
            self.assertAlmostEqual(
                result[f"dutching_bet_{i}_stake"],
                expected_dutching_stake[i],
                delta=0.01,
            )
            self.assertAlmostEqual(db[i].stake, expected_dutching_stake[i], delta=0.01)

        self.assertAlmostEqual(
            result["overall_balance"], expected_overall_balance, delta=0.01
        )

    def test_calculate_dutching_stakes_with_fees(self):
        win_bonus = 75
        main_back_bet = Bet(odds=3.0, stake=75.0, fee=5)
        dutching_bet_0 = Bet(odds=1.4, fee=5.3)

        db = [dutching_bet_0]

        dutching_group = DutchingGroup(main_back_bet, db)

        calc = DutchingWinBonusCalculator(dutching_group, win_bonus)
        result = calc.calculate_stake()

        expected_dutching_stake = [217.79]
        expected_overall_balance = -4.04

        for i in range(len(db)):
            self.assertAlmostEqual(
                result[f"dutching_bet_{i}_stake"],
                expected_dutching_stake[i],
                delta=0.01,
            )

        self.assertAlmostEqual(
            result["overall_balance"], expected_overall_balance, delta=0.01
        )

    def test_negative_win_bonus_raises_validation_error(self):
        dutching_group = DutchingGroup(Bet(odds=3.0, stake=100.0), [Bet(odds=1.7)])

        with self.assertRaises(ValidationError):
            DutchingWinBonusCalculator(dutching_group, -1)

    def test_factory_creates_dutching_win_bonus_calculator(self):
        dutching_group = DutchingGroup(Bet(odds=3.0, stake=100.0), [Bet(odds=1.7)])

        calc = CalculatorFactory.create_dutching_calculator(
            "win_bonus", dutching_group, win_bonus=75
        )

        self.assertIsInstance(calc, DutchingWinBonusCalculator)


if __name__ == "__main__":
    unittest.main()

