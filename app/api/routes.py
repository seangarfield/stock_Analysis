from __future__ import annotations

from datetime import date, datetime
import logging
from typing import Any

import pandas as pd
from fastapi import APIRouter, HTTPException

from app.api.schemas import ScreenerParams, WatchlistRequest
from app.compute.indicators import compute_orb
from app.config import settings
from app.data.service import DataService
from app.engine.screener import (
    calc_turnover,
    compute_signals,
    enrich_indicators,
    hard_filter,
    summarize_stock,
)

logger = logging.getLogger(__name__)
router = APIRouter()
service = DataService()
_cache: dict[str, tuple[datetime, Any]] = {}


@router.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}


@router.get("/search")
async def search(q: str) -> list[dict[str, str]]:
    df = service.get_stock_list()
    mask = df["code"].str.contains(q) | df["name"].str.contains(q)
    return df[mask].head(20).to_dict(orient="records")


@router.get("/stock/{code}/intraday")
async def stock_intraday(code: str, date: str | None = None) -> dict[str, Any]:
    trading_date = datetime.strptime(date, "%Y-%m-%d").date() if date else datetime.now().date()
    df = service.get_intraday(code, trading_date)
    if df.empty:
        raise HTTPException(status_code=404, detail="数据源异常")
    df = df.sort_values("time")
    enriched = enrich_indicators(df)
    orb = compute_orb(df, settings.orb_minutes)
    signals, signal_details = compute_signals(df, None)
    latest = enriched.iloc[-1]
    return {
        "code": code,
        "date": str(trading_date),
        "data": enriched[["time", "open", "high", "low", "close", "volume", "vwap"]].to_dict(orient="records"),
        "orb": orb,
        "indicators": {
            "ema8": float(latest["ema8"]),
            "ema21": float(latest["ema21"]),
            "rsi": float(latest["rsi"]),
            "macd": float(latest["macd"]),
            "macd_signal": float(latest["macd_signal"]),
            "macd_hist": float(latest["macd_hist"]),
        },
        "signals": signal_details,
    }


@router.get("/index/intraday")
async def index_intraday(symbol: str, date: str | None = None) -> dict[str, Any]:
    trading_date = datetime.strptime(date, "%Y-%m-%d").date() if date else datetime.now().date()
    df = service.get_index_intraday(symbol, trading_date)
    if df.empty:
        raise HTTPException(status_code=404, detail="数据源异常")
    return {
        "symbol": symbol,
        "date": str(trading_date),
        "data": df[["time", "open", "high", "low", "close", "volume"]].to_dict(orient="records"),
    }


@router.post("/screener/run")
async def run_screener(payload: ScreenerParams) -> dict[str, Any]:
    cache_key = f"screener:{payload.model_dump()}"
    cached = _cache.get(cache_key)
    if cached:
        ts, value = cached
        if (datetime.utcnow() - ts).total_seconds() < settings.cache_ttl_seconds:
            return value

    trading_date = datetime.strptime(payload.date, "%Y-%m-%d").date() if payload.date else datetime.now().date()
    df_list = service.get_stock_list()
    watchlist = service.get_watchlist()
    if payload.universe == "watchlist":
        df_list = df_list[df_list["code"].isin(watchlist)]

    index_df = service.get_index_intraday("000300", trading_date)

    results = []
    for _, row in df_list.iterrows():
        code = row["code"]
        name = row["name"]
        try:
            df = service.get_intraday(code, trading_date)
        except Exception as exc:  # noqa: BLE001
            logger.warning("Failed to get intraday for %s: %s", code, exc)
            continue
        if df.empty:
            continue
        df = df.sort_values("time")
        latest_price = float(df.iloc[-1]["close"])
        turnover = calc_turnover(df)
        ok, filter_reasons = hard_filter(name, df, latest_price, turnover)
        if not ok:
            continue
        summary = summarize_stock(code, name, df, index_df)
        if filter_reasons:
            summary["reason"].extend(filter_reasons)
        results.append(summary)

    results = sorted(results, key=lambda item: item["score"], reverse=True)
    output = {"date": str(trading_date), "count": len(results), "items": results[: payload.top_n]}
    _cache[cache_key] = (datetime.utcnow(), output)
    return output


@router.get("/review")
async def review(date: str) -> dict[str, Any]:
    trading_date = datetime.strptime(date, "%Y-%m-%d").date()
    df_list = service.get_stock_list()
    stats: dict[str, list[float]] = {}
    for _, row in df_list.iterrows():
        code = row["code"]
        try:
            df = service.get_intraday(code, trading_date)
        except Exception:
            continue
        if df.empty:
            continue
        df = df.sort_values("time")
        signals, _ = compute_signals(df, None)
        if not signals:
            continue
        entry_price = df.iloc[-1]["close"]
        for horizon in [5, 15, 30]:
            if len(df) > horizon:
                future = df.tail(horizon)
                ret = (future["close"].iloc[-1] / entry_price - 1) * 100
                drawdown = (future["low"].min() / entry_price - 1) * 100
            else:
                ret = 0.0
                drawdown = 0.0
            for signal in signals:
                stats.setdefault(f"{signal}-{horizon}", []).append((ret, drawdown))

    summary = []
    for key, values in stats.items():
        rets = [v[0] for v in values]
        dds = [v[1] for v in values]
        signal, horizon = key.rsplit("-", 1)
        summary.append(
            {
                "signal": signal,
                "horizon": int(horizon),
                "avg_return": float(pd.Series(rets).mean()),
                "win_rate": float((pd.Series(rets) > 0).mean()),
                "max_drawdown": float(pd.Series(dds).min()),
                "sample": len(rets),
            }
        )
    return {"date": str(trading_date), "summary": summary}


@router.post("/watchlist")
async def update_watchlist(payload: WatchlistRequest) -> dict[str, Any]:
    service.set_watchlist(payload.code, payload.active)
    return {"code": payload.code, "active": payload.active}
