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
    BackLayNormalCalculator,
)


def main():
    back_bet = Bet(odds=2.0, stake=10, fee=5)
    lay_bet = Bet(odds=2.1, fee=2.0)
    back_lay_group = BackLayGroup(back_bet, lay_bet)
    calc = BackLayNormalCalculator(back_lay_group)

    result = calc.calculate_stake()
    print("Lay Stake:", result["lay_stake"])
    print("Risk:", result["risk"])
    print("Lay Balance:", result["lay_balance"])


if __name__ == "__main__":
    main()
