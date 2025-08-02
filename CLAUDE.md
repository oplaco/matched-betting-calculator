# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

A Python library for matched betting calculations supporting back-lay and dutching strategies. Uses symbolic math with `sympy` to solve stake equations for various bet types (normal, freebet, reimbursement, rollover).

## Development Commands

### Testing
```bash
python -m unittest discover -s tests
```

### Code Formatting (CI requirement)
```bash
black .
```

### Installation
```bash
pip install -r requirements.txt
```

### Running Examples
```bash
python examples/back_lay_normal_example.py
python examples/back_lay_rollover_example.py
python examples/dutching_normal_example.py
```

## Architecture

### Core Components

- **Base Classes**: `CalculatorBase` (matched_betting_calculator/base.py) - abstract base for all calculators
- **Bet Models**: `Bet`, `BackLayGroup`, `DutchingGroup` (matched_betting_calculator/bet.py) - data structures for bets
- **Factory Pattern**: `CalculatorFactory` (matched_betting_calculator/factory.py) - creates calculator instances

### Strategy Structure

**Back-Lay Strategy** (`matched_betting_calculator/back_lay_strategy/`):
- `back_lay_simple_calculator.py` - single event calculators (Normal, Freebet, Reimbursement, Rollover)
- `back_lay_accumulated_calculator.py` - accumulator/combo bet calculators

**Dutching Strategy** (`matched_betting_calculator/dutching_strategy/`):
- `dutching_simple_calculator.py` - multiple bookmaker calculators

### Key Design Patterns

1. **Factory Pattern**: Use `CalculatorFactory.create_back_lay_calculator()` or `create_dutching_calculator()` to instantiate calculators
2. **Strategy Pattern**: Each calculator type implements `CalculatorBase.calculate_stake()` returning standardized results
3. **Data Classes**: `Bet` objects with validation in `__post_init__()`

### Dependencies

- `sympy>=1.14` - symbolic mathematics for solving stake equations
- Standard library only otherwise

### Testing

Uses Python's built-in `unittest` framework. All test values validated against commercial tools (NinjaBet, Vilibets). Test structure mirrors source structure under `tests/`.