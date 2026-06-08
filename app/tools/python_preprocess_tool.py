"""
Python 前処理ツール。
Google ADK の FunctionTool として Preprocessing Agent から呼び出される。
"""
from __future__ import annotations

import json

import pandas as pd


def preprocess_data(data_json: str, operations: list[str]) -> dict:
    """pandas を使ってデータを前処理する。

    Args:
        data_json: Athena クエリ結果の JSON 文字列 ({"rows": [...]} 形式)。
        operations: 実施する前処理の種類リスト。
                    指定可能: "drop_missing", "fill_missing_median",
                              "detect_outliers", "basic_stats", "type_cast"

    Returns:
        {"result": dict, "summary": str} 形式の辞書。
        エラー時は {"error": str} を返す。
    """
    try:
        data = json.loads(data_json) if isinstance(data_json, str) else data_json
        rows = data.get("rows", [])
        if not rows:
            return {"error": "データが空です"}

        df = pd.DataFrame(rows)

        # 数値変換を試みる（変換できない列は元のまま保持）
        for col in df.columns:
            converted = pd.to_numeric(df[col], errors="coerce")
            # 元の非 null 値が過半数以上数値変換できた場合のみ適用
            original_non_null = df[col].notna().sum()
            converted_non_null = converted.notna().sum()
            if original_non_null == 0 or converted_non_null / original_non_null >= 0.5:
                df[col] = converted

        results: dict = {}

        for op in operations:
            if op == "basic_stats":
                results["basic_stats"] = df.describe(include="all").to_dict()

            elif op == "drop_missing":
                before = len(df)
                df = df.dropna()
                results["drop_missing"] = {"removed_rows": before - len(df), "remaining_rows": len(df)}

            elif op == "fill_missing_median":
                filled: dict = {}
                for col in df.select_dtypes(include="number").columns:
                    n = int(df[col].isna().sum())
                    if n > 0:
                        df[col] = df[col].fillna(df[col].median())
                        filled[col] = n
                results["fill_missing_median"] = {"filled_columns": filled}

            elif op == "detect_outliers":
                outlier_counts: dict = {}
                for col in df.select_dtypes(include="number").columns:
                    q1, q3 = df[col].quantile(0.25), df[col].quantile(0.75)
                    iqr = q3 - q1
                    count = int(((df[col] < q1 - 1.5 * iqr) | (df[col] > q3 + 1.5 * iqr)).sum())
                    if count > 0:
                        outlier_counts[col] = count
                results["detect_outliers"] = {"outlier_counts": outlier_counts}

            elif op == "type_cast":
                results["type_cast"] = {col: str(dtype) for col, dtype in df.dtypes.items()}

        return {
            "result": results,
            "processed_rows": len(df),
            "columns": list(df.columns),
            "sample": df.head(5).to_dict(orient="records"),
        }

    except Exception as exc:  # pylint: disable=broad-except
        return {"error": str(exc)}
