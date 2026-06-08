"""
AWS Strands Agents マルチエージェントアプリのエントリーポイント。
Lambda ハンドラーとして動作する。
"""
from __future__ import annotations

import json

from agents.orchestrator import create_orchestrator


def handler(event: dict, context: object) -> dict:
    """AWS Lambda ハンドラー。API Gateway からの POST /query リクエストを処理する。"""
    body = json.loads(event.get("body") or "{}")
    user_query: str = body.get("query", "")

    if not user_query:
        return _response(400, {"error": "query フィールドが空です"})

    orchestrator = create_orchestrator()
    result = orchestrator(user_query)
    result_text = _extract_text(result)

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
