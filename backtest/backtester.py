from __future__ import annotations

from dataclasses import dataclass, asdict
from pathlib import Path
import json

import numpy as np
import pandas as pd

from indicators.ema import BUY, SELL


@dataclass
class BacktestResult:
    equity_curve: pd.Series
    trades: list[dict]
    metrics: dict[str, float | int]


class Backtester:
    def __init__(self, initial_capital: float = 10000.0, fee_rate: float = 0.0) -> None:
        self.initial_capital = float(initial_capital)
        self.fee_rate = float(fee_rate)

    def run(self, strategy, data: pd.DataFrame) -> BacktestResult:
        signals = strategy.analyze(data)

        cash = self.initial_capital
        units = 0.0
        in_position = False
        equity_points: list[float] = []
        equity_index: list[pd.Timestamp] = []
        trades: list[dict] = []
        entry_price = 0.0
        entry_time = None

        for ts, row in signals.iterrows():
            price = float(row["close"])
            signal = int(row["signal"])

            if signal == BUY and not in_position:
                fee = cash * self.fee_rate
                investable_cash = cash - fee
                units = investable_cash / price
                cash = 0.0
                in_position = True
                entry_price = price
                entry_time = ts
            elif signal == SELL and in_position:
                gross = units * price
                fee = gross * self.fee_rate
                cash = gross - fee
                pnl = cash - self.initial_capital if not trades else cash - trades[-1]["equity_after"]
                trades.append(
                    {
                        "entry_time": str(entry_time),
                        "exit_time": str(ts),
                        "entry_price": entry_price,
                        "exit_price": price,
                        "return_pct": ((price - entry_price) / entry_price) * 100,
                        "profit": pnl,
                        "equity_after": cash,
                    }
                )
                units = 0.0
                in_position = False

            equity = cash if not in_position else units * price
            equity_points.append(equity)
            equity_index.append(ts)

        equity_curve = pd.Series(equity_points, index=equity_index, name="equity")
        metrics = self._metrics(equity_curve, trades)
        return BacktestResult(equity_curve=equity_curve, trades=trades, metrics=metrics)

    def _metrics(self, equity_curve: pd.Series, trades: list[dict]) -> dict[str, float | int]:
        if equity_curve.empty:
            return {
                "total_return_pct": 0.0,
                "win_rate": 0.0,
                "profit_factor": 0.0,
                "max_drawdown": 0.0,
                "sharpe_ratio": 0.0,
                "number_of_trades": 0,
            }

        total_return = ((equity_curve.iloc[-1] - self.initial_capital) / self.initial_capital) * 100

        trade_returns = [t["return_pct"] for t in trades]
        wins = [t for t in trade_returns if t > 0]
        losses = [t for t in trade_returns if t <= 0]
        win_rate = (len(wins) / len(trades) * 100) if trades else 0.0
        profit_factor = (sum(wins) / abs(sum(losses))) if losses and sum(losses) != 0 else (float("inf") if wins else 0.0)

        running_max = equity_curve.cummax()
        drawdown = (equity_curve - running_max) / running_max
        max_drawdown = float(drawdown.min() * 100)

        returns = equity_curve.pct_change().dropna()
        sharpe = float(np.sqrt(252) * returns.mean() / returns.std()) if len(returns) > 1 and returns.std() > 0 else 0.0

        return {
            "total_return_pct": float(total_return),
            "win_rate": float(win_rate),
            "profit_factor": float(profit_factor),
            "max_drawdown": float(max_drawdown),
            "sharpe_ratio": sharpe,
            "number_of_trades": len(trades),
        }

    @staticmethod
    def export_results(result: BacktestResult, output_path: str | Path) -> None:
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        payload = {
            "metrics": result.metrics,
            "trades": result.trades,
        }
        output_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
