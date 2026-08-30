from __future__ import annotations

import argparse
import json

from backtest.backtester import Backtester
from config.settings import BACKTEST_DEFAULTS, EMA_DEFAULTS
from data.data_processor import load_ohlcv_data, resample_ohlcv
from strategies.ema_strategy import EMAStrategy
from visualization.plotter import Plotter


def _optimize(timeframe: str, data):
    presets = EMAStrategy.PRESETS.get(timeframe, [(9, 21)])
    best = None
    for fast, slow in presets:
        strategy = EMAStrategy(fast_period=fast, slow_period=slow, timeframe=timeframe)
        result = Backtester(**BACKTEST_DEFAULTS).run(strategy, data)
        total_return = result.metrics["total_return_pct"]
        if best is None or total_return > best["metrics"]["total_return_pct"]:
            best = {"fast": fast, "slow": slow, "metrics": result.metrics}
    return best


def main() -> None:
    parser = argparse.ArgumentParser(description="EMA crossover technical analysis tool")
    parser.add_argument("--data", required=True, help="Path to CSV/JSON OHLCV data")
    parser.add_argument("--timeframe", default="5m", choices=["5m", "15m"], help="Strategy timeframe")
    parser.add_argument("--resample", default=None, help="Pandas resample rule (e.g. 5T, 15T)")
    parser.add_argument("--fast", type=int, default=None, help="Fast EMA period")
    parser.add_argument("--slow", type=int, default=None, help="Slow EMA period")
    parser.add_argument("--variant", default="ema", choices=["ema", "dema", "tema"], help="EMA variant")
    parser.add_argument("--plot", default=None, help="Optional output chart path")
    parser.add_argument("--results", default=None, help="Optional output JSON results path")
    parser.add_argument("--optimize", action="store_true", help="Find best preset for timeframe")

    args = parser.parse_args()

    data = load_ohlcv_data(args.data)
    if args.resample:
        data = resample_ohlcv(data, args.resample)

    default = EMA_DEFAULTS[args.timeframe]
    fast = args.fast if args.fast is not None else default["fast_period"]
    slow = args.slow if args.slow is not None else default["slow_period"]

    strategy = EMAStrategy(fast_period=fast, slow_period=slow, timeframe=args.timeframe, variant=args.variant)
    signals = strategy.analyze(data)

    backtester = Backtester(**BACKTEST_DEFAULTS)
    result = backtester.run(strategy, data)

    payload = {
        "timeframe": args.timeframe,
        "fast_period": fast,
        "slow_period": slow,
        "variant": args.variant,
        "metrics": result.metrics,
    }

    if args.optimize:
        payload["optimization"] = _optimize(args.timeframe, data)

    print(json.dumps(payload, indent=2))

    if args.results:
        backtester.export_results(result, args.results)

    if args.plot:
        Plotter().plot_strategy(data, signals, save_path=args.plot, title=f"EMA Crossover ({args.timeframe})")


if __name__ == "__main__":
    main()
