# Matched Betting Calculator

**Matched Betting Calculator** is a Python library designed to perform accurate stake calculations for matched betting strategies. It provides flexible tools for calculating how to hedge bets using two fundamental paradigms:

- **Back-Lay Strategy** – Using a betting exchange to lay against a back bet.
- **Dutching Strategy** – Using multiple bookmakers to cover all outcomes of an event.

Each strategy supports:

- **Simple Bets** – Single-event bets.
- **Accumulator (Combo) Bets** – Multi-event bets.

Each of these betting modes supports the following bet types:

1. **Normal** – Traditional cash bets.
2. **Freebet** – Bet using a bonus stake not returned on win.
3. **Reimbursement** – Partial or full cashback on loss.
4. **Rollover** – Winnings subject to turnover requirements before withdrawal.

---

## About This Project

This project was born out of the necessity for high-quality (tested), **free and open-source matched betting calculators**. After years of experience with matched betting, I realized that most accurate tools are locked behind paywalls, creating a barrier for newcomers and experienced bettors alike.

By building this library, I aim to empower users to take full control of their matched betting strategies—without the need to pay for basic tools (literally few linear equations!). With accurate stake calculation for various bet types and strategies, this package offers everything needed to profit from matched betting using either exchanges or traditional bookmakers.

## Features

- Modular architecture for clean extensibility.
- Symbolic math using `sympy` for solving stake equations.
- Fine-grained control over balance and risk modeling.
- Full test coverage using Python's `unittest` framework. All tests values were validated against the existing pay-walled online Matched Betting tools NinjaBet and Vilibets .

## Installation
To install the project locally:

```bash
git clone https://github.com/oplaco/matched-betting-calculator.git
cd matched-betting-calculator
pip install -r requirements.txt
```

## Usage examples
There is an example folder containing examples on how to use the calculators in different scenarios.
In the near future I will publish a desktop and/or web interfaces to use this repository via an GUI.

## Running tests
python -m unittest discover -s tests

## Contributing

Contributions are welcome! If you'd like to add new features, fix bugs, or suggest improvements, please follow these steps:

1. **Fork** the repository.
2. **Create** a feature branch: `git checkout -b my-feature`.
3. **Commit** your changes with clear and descriptive messages.
4. **Push** to your branch: `git push origin my-feature`.
5. **Open** a pull request on GitHub.

I also welcome suggestions for future development, improvements to existing calculators, or new betting strategies to support. Feel free to open an issue to start a discussion.
