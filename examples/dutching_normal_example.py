#!/usr/bin/env python
"""Example script demonstrating the DutchingNormalCalculator functionality."""

# Standard library imports
import os
import sys

# Add parent directory to path
parent_dir = os.path.dirname(__file__)
project_root = os.path.abspath(os.path.join(parent_dir, ".."))
sys.path.insert(0, project_root)

# Local imports - must be after sys.path modification
from matched_betting_calculator.bet import Bet, DutchingGroup
from matched_betting_calculator.dutching_strategy.dutching_simple_calculator import (
    DutchingNormalCalculator,
)


def main():
    # Create a main back bet and two dutching bets
    main_back_bet = Bet(odds=3.0, stake=100.0, fee=5.0)
    dutching_bet_0 = Bet(odds=1.7, fee=2.0)
    dutching_bet_1 = Bet(odds=15.0, fee=2.0)
    dutching_bets = [dutching_bet_0, dutching_bet_1]

    # Create a dutching group
    dutching_group = DutchingGroup(main_back_bet, dutching_bets)

    # Create a calculator
    calc = DutchingNormalCalculator(dutching_group)

    result = calc.calculate_stake()
    print("Default mode - With side effects:")
    print(f"Dutching bet 0 stake: {result['dutching_bet_0_stake']}")
    print(f"Dutching bet 1 stake: {result['dutching_bet_1_stake']}")
    print(f"Overall balance: {result['overall_balance']}")


if __name__ == "__main__":
    main()
