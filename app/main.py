"""
ADK マルチエージェントアプリのエントリーポイント。
Lambda ハンドラーとして動作する。
"""
from __future__ import annotations

import json
import os

from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService

from agents.orchestrator import create_orchestrator


def handler(event: dict, context: object) -> dict:
    """AWS Lambda ハンドラー。API Gateway からの POST /query リクエストを処理する。"""
    body = json.loads(event.get("body") or "{}")
    user_query: str = body.get("query", "")

    if not user_query:
        return _response(400, {"error": "query フィールドが空です"})

    session_service = InMemorySessionService()
    session = session_service.create_session(
        app_name="adk-aws-template",
        user_id=event.get("requestContext", {}).get("requestId", "anonymous"),
    )

    orchestrator = create_orchestrator()
    runner = Runner(agent=orchestrator, app_name="adk-aws-template", session_service=session_service)

    result_text = ""
    for event_item in runner.run(
        user_id=session.user_id,
        session_id=session.id,
        new_message=_text_message(user_query),
    ):
        if event_item.is_final_response() and event_item.content:
            for part in event_item.content.parts:
                if part.text:
                    result_text += part.text

    return _response(200, {"result": result_text})


def _text_message(text: str):
    from google.genai.types import Content, Part
    return Content(role="user", parts=[Part(text=text)])


def _response(status_code: int, body: dict) -> dict:
    return {
        "statusCode": status_code,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps(body, ensure_ascii=False),
    }
