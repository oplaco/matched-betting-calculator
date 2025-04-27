import unittest
from bet import Bet, BackLeyGroup
from back_lay_strategy.accumulated.back_lay_accumulated_normal_calculator import BackLayAccumulatedCalculator

class TestBackLayFreebetCalculator(unittest.TestCase):

    def test_calculate_two_picks_accumulated_lay_stakes(self):
        combo_stake = 100
        back_bet_fee = 5.0
        back_bet_1 = Bet(odds=2, fee=back_bet_fee)
        lay_bet_1 = Bet(odds=2.1, fee=4.0)
        back_bet_2 = Bet(odds=3, fee=back_bet_fee)
        lay_bet_2 = Bet(odds=3.4, fee=4.0)
        blg_1 = BackLeyGroup(back_bet_1,lay_bet_1)
        blg_2 = BackLeyGroup(back_bet_2,lay_bet_2)

        calc = BackLayAccumulatedCalculator(combo_stake,back_bet_fee,[blg_1,blg_2])
        result = calc.calculate_stake()

        expected_lay_stake_1 = 79.06
        expected_lay_stake_2 = 169.642
        # assertions
        self.assertEqual(len(result["accumulated_lay_bets"]), 2)
        self.assertAlmostEqual(result["accumulated_lay_bets"][0]["lay_stake"], expected_lay_stake_1, delta=0.01)
        self.assertAlmostEqual(result["accumulated_lay_bets"][1]["lay_stake"], expected_lay_stake_2, delta=0.01)
        
    
    def test_calculate_four_picks_accumulated_lay_stakes(self):
        combo_stake = 20
        back_bet_fee = 1.1
        
        back_bet_1 = Bet(odds=3, fee=back_bet_fee)
        lay_bet_1 = Bet(odds=3.2, fee=1.0)
        back_bet_2 = Bet(odds=2, fee=back_bet_fee)
        lay_bet_2 = Bet(odds=1.9, fee=0)
        back_bet_3 = Bet(odds=4, fee=back_bet_fee)
        lay_bet_3 = Bet(odds=4, fee=3.0)
        back_bet_4 = Bet(odds=5, fee=back_bet_fee)
        lay_bet_4 = Bet(odds=6, fee=4.0)
        
        
        blg_1 = BackLeyGroup(back_bet_1,lay_bet_1)
        blg_2 = BackLeyGroup(back_bet_2,lay_bet_2)
        blg_3 = BackLeyGroup(back_bet_3,lay_bet_3)
        blg_4 = BackLeyGroup(back_bet_4,lay_bet_4)

        calc = BackLayAccumulatedCalculator(combo_stake,back_bet_fee,[blg_1,blg_2,blg_3,blg_4])
        result = calc.calculate_stake()

        expected_lay_stake_1 = 15.41
        expected_lay_stake_2 = 49.17
        expected_lay_stake_3 = 96.3
        expected_lay_stake_4 = 398.26
        # assertions
        self.assertEqual(len(result["accumulated_lay_bets"]), 4)
        self.assertAlmostEqual(result["accumulated_lay_bets"][0]["lay_stake"], expected_lay_stake_1, delta=0.01)
        self.assertAlmostEqual(result["accumulated_lay_bets"][1]["lay_stake"], expected_lay_stake_2, delta=0.01)
        self.assertAlmostEqual(result["accumulated_lay_bets"][2]["lay_stake"], expected_lay_stake_3, delta=0.01)
        self.assertAlmostEqual(result["accumulated_lay_bets"][3]["lay_stake"], expected_lay_stake_4, delta=0.01)

if __name__ == "__main__":
    unittest.main()