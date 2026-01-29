from __future__ import annotations

import numpy as np
import pandas as pd


def compute_vwap(df: pd.DataFrame) -> pd.Series:
    pv = (df["close"] * df["volume"]).cumsum()
    vv = df["volume"].cumsum()
    return pv / vv.replace(0, np.nan)


def compute_ema(series: pd.Series, span: int) -> pd.Series:
    return series.ewm(span=span, adjust=False).mean()


def compute_rsi(series: pd.Series, period: int = 14) -> pd.Series:
    delta = series.diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)
    avg_gain = gain.rolling(window=period, min_periods=period).mean()
    avg_loss = loss.rolling(window=period, min_periods=period).mean()
    rs = avg_gain / avg_loss.replace(0, np.nan)
    rsi = 100 - (100 / (1 + rs))
    return rsi.fillna(0)


def compute_macd(series: pd.Series, fast: int = 12, slow: int = 26, signal: int = 9) -> pd.DataFrame:
    ema_fast = compute_ema(series, fast)
    ema_slow = compute_ema(series, slow)
    macd_line = ema_fast - ema_slow
    signal_line = compute_ema(macd_line, signal)
    hist = macd_line - signal_line
    return pd.DataFrame({"macd": macd_line, "signal": signal_line, "hist": hist})


def compute_orb(df: pd.DataFrame, minutes: int) -> dict[str, float]:
    orb_df = df.head(minutes)
    return {
        "orb_high": float(orb_df["high"].max()) if not orb_df.empty else float("nan"),
        "orb_low": float(orb_df["low"].min()) if not orb_df.empty else float("nan"),
    }


def compute_rvol(current_volume: float, avg_volume: float) -> float:
    if avg_volume == 0:
        return 0.0
    return current_volume / avg_volume


def compute_return(series: pd.Series, window: int) -> float:
    if len(series) < window + 1:
        return 0.0
    return (series.iloc[-1] / series.iloc[-window - 1] - 1) * 100
