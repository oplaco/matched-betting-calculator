from abc import ABC
from typing import Dict, Any
from base import CalculatorBase
from bet import Bet


class BackLayCalculator(CalculatorBase, ABC):
    def __init__(self, back_bet: Bet, lay_bet: Bet):
        self.back_bet = back_bet
        self.lay_bet = lay_bet