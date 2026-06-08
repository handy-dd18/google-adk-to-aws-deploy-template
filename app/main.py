"""
AWS Strands Agents マルチエージェントアプリのエントリーポイント。
Lambda ハンドラーとして動作する。
"""
from __future__ import annotations

import json
import os

from agents.orchestrator import create_orchestrator
from tools.athena_query_tool import run_athena_query


def handler(event: dict, context: object) -> dict:
    """AWS Lambda ハンドラー。API Gateway からの POST /query リクエストを処理する。"""
    body = json.loads(event.get("body") or "{}")
    user_query: str = body.get("query", "")

    if not user_query:
        return _response(400, {"error": "query フィールドが空です"})

    if _is_local_mode():
        return _handle_local_mode(user_query)

    orchestrator = create_orchestrator()
    result = orchestrator(user_query)
    result_text = _extract_text(result)

    return _response(200, {"result": result_text})


def _is_local_mode() -> bool:
    return os.environ.get("APP_EXECUTION_MODE", "cloud").lower() == "local"


def _handle_local_mode(user_query: str) -> dict:
    sql = os.environ.get("LOCAL_MODE_SQL", "").strip()
    if not sql:
        result_text = f"[local-mode] queryを受信: {user_query}"
        return _response(200, {"result": result_text})

    query_result = run_athena_query(sql)
    if "error" in query_result:
        result_text = f"[local-mode] queryを受信: {user_query}\nAthenaスタブ実行エラー: {query_result['error']}"
        return _response(200, {"result": result_text})

    row_count = query_result.get("row_count", 0)
    result_text = f"[local-mode] queryを受信: {user_query}\nAthenaスタブ実行成功: {row_count} rows"
    return _response(200, {"result": result_text})


def _extract_text(result: object) -> str:
    message = getattr(result, "message", None)
    if not message:
        return ""

    content_blocks = message.get("content", []) if isinstance(message, dict) else getattr(message, "content", [])
    texts: list[str] = []
    for block in content_blocks:
        if isinstance(block, dict):
            text = block.get("text")
        else:
            text = getattr(block, "text", None)
        if text:
            texts.append(str(text))
    return "\n".join(texts).strip()


def _response(status_code: int, body: dict) -> dict:
    return {
        "statusCode": status_code,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps(body, ensure_ascii=False),
    }
