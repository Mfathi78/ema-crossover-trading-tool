from __future__ import annotations

from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = BASE_DIR / "data"
OUTPUT_DIR = BASE_DIR / "output"

EMA_DEFAULTS = {
    "5m": {"fast_period": 9, "slow_period": 21, "alternatives": [(10, 20)]},
    "15m": {"fast_period": 9, "slow_period": 34, "alternatives": [(8, 21)]},
}

BACKTEST_DEFAULTS = {
    "initial_capital": 10000.0,
    "fee_rate": 0.0,
}

LOGGING = {
    "level": "INFO",
    "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
}
