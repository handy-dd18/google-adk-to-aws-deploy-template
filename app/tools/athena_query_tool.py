"""
Athena クエリ実行ツール。
AWS Strands Agent のツールとして Data Retrieval Agent から呼び出される。
"""
from __future__ import annotations

import json
import os
import time

import boto3

_POLL_INTERVAL = 2  # 秒
_MAX_POLL_ITERATIONS = 50
_MAX_RESULT_ROWS = 1000


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
    local_mode = os.environ.get("APP_EXECUTION_MODE", "cloud").lower() == "local"

    if local_mode:
        local_stub = _load_local_stub_rows()
        if local_stub is not None:
            if "error" in local_stub:
                return local_stub
            return {"rows": local_stub["rows"], "row_count": len(local_stub["rows"])}

    endpoint_url = os.environ.get("FLOCI_ATHENA_ENDPOINT_URL", "").strip() if local_mode else ""
    client_kwargs: dict = {"region_name": region}
    if endpoint_url:
        client_kwargs["endpoint_url"] = endpoint_url

    client = boto3.client("athena", **client_kwargs)

    start_query_kwargs = {
        "QueryString": sql,
        "QueryExecutionContext": {"Database": database},
        "WorkGroup": workgroup,
    }
    if results_bucket:
        start_query_kwargs["ResultConfiguration"] = {
            "OutputLocation": f"s3://{results_bucket}/results/"
        }

    start_resp = client.start_query_execution(**start_query_kwargs)
    query_id = start_resp["QueryExecutionId"]

    # クエリ完了まで待機（最大 50 イテレーション × 2秒 = 100 秒）
    for _ in range(_MAX_POLL_ITERATIONS):
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
        if len(rows) >= _MAX_RESULT_ROWS:
            break

    return {"rows": rows, "row_count": len(rows)}


def _load_local_stub_rows() -> dict | None:
    raw = os.environ.get("LOCAL_ATHENA_STUB_ROWS", "").strip()
    if not raw:
        return None

    try:
        parsed = json.loads(raw)
    except json.JSONDecodeError as exc:
        return {"error": f"LOCAL_ATHENA_STUB_ROWS のJSONが不正です: {exc}"}

    if isinstance(parsed, dict):
        return {"rows": [parsed]}
    if isinstance(parsed, list):
        return {"rows": [row for row in parsed if isinstance(row, dict)]}

    return {"rows": []}
