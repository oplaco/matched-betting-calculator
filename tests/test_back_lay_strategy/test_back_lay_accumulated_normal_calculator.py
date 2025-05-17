import unittest
from matched_betting_calculator.bet import Bet, BackLayGroup
from matched_betting_calculator.back_lay_strategy.back_lay_accumulated_calculator import (
    BackLayAccumulatedNormalCalculator,
    BackLayAccumulatedFreebetCalculator,
    BackLayAccumulatedReimbursementCalculator,
)


class TestBackLayAccumulatedCalculator(unittest.TestCase):
    def setUp(self):
        # First accumulated example
        self.acc1_combo_stake = 100
        self.acc1_back_bet_fee = 5.0

        back_bet_1 = Bet(odds=2, fee=self.acc1_back_bet_fee)
        lay_bet_1 = Bet(odds=2.1, fee=4.0)
        back_bet_2 = Bet(odds=3, fee=self.acc1_back_bet_fee)
        lay_bet_2 = Bet(odds=3.4, fee=4.0)
        blg_1 = BackLayGroup(back_bet_1, lay_bet_1)
        blg_2 = BackLayGroup(back_bet_2, lay_bet_2)

        self.acc1_bl_group = [blg_1, blg_2]

        # Second accumulated example
        self.acc2_combo_stake = 20
        self.acc2_back_bet_fee = 1.1

        back_bet_1 = Bet(odds=3, fee=self.acc2_back_bet_fee)
        lay_bet_1 = Bet(odds=3.2, fee=1.0)
        back_bet_2 = Bet(odds=2, fee=self.acc2_back_bet_fee)
        lay_bet_2 = Bet(odds=1.9, fee=0)
        back_bet_3 = Bet(odds=4, fee=self.acc2_back_bet_fee)
        lay_bet_3 = Bet(odds=4, fee=3.0)
        back_bet_4 = Bet(odds=5, fee=self.acc2_back_bet_fee)
        lay_bet_4 = Bet(odds=6, fee=4.0)

        blg_1 = BackLayGroup(back_bet_1, lay_bet_1)
        blg_2 = BackLayGroup(back_bet_2, lay_bet_2)
        blg_3 = BackLayGroup(back_bet_3, lay_bet_3)
        blg_4 = BackLayGroup(back_bet_4, lay_bet_4)

        self.acc2_bl_group = [blg_1, blg_2, blg_3, blg_4]

    def test_calculate_two_picks_accumulated_normal(self):
        calc = BackLayAccumulatedNormalCalculator(
            self.acc1_combo_stake, self.acc1_back_bet_fee, self.acc1_bl_group
        )
        result = calc.calculate_stake()

        expected_lay_stake_1 = 79.06
        expected_lay_stake_2 = 169.642
        # assertions
        self.assertEqual(len(result["accumulated_lay_bets"]), 2)
        self.assertAlmostEqual(
            result["accumulated_lay_bets"][0]["lay_stake"],
            expected_lay_stake_1,
            delta=0.01,
        )
        self.assertAlmostEqual(
            result["accumulated_lay_bets"][1]["lay_stake"],
            expected_lay_stake_2,
            delta=0.01,
        )

    def test_calculate_four_picks_accumulated_normal(self):
        calc = BackLayAccumulatedNormalCalculator(
            self.acc2_combo_stake, self.acc2_back_bet_fee, self.acc2_bl_group
        )
        result = calc.calculate_stake()

        expected_lay_stake_1 = 15.41
        expected_lay_stake_2 = 49.17
        expected_lay_stake_3 = 96.3
        expected_lay_stake_4 = 398.26
        # assertions
        self.assertEqual(len(result["accumulated_lay_bets"]), 4)
        self.assertAlmostEqual(
            result["accumulated_lay_bets"][0]["lay_stake"],
            expected_lay_stake_1,
            delta=0.01,
        )
        self.assertAlmostEqual(
            result["accumulated_lay_bets"][1]["lay_stake"],
            expected_lay_stake_2,
            delta=0.01,
        )
        self.assertAlmostEqual(
            result["accumulated_lay_bets"][2]["lay_stake"],
            expected_lay_stake_3,
            delta=0.01,
        )
        self.assertAlmostEqual(
            result["accumulated_lay_bets"][3]["lay_stake"],
            expected_lay_stake_4,
            delta=0.01,
        )

    def test_calculate_two_picks_accumulated_freebet(self):
        calc = BackLayAccumulatedFreebetCalculator(
            self.acc1_combo_stake, self.acc1_back_bet_fee, self.acc1_bl_group
        )
        result = calc.calculate_stake()

        expected_lay_stake_1 = 65.88
        expected_lay_stake_2 = 141.37
        # assertions
        self.assertEqual(len(result["accumulated_lay_bets"]), 2)
        self.assertAlmostEqual(
            result["accumulated_lay_bets"][0]["lay_stake"],
            expected_lay_stake_1,
            delta=0.01,
        )
        self.assertAlmostEqual(
            result["accumulated_lay_bets"][1]["lay_stake"],
            expected_lay_stake_2,
            delta=0.01,
        )

    def test_calculate_four_picks_accumulated_freebet(self):
        calc = BackLayAccumulatedFreebetCalculator(
            self.acc2_combo_stake, self.acc2_back_bet_fee, self.acc2_bl_group
        )
        result = calc.calculate_stake()

        expected_lay_stake_1 = 15.28
        expected_lay_stake_2 = 48.76
        expected_lay_stake_3 = 95.5
        expected_lay_stake_4 = 394.94
        # assertions
        self.assertEqual(len(result["accumulated_lay_bets"]), 4)
        self.assertAlmostEqual(
            result["accumulated_lay_bets"][0]["lay_stake"],
            expected_lay_stake_1,
            delta=0.01,
        )
        self.assertAlmostEqual(
            result["accumulated_lay_bets"][1]["lay_stake"],
            expected_lay_stake_2,
            delta=0.01,
        )
        self.assertAlmostEqual(
            result["accumulated_lay_bets"][2]["lay_stake"],
            expected_lay_stake_3,
            delta=0.01,
        )
        self.assertAlmostEqual(
            result["accumulated_lay_bets"][3]["lay_stake"],
            expected_lay_stake_4,
            delta=0.01,
        )

    def test_calculate_two_picks_accumulated_reimbursement(self):
        reimbursement = 50
        calc = BackLayAccumulatedReimbursementCalculator(
            self.acc1_combo_stake,
            self.acc1_back_bet_fee,
            self.acc1_bl_group,
            reimbursement,
        )
        result = calc.calculate_stake()

        expected_lay_stake_1 = 72.12
        expected_lay_stake_2 = 154.76
        # assertions
        self.assertEqual(len(result["accumulated_lay_bets"]), 2)
        self.assertAlmostEqual(
            result["accumulated_lay_bets"][0]["lay_stake"],
            expected_lay_stake_1,
            delta=0.01,
        )
        self.assertAlmostEqual(
            result["accumulated_lay_bets"][1]["lay_stake"],
            expected_lay_stake_2,
            delta=0.01,
        )

    def test_calculate_four_picks_accumulated_reimbursement(self):
        combo_stake = 50
        reimbursement = 25
        calc = BackLayAccumulatedReimbursementCalculator(
            combo_stake, self.acc2_back_bet_fee, self.acc2_bl_group, reimbursement
        )
        result = calc.calculate_stake()

        expected_lay_stake_1 = 38.37
        expected_lay_stake_2 = 122.4
        expected_lay_stake_3 = 239.74
        expected_lay_stake_4 = 991.44
        # assertions
        self.assertEqual(len(result["accumulated_lay_bets"]), 4)
        self.assertAlmostEqual(
            result["accumulated_lay_bets"][0]["lay_stake"],
            expected_lay_stake_1,
            delta=0.01,
        )
        self.assertAlmostEqual(
            result["accumulated_lay_bets"][1]["lay_stake"],
            expected_lay_stake_2,
            delta=0.01,
        )
        self.assertAlmostEqual(
            result["accumulated_lay_bets"][2]["lay_stake"],
            expected_lay_stake_3,
            delta=0.01,
        )
        self.assertAlmostEqual(
            result["accumulated_lay_bets"][3]["lay_stake"],
            expected_lay_stake_4,
            delta=0.01,
        )
