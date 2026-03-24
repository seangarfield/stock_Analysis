from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Settings:
    data_dir: Path = Path(os.getenv("DATA_DIR", "./data"))
    db_path: Path = Path(os.getenv("DB_PATH", "./data/cache.db"))
    log_dir: Path = Path(os.getenv("LOG_DIR", "./logs"))
    orb_minutes: int = int(os.getenv("ORB_MINUTES", "15"))
    refresh_seconds: int = int(os.getenv("REFRESH_SECONDS", "20"))
    cache_ttl_seconds: int = int(os.getenv("CACHE_TTL_SECONDS", "60"))

    min_price: float = float(os.getenv("MIN_PRICE", "2"))
    max_price: float = float(os.getenv("MAX_PRICE", "200"))
    min_turnover: float = float(os.getenv("MIN_TURNOVER", "10000000"))

    momentum_window_minutes: int = int(os.getenv("MOMENTUM_WINDOW_MINUTES", "30"))
    relative_strength_threshold: float = float(os.getenv("RELATIVE_STRENGTH_THRESHOLD", "0.5"))
    rvol_threshold: float = float(os.getenv("RVOL_THRESHOLD", "1.5"))

    vwap_lookback_minutes: int = int(os.getenv("VWAP_LOOKBACK_MINUTES", "20"))


settings = Settings()
