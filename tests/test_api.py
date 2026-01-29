from datetime import date

import pandas as pd
from fastapi.testclient import TestClient

from app.main import app
from app.api import routes


class FakeService:
    def get_stock_list(self):
        return pd.DataFrame({"code": ["000001"], "name": ["测试"]})

    def get_intraday(self, code: str, trading_date: date):
        return pd.DataFrame(
            {
                "code": [code] * 6,
                "date": [str(trading_date)] * 6,
                "time": ["09:31", "09:32", "09:33", "09:34", "09:35", "09:36"],
                "open": [10, 10.1, 10.2, 10.3, 10.4, 10.5],
                "high": [10.2, 10.3, 10.4, 10.5, 10.6, 10.7],
                "low": [9.9, 10.0, 10.1, 10.2, 10.3, 10.4],
                "close": [10.1, 10.2, 10.3, 10.4, 10.5, 10.6],
                "volume": [1000, 1200, 1300, 1500, 1600, 1800],
            }
        )

    def get_index_intraday(self, symbol: str, trading_date: date):
        return self.get_intraday(symbol, trading_date)

    def get_watchlist(self):
        return []


client = TestClient(app)


def test_screener_run_structure(monkeypatch):
    monkeypatch.setattr(routes, "service", FakeService())
    response = client.post("/api/screener/run", json={"top_n": 5})
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert isinstance(data["items"], list)
