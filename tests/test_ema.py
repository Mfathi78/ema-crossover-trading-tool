import pandas as pd

from indicators.ema import BUY, HOLD, SELL, crossover_signal, dema, ema, ema_crossover, tema


def test_ema_matches_expected_shape_and_index():
    close = pd.Series([1, 2, 3, 4, 5], index=pd.date_range("2024-01-01", periods=5, freq="D"))
    result = ema(close, 3)
    assert len(result) == len(close)
    assert result.index.equals(close.index)


def test_dema_and_tema_return_series():
    close = pd.Series([1, 2, 3, 4, 5])
    assert len(dema(close, 3)) == 5
    assert len(tema(close, 3)) == 5


def test_crossover_signal_detects_buy_and_sell():
    idx = pd.date_range("2024-01-01", periods=4, freq="D")
    fast = pd.Series([1, 1, 3, 0], index=idx)
    slow = pd.Series([2, 2, 2, 2], index=idx)
    signals = crossover_signal(fast, slow)
    assert signals.iloc[2] == BUY
    assert signals.iloc[3] == SELL
    assert signals.iloc[0] == HOLD


def test_ema_crossover_dataframe_columns():
    close = pd.Series([100, 101, 102, 103], index=pd.date_range("2024-01-01", periods=4, freq="D"))
    result = ema_crossover(close, fast_period=2, slow_period=3)
    assert {"close", "fast", "slow", "signal"}.issubset(result.columns)
