import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from matched_betting_calculator.bet import Bet, BackLayGroup
from matched_betting_calculator.back_lay_strategy.back_lay_simple_calculator import BackLayNormalCalculator

def main():
    back_bet = Bet(odds=2.0, stake=100, fee=5.0)  # 5% fee
    lay_bet = Bet(odds=2.1, fee=2.0)  # stake will be calculated
    back_lay_group = BackLayGroup(back_bet,lay_bet)
    calc = BackLayNormalCalculator(back_lay_group)
    result = calc.calculate_stake()

    print("Lay Stake:", result["lay_stake"])
    print("Risk:", result["risk"])

if __name__ == "__main__":
    main()
