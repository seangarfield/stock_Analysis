import pandas as pd

from app.engine.screener import ScoreBreakdown, build_reason, compute_signals, summarize_stock


def sample_df():
    return pd.DataFrame(
        {
            "code": ["000001"] * 6,
            "date": ["2024-01-02"] * 6,
            "time": ["09:31", "09:32", "09:33", "09:34", "09:35", "09:36"],
            "open": [10, 10.1, 10.2, 10.3, 10.4, 10.5],
            "high": [10.2, 10.3, 10.4, 10.5, 10.6, 10.7],
            "low": [9.9, 10.0, 10.1, 10.2, 10.3, 10.4],
            "close": [10.1, 10.2, 10.3, 10.4, 10.5, 10.6],
            "volume": [1000, 1200, 1300, 1500, 1600, 1800],
        }
    )


def test_score_breakdown_total():
    score = ScoreBreakdown(momentum=10, volume=10, structure=10, risk=5)
    assert score.total == 25


def test_build_reason():
    score = ScoreBreakdown(momentum=10, volume=10, structure=10, risk=5)
    reason = build_reason(score, ["信号A"])
    assert any("动量分" in item for item in reason)


def test_compute_signals_format():
    df = sample_df()
    signals, details = compute_signals(df, None)
    assert isinstance(signals, list)
    assert isinstance(details, list)


def test_summarize_stock():
    df = sample_df()
    summary = summarize_stock("000001", "测试", df, None)
    assert "score" in summary
    assert "reason" in summary
