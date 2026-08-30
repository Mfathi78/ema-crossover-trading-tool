from __future__ import annotations

from pathlib import Path

import pandas as pd

REQUIRED_COLUMNS = ["open", "high", "low", "close", "volume"]


def _normalize_columns(data: pd.DataFrame) -> pd.DataFrame:
    data = data.copy()
    data.columns = [str(c).strip().lower() for c in data.columns]
    return data


def validate_ohlcv(data: pd.DataFrame) -> pd.DataFrame:
    data = _normalize_columns(data)
    missing = [c for c in REQUIRED_COLUMNS if c not in data.columns]
    if missing:
        raise ValueError(f"Missing required OHLCV columns: {missing}")

    validated = data[REQUIRED_COLUMNS].copy()
    for col in REQUIRED_COLUMNS:
        validated[col] = pd.to_numeric(validated[col], errors="coerce")

    validated = validated.ffill().bfill().dropna()
    return validated


def _ensure_datetime_index(data: pd.DataFrame) -> pd.DataFrame:
    if isinstance(data.index, pd.DatetimeIndex):
        return data.sort_index()

    timestamp_col = None
    for candidate in ("timestamp", "time", "date", "datetime"):
        if candidate in data.columns:
            timestamp_col = candidate
            break

    if timestamp_col is None:
        raise ValueError("Data must include a DatetimeIndex or timestamp/date column")

    with_index = data.copy()
    with_index[timestamp_col] = pd.to_datetime(with_index[timestamp_col], errors="coerce")
    with_index = with_index.dropna(subset=[timestamp_col]).set_index(timestamp_col)
    return with_index.sort_index()


def load_ohlcv_data(file_path: str | Path) -> pd.DataFrame:
    file_path = Path(file_path)
    suffix = file_path.suffix.lower()

    if suffix == ".csv":
        raw = pd.read_csv(file_path)
    elif suffix == ".json":
        raw = pd.read_json(file_path)
    else:
        raise ValueError("Only CSV and JSON formats are supported")

    raw = _normalize_columns(raw)
    raw = _ensure_datetime_index(raw)
    return validate_ohlcv(raw)


def resample_ohlcv(data: pd.DataFrame, timeframe: str) -> pd.DataFrame:
    data = _ensure_datetime_index(_normalize_columns(data))
    data = validate_ohlcv(data)
    timeframe = timeframe.strip()
    if timeframe.lower().endswith("t"):
        timeframe = f"{timeframe[:-1]}min"
    return (
        data.resample(timeframe)
        .agg({"open": "first", "high": "max", "low": "min", "close": "last", "volume": "sum"})
        .dropna()
    )
