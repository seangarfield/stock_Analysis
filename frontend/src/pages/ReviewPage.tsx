import { useState } from "react";

import { apiGet } from "../api/client";

interface ReviewItem {
  signal: string;
  horizon: number;
  avg_return: number;
  win_rate: number;
  max_drawdown: number;
  sample: number;
}

interface ReviewResponse {
  date: string;
  summary: ReviewItem[];
}

const ReviewPage = () => {
  const [date, setDate] = useState("");
  const [data, setData] = useState<ReviewItem[]>([]);
  const [error, setError] = useState<string | null>(null);

  const fetchReview = async () => {
    if (!date) return;
    try {
      setError(null);
      const response = await apiGet<ReviewResponse>(`/review?date=${date}`);
      setData(response.summary);
    } catch (err) {
      setError((err as Error).message);
    }
  };

  return (
    <div className="grid">
      <div className="card">
        <h2>复盘统计</h2>
        <div className="flex">
          <input className="input" type="date" value={date} onChange={(event) => setDate(event.target.value)} />
          <button className="button" onClick={fetchReview}>
            查询
          </button>
        </div>
        {error && <div className="notice">{error}</div>}
        {data.length > 0 && (
          <table className="table">
            <thead>
              <tr>
                <th>信号</th>
                <th>窗口(分钟)</th>
                <th>平均收益%</th>
                <th>胜率</th>
                <th>最大回撤%</th>
                <th>样本数</th>
              </tr>
            </thead>
            <tbody>
              {data.map((item) => (
                <tr key={`${item.signal}-${item.horizon}`}>
                  <td>{item.signal}</td>
                  <td>{item.horizon}</td>
                  <td>{item.avg_return.toFixed(2)}</td>
                  <td>{(item.win_rate * 100).toFixed(1)}%</td>
                  <td>{item.max_drawdown.toFixed(2)}</td>
                  <td>{item.sample}</td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </div>
  );
};

export default ReviewPage;
