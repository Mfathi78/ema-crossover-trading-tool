# ema-crossover-trading-tool

Technical analysis tool with EMA crossover indicator for M5/M15 timeframes.

## Installation

```bash
pip install -r requirements.txt
```

## Features

- EMA, DEMA, and TEMA indicator variants
- Golden Cross / Death Cross signals: BUY (1), SELL (-1), HOLD (0)
- Data loading from CSV/JSON with OHLCV validation and resampling
- M5 and M15 strategy presets
- Backtesting metrics:
  - Total return %
  - Win rate
  - Profit factor
  - Max drawdown
  - Sharpe ratio
  - Number of trades
- Candlestick charting with EMA overlays, buy/sell markers, and volume
- CLI for analysis, plotting, backtest export, and preset optimization

## Recommended EMA Settings

- **M5**: Fast EMA 9/10, Slow EMA 21/20
- **M15**: Fast EMA 8/9, Slow EMA 21/34

## Usage

```bash
python cli.py --data data/BTCUSDT.csv --timeframe 5m --resample 5T --plot output/m5.png --results output/m5_results.json
python cli.py --data data/BTCUSDT.csv --timeframe 15m --resample 15T --optimize
```

## Python API

```python
from data.data_processor import load_ohlcv_data
from strategies.ema_strategy import EMAStrategy
from backtest.backtester import Backtester
from visualization.plotter import Plotter

data = load_ohlcv_data('data/BTCUSDT.csv')

m5_strategy = EMAStrategy(fast_period=9, slow_period=21, timeframe='5m')
m5_signals = m5_strategy.analyze(data)

m15_strategy = EMAStrategy(fast_period=9, slow_period=34, timeframe='15m')
m15_signals = m15_strategy.analyze(data)

backtester = Backtester(initial_capital=10000)
results = backtester.run(m5_strategy, data)
print(results.metrics)

plotter = Plotter()
plotter.plot_strategy(data, m5_signals, save_path='output/m5_chart.png')
```

## Parameter Tuning Guide

Use CLI `--optimize` to evaluate timeframe presets:

- M5: (9,21), (10,20)
- M15: (8,21), (9,34)

Compare by total return, then verify stability with win rate and drawdown.
