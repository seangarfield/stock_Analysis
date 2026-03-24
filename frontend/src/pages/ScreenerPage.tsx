import { useEffect, useMemo, useState } from "react";
import { useNavigate } from "react-router-dom";

import { apiPost } from "../api/client";

interface ScreenerItem {
  code: string;
  name: string;
  price: number;
  pct_change_today: number;
  rel_strength_vs_index: number;
  rvol: number;
  vwap_distance: number;
  orb_breakout: boolean;
  signals: string[];
  score: number;
  reason: string[];
}

interface ScreenerResponse {
  date: string;
  count: number;
  items: ScreenerItem[];
}

const ScreenerPage = () => {
  const [intervalSec, setIntervalSec] = useState(20);
  const [topN, setTopN] = useState(30);
  const [data, setData] = useState<ScreenerItem[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [sortKey, setSortKey] = useState<"score" | "pct_change_today" | "rvol">("score");
  const navigate = useNavigate();

  const fetchData = async () => {
    try {
      setError(null);
      const response = await apiPost<ScreenerResponse, { top_n: number }>("/screener/run", {
        top_n: topN,
      });
      setData(response.items);
    } catch (err) {
      setError((err as Error).message);
    }
  };

  useEffect(() => {
    fetchData();
    const timer = setInterval(fetchData, intervalSec * 1000);
    return () => clearInterval(timer);
  }, [intervalSec, topN]);

  const sorted = useMemo(() => {
    return [...data].sort((a, b) => b[sortKey] - a[sortKey]);
  }, [data, sortKey]);

  return (
    <div className="grid">
      <div className="card">
        <h2>实时候选榜单</h2>
        <div className="flex">
          <label>
            刷新间隔(秒)
            <input
              className="input"
              type="number"
              value={intervalSec}
              onChange={(event) => setIntervalSec(Number(event.target.value))}
            />
          </label>
          <label>
            Top N
            <input
              className="input"
              type="number"
              value={topN}
              onChange={(event) => setTopN(Number(event.target.value))}
            />
          </label>
          <label>
            排序
            <select className="input" value={sortKey} onChange={(event) => setSortKey(event.target.value as typeof sortKey)}>
              <option value="score">评分</option>
              <option value="pct_change_today">涨幅</option>
              <option value="rvol">相对成交量</option>
            </select>
          </label>
        </div>
        {error && <div className="notice">{error}</div>}
        {!error && sorted.length === 0 && <div>无满足条件标的</div>}
        {sorted.length > 0 && (
          <table className="table">
            <thead>
              <tr>
                <th>代码</th>
                <th>名称</th>
                <th>价格</th>
                <th>涨幅%</th>
                <th>相对强度%</th>
                <th>RVOL</th>
                <th>VWAP偏离%</th>
                <th>信号</th>
                <th>评分</th>
                <th>原因</th>
              </tr>
            </thead>
            <tbody>
              {sorted.map((item) => (
                <tr key={item.code} onClick={() => navigate(`/stock/${item.code}`)} style={{ cursor: "pointer" }}>
                  <td>{item.code}</td>
                  <td>{item.name}</td>
                  <td>{item.price.toFixed(2)}</td>
                  <td>{item.pct_change_today.toFixed(2)}</td>
                  <td>{item.rel_strength_vs_index.toFixed(2)}</td>
                  <td>{item.rvol.toFixed(2)}</td>
                  <td>{item.vwap_distance.toFixed(2)}</td>
                  <td>
                    {item.signals.map((signal) => (
                      <span className="tag" key={signal}>
                        {signal}
                      </span>
                    ))}
                  </td>
                  <td>{item.score.toFixed(1)}</td>
                  <td>
                    <ul>
                      {item.reason.map((reason) => (
                        <li key={reason}>{reason}</li>
                      ))}
                    </ul>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </div>
  );
};

export default ScreenerPage;
