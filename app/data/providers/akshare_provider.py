from __future__ import annotations

from datetime import date
import logging

import akshare as ak
import pandas as pd

from app.data.providers.base import DataProviderError

logger = logging.getLogger(__name__)


class AKShareProvider:
    def get_stock_list(self) -> pd.DataFrame:
        try:
            df = ak.stock_zh_a_spot_em()
            return df[["代码", "名称"]].rename(columns={"代码": "code", "名称": "name"})
        except Exception as exc:  # noqa: BLE001
            logger.exception("AKShare stock list fetch failed")
            raise DataProviderError("AKShare stock list fetch failed") from exc

    def get_intraday(self, code: str, trading_date: date) -> pd.DataFrame:
        try:
            df = ak.stock_zh_a_hist_min_em(
                symbol=code,
                period="1",
                adjust="",
            )
            df = df.rename(
                columns={
                    "时间": "datetime",
                    "开盘": "open",
                    "收盘": "close",
                    "最高": "high",
                    "最低": "low",
                    "成交量": "volume",
                }
            )
            df["datetime"] = pd.to_datetime(df["datetime"])
            df = df[df["datetime"].dt.date == trading_date]
            df["date"] = df["datetime"].dt.date.astype(str)
            df["time"] = df["datetime"].dt.strftime("%H:%M")
            df["code"] = code
            return df[["code", "date", "time", "open", "high", "low", "close", "volume"]]
        except Exception as exc:  # noqa: BLE001
            logger.exception("AKShare intraday fetch failed for %s", code)
            raise DataProviderError("AKShare intraday fetch failed") from exc

    def get_index_intraday(self, symbol: str, trading_date: date) -> pd.DataFrame:
        try:
            df = ak.index_zh_a_hist_min_em(symbol=symbol, period="1")
            df = df.rename(
                columns={
                    "时间": "datetime",
                    "开盘": "open",
                    "收盘": "close",
                    "最高": "high",
                    "最低": "low",
                    "成交量": "volume",
                }
            )
            df["datetime"] = pd.to_datetime(df["datetime"])
            df = df[df["datetime"].dt.date == trading_date]
            df["date"] = df["datetime"].dt.date.astype(str)
            df["time"] = df["datetime"].dt.strftime("%H:%M")
            df["code"] = symbol
            return df[["code", "date", "time", "open", "high", "low", "close", "volume"]]
        except Exception as exc:  # noqa: BLE001
            logger.exception("AKShare index intraday fetch failed for %s", symbol)
            raise DataProviderError("AKShare index intraday fetch failed") from exc
