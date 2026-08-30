from __future__ import annotations

from pathlib import Path

import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import pandas as pd


class Plotter:
    def __init__(self, style: str = "seaborn-v0_8") -> None:
        plt.style.use(style)

    def plot_strategy(
        self,
        data: pd.DataFrame,
        signals: pd.DataFrame,
        save_path: str | Path | None = None,
        title: str = "EMA Crossover Strategy",
    ) -> None:
        required = {"open", "high", "low", "close", "volume"}
        if not required.issubset(data.columns):
            raise ValueError("Data must include open, high, low, close, volume for plotting")

        fig, (ax_price, ax_vol) = plt.subplots(
            2,
            1,
            figsize=(14, 8),
            dpi=150,
            sharex=True,
            gridspec_kw={"height_ratios": [3, 1]},
        )

        x = mdates.date2num(data.index.to_pydatetime())
        width = 0.6 * (x[1] - x[0]) if len(x) > 1 else 0.0005

        for i, (_, row) in enumerate(data.iterrows()):
            o, h, l, c = row["open"], row["high"], row["low"], row["close"]
            color = "#2ca02c" if c >= o else "#d62728"
            ax_price.vlines(x[i], l, h, color=color, linewidth=1)
            bottom = min(o, c)
            height = max(abs(c - o), 1e-8)
            ax_price.add_patch(plt.Rectangle((x[i] - width / 2, bottom), width, height, color=color, alpha=0.8))

        if "fast" in signals.columns:
            ax_price.plot(signals.index, signals["fast"], label="Fast EMA", color="#1f77b4", linewidth=1.4)
        if "slow" in signals.columns:
            ax_price.plot(signals.index, signals["slow"], label="Slow EMA", color="#ff7f0e", linewidth=1.4)

        if "signal" in signals.columns and "close" in signals.columns:
            buys = signals[signals["signal"] == 1]
            sells = signals[signals["signal"] == -1]
            ax_price.scatter(buys.index, buys["close"], marker="^", color="green", s=60, label="BUY", zorder=5)
            ax_price.scatter(sells.index, sells["close"], marker="v", color="red", s=60, label="SELL", zorder=5)

        ax_vol.bar(data.index, data["volume"], color="#7f7f7f", width=width)

        ax_price.set_title(title)
        ax_price.set_ylabel("Price")
        ax_vol.set_ylabel("Volume")
        ax_price.legend(loc="upper left")
        ax_price.grid(alpha=0.2)
        ax_vol.grid(alpha=0.2)
        ax_vol.xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m-%d\n%H:%M"))

        fig.tight_layout()
        if save_path:
            save_path = Path(save_path)
            save_path.parent.mkdir(parents=True, exist_ok=True)
            fig.savefig(save_path, bbox_inches="tight")
        else:
            plt.show()
        plt.close(fig)
