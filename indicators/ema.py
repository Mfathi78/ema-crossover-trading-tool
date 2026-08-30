from __future__ import annotations

from typing import Literal

import pandas as pd

BUY = 1
SELL = -1
HOLD = 0
Signal = Literal[-1, 0, 1]


def _validate_period(period: int) -> None:
    if period <= 0:
        raise ValueError("period must be > 0")


def ema(series: pd.Series, period: int) -> pd.Series:
    _validate_period(period)
    return series.astype(float).ewm(span=period, adjust=False).mean()


def dema(series: pd.Series, period: int) -> pd.Series:
    ema_1 = ema(series, period)
    ema_2 = ema(ema_1, period)
    return 2 * ema_1 - ema_2


def tema(series: pd.Series, period: int) -> pd.Series:
    ema_1 = ema(series, period)
    ema_2 = ema(ema_1, period)
    ema_3 = ema(ema_2, period)
    return 3 * (ema_1 - ema_2) + ema_3


def crossover_signal(fast: pd.Series, slow: pd.Series) -> pd.Series:
    if len(fast) != len(slow):
        raise ValueError("fast and slow series must have the same length")

    above_now = (fast > slow).astype(bool)
    above_prev = above_now.shift(1).fillna(False).astype(bool)

    signals = pd.Series(HOLD, index=fast.index, dtype=int)
    signals[(~above_prev) & above_now] = BUY
    signals[above_prev & (~above_now)] = SELL
    return signals


def ema_crossover(
    close: pd.Series,
    fast_period: int = 9,
    slow_period: int = 21,
    variant: str = "ema",
) -> pd.DataFrame:
    if fast_period >= slow_period:
        raise ValueError("fast_period must be less than slow_period")

    calculators = {"ema": ema, "dema": dema, "tema": tema}
    if variant not in calculators:
        raise ValueError("variant must be one of: ema, dema, tema")

    calc = calculators[variant]
    fast = calc(close, fast_period)
    slow = calc(close, slow_period)
    signal = crossover_signal(fast, slow)

    return pd.DataFrame(
        {
            "close": close,
            "fast": fast,
            "slow": slow,
            "signal": signal,
        },
        index=close.index,
    )
