import unittest
from matched_betting_calculator.bet import Bet, BackLayGroup
from matched_betting_calculator.back_lay_strategy.back_lay_simple_calculator import BackLayReimbursementCalculator

class TestBackLayReimbursementCalculator(unittest.TestCase):

    def test_calculate_lay_stake_basic(self):
        back_bet = Bet(odds=5.0, stake=100, fee=5.0)
        lay_bet = Bet(odds=5.5, fee=2.0)
        back_lay_group = BackLayGroup(back_bet,lay_bet)
        reimbursement = 70

        calc = BackLayReimbursementCalculator(back_lay_group,reimbursement)
        result = calc.calculate_stake()

        expected_lay_stake = 73.91
        expected_risk = 332.6
        expected_balance = 42.43
        
        self.assertAlmostEqual(result["lay_stake"], expected_lay_stake, delta=0.01)
        self.assertAlmostEqual(result["risk"], expected_risk, delta=0.011)
        self.assertAlmostEqual(result["back_balance"], expected_balance, delta=0.01)
        self.assertAlmostEqual(lay_bet.stake, expected_lay_stake, delta=0.01)

    def test_calculate_lay_stake_no_fees(self):
        back_bet = Bet(odds=3.0, stake=50, fee=0.0)
        lay_bet = Bet(odds=2.8, fee=0.0)
        back_lay_group = BackLayGroup(back_bet,lay_bet)
        reimbursement = 25

        calc = BackLayReimbursementCalculator(back_lay_group,reimbursement)
        result = calc.calculate_stake()

        expected = 44.64
        expected_risk = 80.35
        expected_balance = 19.64
        
        self.assertAlmostEqual(result["lay_stake"], expected, delta=0.01)
        self.assertAlmostEqual(result["risk"], expected_risk, delta=0.01)
        self.assertAlmostEqual(result["back_balance"], expected_balance, delta=0.01)
        self.assertAlmostEqual(lay_bet.stake, expected, delta=0.01)
