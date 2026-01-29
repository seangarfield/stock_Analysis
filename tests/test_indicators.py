import pandas as pd

from app.compute.indicators import (
    compute_ema,
    compute_macd,
    compute_orb,
    compute_return,
    compute_rsi,
    compute_rvol,
    compute_vwap,
)


def sample_df():
    return pd.DataFrame(
        {
            "close": [10, 10.5, 10.2, 10.8, 11.0],
            "open": [10, 10.4, 10.3, 10.7, 10.9],
            "high": [10.6, 10.7, 10.5, 10.9, 11.1],
            "low": [9.9, 10.2, 10.1, 10.6, 10.8],
            "volume": [100, 150, 120, 180, 200],
        }
    )


def test_compute_vwap():
    df = sample_df()
    vwap = compute_vwap(df)
    assert vwap.iloc[-1] > 0


def test_compute_ema():
    df = sample_df()
    ema = compute_ema(df["close"], 3)
    assert len(ema) == len(df)


def test_compute_rsi():
    df = sample_df()
    rsi = compute_rsi(df["close"], 3)
    assert 0 <= rsi.iloc[-1] <= 100


def test_compute_macd():
    df = sample_df()
    macd = compute_macd(df["close"])
    assert {"macd", "signal", "hist"}.issubset(macd.columns)


def test_compute_orb():
    df = sample_df()
    orb = compute_orb(df, 3)
    assert orb["orb_high"] >= orb["orb_low"]


def test_compute_return():
    df = sample_df()
    ret = compute_return(df["close"], 2)
    assert isinstance(ret, float)


def test_compute_rvol():
    rvol = compute_rvol(1000, 500)
    assert rvol == 2
