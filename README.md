# TradingAlgorithm
Here I back-tested the the trading strategy based on the following rules of technical indicators.

libraries used:

-talib (for the technical indicators)

-nsepy (for extracting national stock exchange data)

-datetime

-pandas

-numpy
## Algorithm-1
Trading Vehicle and Trade Objective: Equity Swings

Indicators: Market Condition Indicator (to identify the markate trend, range and volatility): - Exponential Moving Average-200

Area of value (where might potential buy/sell opportunity come in):
- Exponential Moving Average-50
- Stochastic-14

Rules: Buying: - Latest trading price, above Exponential Moving Average-200, AND - Latest trading price, above Exponential Moving Average-50, AND - Stochastic %K line value < Stochastic %D line value, AND - Stochastic %K line value < 25 stochastic point

Selling:
	Strategic:
	- Stochastic %K line value < Stochastic %D line value, AND
	- Stochastic %K line value > 70 stochastic point
OR
	Stop-loss:
	- Latest trading price, below Exponential Moving Average-50 by dR% of Latest trading price, OR
	- Latest trading price, below by R% of stock purchase value // %R = Risk percentage

Quantity:
- Decision according to Risk capacity and available fund
