from __future__ import annotations

from dataclasses import dataclass
from datetime import date
import logging
from typing import Any

import numpy as np
import pandas as pd

from app.compute.indicators import (
    compute_ema,
    compute_macd,
    compute_orb,
    compute_return,
    compute_rsi,
    compute_rvol,
    compute_vwap,
)
from app.config import settings

logger = logging.getLogger(__name__)


@dataclass
class SignalDetail:
    name: str
    triggered: bool
    time: str
    price: float
    message: str
    risk: str


@dataclass
class ScoreBreakdown:
    momentum: float
    volume: float
    structure: float
    risk: float

    @property
    def total(self) -> float:
        total = self.momentum + self.volume + self.structure - self.risk
        return float(max(0, min(100, total)))

    def to_dict(self) -> dict[str, float]:
        return {
            "momentum": self.momentum,
            "volume": self.volume,
            "structure": self.structure,
            "risk": self.risk,
            "total": self.total,
        }


def _is_halted(df: pd.DataFrame) -> bool:
    return df.empty or df["volume"].sum() == 0


def hard_filter(name: str, df: pd.DataFrame, latest_price: float, turnover: float) -> tuple[bool, list[str]]:
    reasons = []
    if "ST" in name or "退" in name:
        reasons.append("剔除ST/退市标的")
        return False, reasons
    if _is_halted(df):
        reasons.append("停牌或无成交")
        return False, reasons
    if latest_price < settings.min_price or latest_price > settings.max_price:
        reasons.append("价格超出范围")
        return False, reasons
    if turnover < settings.min_turnover:
        reasons.append("成交额不足")
        return False, reasons
    return True, reasons


def compute_signals(df: pd.DataFrame, index_df: pd.DataFrame | None) -> tuple[list[str], list[SignalDetail]]:
    signals: list[str] = []
    details: list[SignalDetail] = []
    latest = df.iloc[-1]
    vwap = compute_vwap(df)
    orb = compute_orb(df, settings.orb_minutes)

    momentum_return = compute_return(df["close"], settings.momentum_window_minutes)
    index_return = 0.0
    if index_df is not None and not index_df.empty:
        index_return = compute_return(index_df["close"], settings.momentum_window_minutes)
    rel_strength = momentum_return - index_return

    if momentum_return > 0 and rel_strength > settings.relative_strength_threshold:
        signals.append("动量/相对强度")
        details.append(
            SignalDetail(
                name="动量/相对强度",
                triggered=True,
                time=str(latest["time"]),
                price=float(latest["close"]),
                message=f"近{settings.momentum_window_minutes}分钟收益{momentum_return:.2f}%，相对强度{rel_strength:.2f}%",
                risk="若指数回落，动量可能衰减",
            )
        )

    rvol = compute_rvol(df["volume"].sum(), df["volume"].mean() * len(df))
    if rvol > settings.rvol_threshold:
        signals.append("放量")
        details.append(
            SignalDetail(
                name="放量",
                triggered=True,
                time=str(latest["time"]),
                price=float(latest["close"]),
                message=f"相对成交量{rvol:.2f}",
                risk="放量后可能冲高回落",
            )
        )

    vwap_cross = False
    if len(df) >= settings.vwap_lookback_minutes:
        recent = df.tail(settings.vwap_lookback_minutes)
        vwap_recent = vwap.tail(settings.vwap_lookback_minutes)
        vwap_cross = (recent["close"] > vwap_recent).iloc[-1] and (
            (recent["close"] <= vwap_recent).iloc[:-1].any()
        )
    if latest["close"] > vwap.iloc[-1] and vwap_cross:
        signals.append("VWAP站上")
        details.append(
            SignalDetail(
                name="VWAP站上",
                triggered=True,
                time=str(latest["time"]),
                price=float(latest["close"]),
                message="价格站上VWAP且近期回踩确认",
                risk="若跌破VWAP需警惕",
            )
        )

    if not np.isnan(orb["orb_high"]) and latest["close"] > orb["orb_high"]:
        signals.append("ORB突破")
        details.append(
            SignalDetail(
                name="ORB突破",
                triggered=True,
                time=str(latest["time"]),
                price=float(latest["close"]),
                message=f"突破开盘{settings.orb_minutes}分钟高点 {orb['orb_high']:.2f}",
                risk="突破失败可能回落至开盘区间",
            )
        )

    return signals, details


