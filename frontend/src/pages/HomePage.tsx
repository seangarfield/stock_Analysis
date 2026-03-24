import { useState } from "react";
import { useNavigate } from "react-router-dom";

import { apiGet } from "../api/client";

interface SearchResult {
  code: string;
  name: string;
}

const HomePage = () => {
  const [query, setQuery] = useState("");
  const [results, setResults] = useState<SearchResult[]>([]);
  const [error, setError] = useState<string | null>(null);
  const navigate = useNavigate();

  const handleSearch = async () => {
    if (!query) return;
    setError(null);
    try {
      const data = await apiGet<SearchResult[]>(`/search?q=${encodeURIComponent(query)}`);
      setResults(data);
    } catch (err) {
      setError((err as Error).message);
    }
  };

  return (
    <div className="grid">
      <div className="card">
        <h2>搜索股票</h2>
        <div className="flex">
          <input
            className="input"
            value={query}
            onChange={(event) => setQuery(event.target.value)}
            placeholder="输入代码或名称"
          />
          <button className="button" onClick={handleSearch}>
            搜索
          </button>
          <button className="button" onClick={() => navigate("/screener")}>实时候选榜单</button>
        </div>
        {error && <div className="notice">{error}</div>}
        {results.length > 0 && (
          <table className="table">
            <thead>
              <tr>
                <th>代码</th>
                <th>名称</th>
                <th>操作</th>
              </tr>
            </thead>
            <tbody>
              {results.map((item) => (
                <tr key={item.code}>
                  <td>{item.code}</td>
                  <td>{item.name}</td>
                  <td>
                    <button className="button" onClick={() => navigate(`/stock/${item.code}`)}>
                      查看
                    </button>
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

export default HomePage;
