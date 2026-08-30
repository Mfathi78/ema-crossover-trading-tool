import pandas as pd

from backtest.backtester import Backtester
from strategies.ema_strategy import EMAStrategy


def _sample_data():
    idx = pd.date_range("2024-01-01", periods=20, freq="min")
    close = pd.Series([100, 101, 102, 103, 104, 103, 102, 101, 100, 99, 100, 101, 102, 103, 104, 105, 106, 105, 104, 103], index=idx)
    return pd.DataFrame(
        {
            "open": close,
            "high": close + 0.5,
            "low": close - 0.5,
            "close": close,
            "volume": 10,
        },
        index=idx,
    )


def test_strategy_outputs_signals_and_stats():
    data = _sample_data()
    strategy = EMAStrategy(fast_period=2, slow_period=4)
    signals = strategy.analyze(data)
    stats = strategy.stats(signals)

    assert "signal" in signals.columns
    assert "number_of_trades" in stats


def test_backtester_returns_metrics():
    data = _sample_data()
    strategy = EMAStrategy(fast_period=2, slow_period=4)
    result = Backtester(initial_capital=1000).run(strategy, data)

    assert "total_return_pct" in result.metrics
    assert "win_rate" in result.metrics
    assert "number_of_trades" in result.metrics
