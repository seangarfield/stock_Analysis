import { Link, Route, Routes } from "react-router-dom";

import HomePage from "./pages/HomePage";
import ScreenerPage from "./pages/ScreenerPage";
import StockPage from "./pages/StockPage";
import ReviewPage from "./pages/ReviewPage";

const App = () => {
  return (
    <div className="app">
      <header className="header">
        <h1>A股盘中实时选股/分析平台 MVP</h1>
        <nav>
          <Link to="/">首页</Link>
          <Link to="/screener">实时榜单</Link>
          <Link to="/review">复盘统计</Link>
        </nav>
      </header>
      <main className="main">
        <Routes>
          <Route path="/" element={<HomePage />} />
          <Route path="/screener" element={<ScreenerPage />} />
          <Route path="/stock/:code" element={<StockPage />} />
          <Route path="/review" element={<ReviewPage />} />
        </Routes>
      </main>
    </div>
  );
};

export default App;
