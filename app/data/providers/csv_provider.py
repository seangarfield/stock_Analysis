from __future__ import annotations

from datetime import date
from pathlib import Path

import pandas as pd

from app.data.providers.base import DataProviderError


class CSVProvider:
    def __init__(self, base_dir: Path) -> None:
        self.base_dir = base_dir

    def get_stock_list(self) -> pd.DataFrame:
        files = list(self.base_dir.glob("*.csv"))
        if not files:
            raise DataProviderError("No CSV sample data found")
        data = []
        for file in files:
            code = file.stem
            data.append({"code": code, "name": f"样例{code}"})
        return pd.DataFrame(data)

    def get_intraday(self, code: str, trading_date: date) -> pd.DataFrame:
        path = self.base_dir / f"{code}.csv"
        if not path.exists():
            raise DataProviderError(f"CSV not found for {code}")
        df = pd.read_csv(path)
        df = df[df["date"] == str(trading_date)]
        if df.empty:
            raise DataProviderError(f"No data for {code} on {trading_date}")
        return df[["code", "date", "time", "open", "high", "low", "close", "volume"]]

    def get_index_intraday(self, symbol: str, trading_date: date) -> pd.DataFrame:
        raise DataProviderError("CSVProvider does not provide index data")
