import pandas as pd

from data.data_processor import load_ohlcv_data, resample_ohlcv


def test_load_ohlcv_data_csv(tmp_path):
    file = tmp_path / "sample.csv"
    file.write_text(
        "timestamp,open,high,low,close,volume\n"
        "2024-01-01 00:00:00,100,101,99,100.5,10\n"
        "2024-01-01 00:01:00,100.5,102,100,101.2,12\n"
    )
    data = load_ohlcv_data(file)
    assert list(data.columns) == ["open", "high", "low", "close", "volume"]
    assert isinstance(data.index, pd.DatetimeIndex)


def test_resample_ohlcv(tmp_path):
    file = tmp_path / "sample.csv"
    file.write_text(
        "timestamp,open,high,low,close,volume\n"
        "2024-01-01 00:00:00,100,101,99,100.5,10\n"
        "2024-01-01 00:01:00,100.5,102,100,101.2,12\n"
        "2024-01-01 00:02:00,101.2,103,101,102.1,8\n"
    )
    data = load_ohlcv_data(file)
    out = resample_ohlcv(data, "2T")
    assert len(out) >= 1
    assert out.iloc[0]["volume"] == 22