def score_stock(df: pd.DataFrame, index_df: pd.DataFrame | None) -> ScoreBreakdown:
    latest = df.iloc[-1]
    momentum_30 = compute_return(df["close"], settings.momentum_window_minutes)
    momentum_60 = compute_return(df["close"], settings.momentum_window_minutes * 2)
    index_return = compute_return(index_df["close"], settings.momentum_window_minutes) if index_df is not None else 0.0
    rel_strength = momentum_30 - index_return

    momentum_score = max(0.0, min(30.0, (momentum_30 + momentum_60) * 0.5 + rel_strength))

    rvol = compute_rvol(df["volume"].sum(), df["volume"].mean() * len(df))
    volume_score = max(0.0, min(30.0, rvol * 10))

    vwap = compute_vwap(df)
    ema8 = compute_ema(df["close"], 8)
    ema21 = compute_ema(df["close"], 21)
    orb = compute_orb(df, settings.orb_minutes)

    structure_score = 0.0
    if latest["close"] > vwap.iloc[-1]:
        structure_score += 8
    if ema8.iloc[-1] > ema21.iloc[-1]:
        structure_score += 8
    if not np.isnan(orb["orb_high"]) and latest["close"] > orb["orb_high"]:
        structure_score += 9
    structure_score = min(25.0, structure_score)

    risk = 0.0
    minute_range = (df["high"] - df["low"]).tail(10).mean()
    if minute_range / latest["close"] > 0.02:
        risk += 5
    limit_up_distance = (latest["close"] * 1.1 - latest["close"]) / latest["close"] * 100
    if limit_up_distance < 0.3:
        risk += 5
    drawdown = (df["close"].max() - latest["close"]) / df["close"].max() * 100
    if drawdown > 3:
        risk += 5

    return ScoreBreakdown(momentum=momentum_score, volume=volume_score, structure=structure_score, risk=risk)


def enrich_indicators(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["vwap"] = compute_vwap(df)
    df["ema8"] = compute_ema(df["close"], 8)
    df["ema21"] = compute_ema(df["close"], 21)
    df["rsi"] = compute_rsi(df["close"], 14)
    macd_df = compute_macd(df["close"], 12, 26, 9)
    df["macd"] = macd_df["macd"]
    df["macd_signal"] = macd_df["signal"]
    df["macd_hist"] = macd_df["hist"]
    return df


def build_reason(score: ScoreBreakdown, signals: list[str]) -> list[str]:
    reasons = [
        f"动量分{score.momentum:.1f}/30",
        f"量能分{score.volume:.1f}/30",
        f"结构分{score.structure:.1f}/25",
        f"风险扣分{score.risk:.1f}/20",
    ]
    if signals:
        reasons.append("触发信号: " + "、".join(signals))
    return reasons


def summarize_stock(
    code: str,
    name: str,
    df: pd.DataFrame,
    index_df: pd.DataFrame | None,
) -> dict[str, Any]:
    df = df.sort_values("time")
    latest = df.iloc[-1]
    vwap = compute_vwap(df).iloc[-1]
    pct_change = (latest["close"] / df.iloc[0]["open"] - 1) * 100
    index_return = compute_return(index_df["close"], settings.momentum_window_minutes) if index_df is not None else 0.0
    rel_strength = pct_change - index_return

    signals, signal_details = compute_signals(df, index_df)
    score = score_stock(df, index_df)

    return {
        "code": code,
        "name": name,
        "price": float(latest["close"]),
        "pct_change_today": float(pct_change),
        "rel_strength_vs_index": float(rel_strength),
        "rvol": float(compute_rvol(df["volume"].sum(), df["volume"].mean() * len(df))),
        "vwap_distance": float((latest["close"] - vwap) / vwap * 100) if vwap else 0.0,
        "orb_breakout": bool(signals and "ORB突破" in signals),
        "signals": signals,
        "score": score.total,
        "score_detail": score.to_dict(),
        "reason": build_reason(score, signals),
        "signal_details": [detail.__dict__ for detail in signal_details],
    }


def calc_turnover(df: pd.DataFrame) -> float:
    return float((df["close"] * df["volume"]).sum())
