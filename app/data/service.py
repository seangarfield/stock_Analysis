from __future__ import annotations

from datetime import date, datetime
import logging
from pathlib import Path

import pandas as pd

from app.config import settings
from app.data.cache.sqlite_cache import SQLiteCache
from app.data.providers.akshare_provider import AKShareProvider
from app.data.providers.base import DataProviderError, IDataProvider
from app.data.providers.csv_provider import CSVProvider

logger = logging.getLogger(__name__)


class DataService:
    def __init__(self, provider: IDataProvider | None = None) -> None:
        self.cache = SQLiteCache()
        self.provider = provider or AKShareProvider()
        self.csv_provider = CSVProvider(Path("./data/sample"))

    def get_stock_list(self) -> pd.DataFrame:
        cached = self.cache.get_stock_list()
        if not cached.empty:
            last_update = pd.to_datetime(cached["updated_at"]).max()
            if (datetime.utcnow() - last_update).days < 1:
                return cached[["code", "name"]]
        try:
            df = self.provider.get_stock_list()
            self.cache.upsert_stock_list(df[["code", "name"]].itertuples(index=False, name=None))
            return df[["code", "name"]]
        except DataProviderError:
            logger.warning("Using cached stock list due to provider error")
            if cached.empty:
                raise
            return cached[["code", "name"]]

    def get_intraday(self, code: str, trading_date: date) -> pd.DataFrame:
        cached = self.cache.get_intraday(code, str(trading_date))
        last_time = self.cache.get_last_intraday_time(code, str(trading_date))
        try:
            df = self.provider.get_intraday(code, trading_date)
        except DataProviderError as exc:
            logger.error("AKShare failed for %s: %s", code, exc)
            if not cached.empty:
                return cached
            df = self.csv_provider.get_intraday(code, trading_date)

        if last_time:
            df = df[df["time"] > last_time]
        if not df.empty:
            self.cache.upsert_intraday(df)
        updated = self.cache.get_intraday(code, str(trading_date))
        return updated if not updated.empty else df

    def get_index_intraday(self, symbol: str, trading_date: date) -> pd.DataFrame:
        try:
            return self.provider.get_index_intraday(symbol, trading_date)
        except DataProviderError as exc:
            logger.error("Index data fetch failed: %s", exc)
            return pd.DataFrame()

    def set_watchlist(self, code: str, active: bool) -> None:
        self.cache.set_watchlist(code, active)

    def get_watchlist(self) -> list[str]:
        return self.cache.get_watchlist()
