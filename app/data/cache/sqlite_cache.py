from __future__ import annotations

import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Iterable

import pandas as pd

from app.config import settings


class SQLiteCache:
    def __init__(self, db_path: Path | None = None) -> None:
        self.db_path = db_path or settings.db_path
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_schema()

    def _init_schema(self) -> None:
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS stock_list (
                    code TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                )
                """
            )
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS intraday (
                    code TEXT NOT NULL,
                    date TEXT NOT NULL,
                    time TEXT NOT NULL,
                    open REAL,
                    high REAL,
                    low REAL,
                    close REAL,
                    volume REAL,
                    PRIMARY KEY (code, date, time)
                )
                """
            )
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS watchlist (
                    code TEXT PRIMARY KEY
                )
                """
            )

    def upsert_stock_list(self, rows: Iterable[tuple[str, str]]) -> None:
        now = datetime.utcnow().isoformat()
        with sqlite3.connect(self.db_path) as conn:
            conn.executemany(
                "INSERT OR REPLACE INTO stock_list (code, name, updated_at) VALUES (?, ?, ?)",
                [(code, name, now) for code, name in rows],
            )

    def get_stock_list(self) -> pd.DataFrame:
        with sqlite3.connect(self.db_path) as conn:
            return pd.read_sql_query("SELECT code, name, updated_at FROM stock_list", conn)

    def upsert_intraday(self, df: pd.DataFrame) -> None:
        if df.empty:
            return
        with sqlite3.connect(self.db_path) as conn:
            conn.executemany(
                """
                INSERT OR REPLACE INTO intraday (code, date, time, open, high, low, close, volume)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                df[[
                    "code",
                    "date",
                    "time",
                    "open",
                    "high",
                    "low",
                    "close",
                    "volume",
                ]].itertuples(index=False, name=None),
            )

    def get_intraday(self, code: str, date: str) -> pd.DataFrame:
        with sqlite3.connect(self.db_path) as conn:
            return pd.read_sql_query(
                """
                SELECT code, date, time, open, high, low, close, volume
                FROM intraday WHERE code = ? AND date = ? ORDER BY time
                """,
                conn,
                params=(code, date),
            )

    def get_last_intraday_time(self, code: str, date: str) -> str | None:
        with sqlite3.connect(self.db_path) as conn:
            row = conn.execute(
                "SELECT time FROM intraday WHERE code = ? AND date = ? ORDER BY time DESC LIMIT 1",
                (code, date),
            ).fetchone()
        return row[0] if row else None

    def set_watchlist(self, code: str, active: bool) -> None:
        with sqlite3.connect(self.db_path) as conn:
            if active:
                conn.execute(
                    "INSERT OR REPLACE INTO watchlist (code) VALUES (?)",
                    (code,),
                )
            else:
                conn.execute("DELETE FROM watchlist WHERE code = ?", (code,))

    def get_watchlist(self) -> list[str]:
        with sqlite3.connect(self.db_path) as conn:
            rows = conn.execute("SELECT code FROM watchlist").fetchall()
        return [row[0] for row in rows]
