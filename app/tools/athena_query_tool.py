"""
Athena クエリ実行ツール。
Google ADK の FunctionTool として Data Retrieval Agent から呼び出される。
"""
from __future__ import annotations

import json
import os
import time

import boto3

_POLL_INTERVAL = 2  # 秒


def run_athena_query(sql: str) -> dict:
    """Athena で SQL を実行し、結果を辞書リストとして返す。

    Args:
        sql: 実行する SELECT 文。

    Returns:
        {"rows": [...], "row_count": int} 形式の辞書。
        エラー時は {"error": str} を返す。
    """
    if not sql.strip().upper().startswith("SELECT"):
        return {"error": "SELECT 文のみ実行できます"}

    workgroup = os.environ.get("ATHENA_WORKGROUP", "primary")
    database = os.environ.get("ATHENA_DATABASE", "default")
    results_bucket = os.environ.get("ATHENA_RESULTS_BUCKET", "")
    region = os.environ.get("AWS_REGION", "ap-northeast-1")

    client = boto3.client("athena", region_name=region)

    start_resp = client.start_query_execution(
        QueryString=sql,
        QueryExecutionContext={"Database": database},
        WorkGroup=workgroup,
        ResultConfiguration={
            "OutputLocation": f"s3://{results_bucket}/results/"
        } if results_bucket else {},
    )
    query_id = start_resp["QueryExecutionId"]

    # クエリ完了まで待機
    for _ in range(60):  # 最大 120 秒
        status_resp = client.get_query_execution(QueryExecutionId=query_id)
        state = status_resp["QueryExecution"]["Status"]["State"]
        if state == "SUCCEEDED":
            break
        if state in ("FAILED", "CANCELLED"):
            reason = status_resp["QueryExecution"]["Status"].get("StateChangeReason", "")
            return {"error": f"クエリ失敗: {reason}"}
        time.sleep(_POLL_INTERVAL)
    else:
        return {"error": "クエリがタイムアウトしました"}

    # 結果を取得（最大 1000 行）
    paginator = client.get_paginator("get_query_results")
    rows: list[dict] = []
    headers: list[str] = []

    for page_idx, page in enumerate(paginator.paginate(QueryExecutionId=query_id)):
        result_rows = page["ResultSet"]["Rows"]
        if page_idx == 0:
            # 1ページ目の1行目はヘッダー
            headers = [col["VarCharValue"] for col in result_rows[0]["Data"]]
            result_rows = result_rows[1:]
        for row in result_rows:
            rows.append({
                headers[i]: col.get("VarCharValue", None)
                for i, col in enumerate(row["Data"])
            })
        if len(rows) >= 1000:
            break

    return {"rows": rows, "row_count": len(rows)}
