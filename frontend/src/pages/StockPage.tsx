import { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import ReactECharts from "echarts-for-react";

import { apiGet, apiPost } from "../api/client";

interface IntradayPoint {
  time: string;
  open: number;
  high: number;
  low: number;
  close: number;
  volume: number;
  vwap: number;
}

interface SignalDetail {
  name: string;
  triggered: boolean;
  time: string;
  price: number;
  message: string;
  risk: string;
}

interface IntradayResponse {
  code: string;
  date: string;
  data: IntradayPoint[];
  orb: { orb_high: number; orb_low: number };
  indicators: {
    ema8: number;
    ema21: number;
    rsi: number;
    macd: number;
    macd_signal: number;
    macd_hist: number;
  };
  signals: SignalDetail[];
}

const StockPage = () => {
  const { code } = useParams();
  const [data, setData] = useState<IntradayResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [watching, setWatching] = useState(false);

  useEffect(() => {
    if (!code) return;
    const fetchData = async () => {
      try {
        setError(null);
        const response = await apiGet<IntradayResponse>(`/stock/${code}/intraday`);
        setData(response);
      } catch (err) {
        setError((err as Error).message);
      }
    };
    fetchData();
  }, [code]);

  const toggleWatch = async () => {
    if (!code) return;
    const next = !watching;
    await apiPost("/watchlist", { code, active: next });
    setWatching(next);
  };

  const option = data
    ? {
        tooltip: { trigger: "axis" },
        xAxis: { type: "category", data: data.data.map((item) => item.time) },
        yAxis: [{ type: "value", scale: true }, { type: "value" }],
        series: [
          {
            name: "价格",
            type: "line",
            data: data.data.map((item) => item.close),
            smooth: true,
          },
          {
            name: "VWAP",
            type: "line",
            data: data.data.map((item) => item.vwap),
            smooth: true,
          },
          {
            name: "成交量",
            type: "bar",
            yAxisIndex: 1,
            data: data.data.map((item) => item.volume),
          },
          {
            name: "ORB高",
            type: "line",
            data: data.data.map(() => data.orb.orb_high),
            lineStyle: { type: "dashed" },
          },
          {
            name: "ORB低",
            type: "line",
            data: data.data.map(() => data.orb.orb_low),
            lineStyle: { type: "dashed" },
          },
        ],
      }
    : {};

  return (
    <div className="grid">
      {error && <div className="notice">{error}</div>}
      {data && (
        <>
          <div className="card">
            <div className="flex">
              <h2>个股详情 {data.code}</h2>
              <button className="button" onClick={toggleWatch}>
                {watching ? "移出观察" : "加入观察"}
              </button>
            </div>
            <ReactECharts option={option} style={{ height: 360 }} />
          </div>
          <div className="card">
            <h3>指标面板</h3>
            <div className="grid" style={{ gridTemplateColumns: "repeat(3, 1fr)" }}>
              <div>EMA8: {data.indicators.ema8.toFixed(2)}</div>
              <div>EMA21: {data.indicators.ema21.toFixed(2)}</div>
              <div>RSI: {data.indicators.rsi.toFixed(2)}</div>
              <div>MACD: {data.indicators.macd.toFixed(2)}</div>
              <div>Signal: {data.indicators.macd_signal.toFixed(2)}</div>
              <div>Hist: {data.indicators.macd_hist.toFixed(2)}</div>
            </div>
          </div>
          <div className="card">
            <h3>信号解释</h3>
            {data.signals.length === 0 && <div>暂无触发信号</div>}
            {data.signals.map((signal) => (
              <div key={signal.name} style={{ marginBottom: 12 }}>
                <strong>{signal.name}</strong>
                <div>触发时间: {signal.time}</div>
                <div>关键价位: {signal.price.toFixed(2)}</div>
                <div>触发条件: {signal.message}</div>
                <div>风险提示: {signal.risk}</div>
              </div>
            ))}
          </div>
        </>
      )}
    </div>
  );
};

export default StockPage;
