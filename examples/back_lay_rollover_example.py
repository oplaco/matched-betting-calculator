#!/usr/bin/env python
"""Example script demonstrating the BackLayNormalCalculator functionality."""

# Standard library imports
import os
import sys

# Add parent directory to path
parent_dir = os.path.dirname(__file__)
project_root = os.path.abspath(os.path.join(parent_dir, ".."))
sys.path.insert(0, project_root)

# Local imports - must be after sys.path modification
from matched_betting_calculator.bet import Bet, BackLayGroup
from matched_betting_calculator.back_lay_strategy.back_lay_simple_calculator import (
    BackLayRolloverCalculator,
)


def main():
    back_bet = Bet(odds=3.2, stake=400, fee=0)  # 5% fee
    lay_bet = Bet(odds=3.3, fee=2.0)  # stake will be calculated
    back_lay_group = BackLayGroup(back_bet, lay_bet)
    bonus_ammount = 0
    remaining_rollover = 1200
    expected_rating = 94
    calc = BackLayRolloverCalculator(
        back_lay_group, bonus_ammount, remaining_rollover, expected_rating
    )

    result = calc.calculate_stake()
    print("Lay Stake:", result["lay_stake"])
    print("Risk:", result["risk"])
    print("Back Balance", result["back_balance"])
    print("Lay Balance", result["lay_balance"])


if __name__ == "__main__":
    main()
