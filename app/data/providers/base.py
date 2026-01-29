from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import date
from typing import Protocol

import pandas as pd


class IDataProvider(Protocol):
    def get_stock_list(self) -> pd.DataFrame: ...

    def get_intraday(self, code: str, trading_date: date) -> pd.DataFrame: ...

    def get_index_intraday(self, symbol: str, trading_date: date) -> pd.DataFrame: ...


class DataProviderError(RuntimeError):
    pass
