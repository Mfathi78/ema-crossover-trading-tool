from __future__ import annotations

from dataclasses import dataclass

import pandas as pd

from indicators.ema import BUY, SELL, ema_crossover


@dataclass(frozen=True)
class Trade:
    entry_time: pd.Timestamp
    entry_price: float
    exit_time: pd.Timestamp
    exit_price: float
    return_pct: float


class EMAStrategy:
    PRESETS = {
        "5m": [(9, 21), (10, 20)],
        "15m": [(8, 21), (9, 34)],
    }

    def __init__(self, fast_period: int = 9, slow_period: int = 21, timeframe: str = "5m", variant: str = "ema") -> None:
        self.fast_period = fast_period
        self.slow_period = slow_period
        self.timeframe = timeframe
        self.variant = variant

    def analyze(self, data: pd.DataFrame) -> pd.DataFrame:
        if "close" not in data.columns:
            raise ValueError("Data must contain a 'close' column")

        signals = ema_crossover(
            data["close"],
            fast_period=self.fast_period,
            slow_period=self.slow_period,
            variant=self.variant,
        )
        if "open" in data.columns:
            for col in ("open", "high", "low", "volume"):
                if col in data.columns:
                    signals[col] = data[col]
        return signals

    def extract_trades(self, signals: pd.DataFrame) -> list[Trade]:
        trades: list[Trade] = []
        entry_time: pd.Timestamp | None = None
        entry_price: float | None = None

        for ts, row in signals.iterrows():
            signal = int(row["signal"])
            close = float(row["close"])

            if signal == BUY and entry_time is None:
                entry_time, entry_price = ts, close
            elif signal == SELL and entry_time is not None and entry_price is not None:
                ret = ((close - entry_price) / entry_price) * 100
                trades.append(Trade(entry_time, entry_price, ts, close, ret))
                entry_time, entry_price = None, None

        return trades

    def stats(self, signals: pd.DataFrame) -> dict[str, float | int]:
        trades = self.extract_trades(signals)
        wins = sum(1 for t in trades if t.return_pct > 0)
        losses = sum(1 for t in trades if t.return_pct <= 0)
        total = len(trades)
        return {
            "number_of_trades": total,
            "wins": wins,
            "losses": losses,
            "win_rate": (wins / total * 100) if total else 0.0,
        }
