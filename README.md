# A股盘中实时选股/分析平台 MVP

## 功能概览
- 实时榜单：轮询刷新候选股，展示评分、信号与入选原因。
- 个股详情：分时图 + VWAP/ORB 线，指标面板与信号解释。
- 搜索：代码/名称模糊匹配。
- 复盘统计：信号触发后 5/15/30 分钟表现统计。

## 目录结构
```
app/
  api/            # FastAPI 路由
  compute/        # 指标计算
  data/           # 数据与缓存
  engine/         # 规则与打分
frontend/         # React 前端
tests/            # pytest 单元测试
```

## 本地运行

### 后端
```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

### 前端
```bash
cd frontend
npm install
npm run dev
```

## 配置
复制 `.env.example` 到 `.env`，按需调整：
- `ORB_MINUTES`：开盘区间分钟数。
- `CACHE_TTL_SECONDS`：筛选缓存秒数。
- `VITE_API_BASE`：前端请求后端地址。

## 数据源说明
- 默认使用 AKShare，若 AKShare 拉取失败会记录日志并尝试读取 `data/sample` 内 CSV 示例。
- 分钟线缓存于 SQLite（`DB_PATH`），增量更新。


## AKShare接口自检（新增）
可执行以下命令快速确认 A 股接口是否可拉取到数据：
```bash
python scripts/check_akshare.py
```
- 成功会输出 JSON：`ok=true` 且包含 `stock_list_count / stock_intraday_rows / index_intraday_rows`。
- 失败会输出 `stage` 与 `error`，用于定位是股票列表、个股分钟线还是指数分钟线异常。

## 常见问题
- **AKShare 接口不稳定**：查看 `logs/app.log`，确认网络与接口状态。
- **无候选结果**：可在 `.env` 降低 `MIN_TURNOVER` 或 `RVOL_THRESHOLD`。

## 接口摘要
- `GET /api/health`
- `GET /api/search?q=xxx`
- `GET /api/stock/{code}/intraday`
- `GET /api/index/intraday?symbol=000300`
- `POST /api/screener/run`
- `GET /api/review?date=YYYY-MM-DD`
- `POST /api/watchlist`

## 验收清单
- 实时榜单 `/screener` 可刷新候选列表。
- 个股详情 `/stock/:code` 展示分时图与信号解释。
- 复盘统计 `/review` 展示信号统计。
- 搜索框支持代码/名称查询。
- pytest 单元测试覆盖指标、信号、评分、API 返回结构。
