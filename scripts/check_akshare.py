from __future__ import annotations

from datetime import date
import json
import sys


def main() -> int:
    try:
        import akshare as ak  # type: ignore
        import pandas as pd  # type: ignore
    except Exception as exc:  # noqa: BLE001
        print(json.dumps({"ok": False, "stage": "import", "error": str(exc)}, ensure_ascii=False))
        return 2

    report: dict[str, object] = {"ok": True, "date": str(date.today())}

    try:
        spot_df = ak.stock_zh_a_spot_em()
        report["stock_list_count"] = int(len(spot_df))
    except Exception as exc:  # noqa: BLE001
        print(json.dumps({"ok": False, "stage": "stock_zh_a_spot_em", "error": str(exc)}, ensure_ascii=False))
        return 3

    sample_code = str(spot_df.iloc[0]["代码"])
    report["sample_code"] = sample_code

    try:
        stock_min_df = ak.stock_zh_a_hist_min_em(symbol=sample_code, period="1", adjust="")
        report["stock_intraday_rows"] = int(len(stock_min_df))
    except Exception as exc:  # noqa: BLE001
        print(
            json.dumps(
                {"ok": False, "stage": "stock_zh_a_hist_min_em", "sample_code": sample_code, "error": str(exc)},
                ensure_ascii=False,
            )
        )
        return 4

    try:
        index_min_df = ak.index_zh_a_hist_min_em(symbol="000300", period="1")
        report["index_intraday_rows"] = int(len(index_min_df))
    except Exception as exc:  # noqa: BLE001
        print(json.dumps({"ok": False, "stage": "index_zh_a_hist_min_em", "error": str(exc)}, ensure_ascii=False))
        return 5

    if report["stock_list_count"] == 0 or report["stock_intraday_rows"] == 0:
        report["ok"] = False
        report["error"] = "AKShare返回空数据"
        print(json.dumps(report, ensure_ascii=False))
        return 6

    print(json.dumps(report, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
