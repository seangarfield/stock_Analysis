from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class ScreenerParams(BaseModel):
    date: str | None = None
    top_n: int = 50
    universe: str = "all"
    params: dict[str, Any] = Field(default_factory=dict)


class WatchlistRequest(BaseModel):
    code: str
    active: bool
