"""
main.handler のユニットテスト。
"""
from __future__ import annotations

import json
import sys
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "app"))

import main  # noqa: E402


def test_handler_returns_400_when_query_missing():
    response = main.handler({"body": "{}"}, context={})
    assert response["statusCode"] == 400


def test_handler_cloud_mode(monkeypatch):
    monkeypatch.setenv("APP_EXECUTION_MODE", "cloud")
    fake_result = SimpleNamespace(message={"content": [{"text": "ok"}]})

    with patch("main.create_orchestrator") as mock_create_orchestrator:
        mock_agent = MagicMock(return_value=fake_result)
        mock_create_orchestrator.return_value = mock_agent
        response = main.handler({"body": json.dumps({"query": "sales?"})}, context={})

    body = json.loads(response["body"])
    assert response["statusCode"] == 200
    assert body["result"] == "ok"


def test_handler_local_mode_without_sql(monkeypatch):
    monkeypatch.setenv("APP_EXECUTION_MODE", "local")
    monkeypatch.delenv("LOCAL_MODE_SQL", raising=False)

    response = main.handler({"body": json.dumps({"query": "sales?"})}, context={})
    body = json.loads(response["body"])

    assert response["statusCode"] == 200
    assert "[local-mode] queryを受信" in body["result"]


def test_handler_local_mode_with_sql(monkeypatch):
    monkeypatch.setenv("APP_EXECUTION_MODE", "local")
    monkeypatch.setenv("LOCAL_MODE_SQL", "SELECT 1")

    with patch("main.run_athena_query") as mock_run_athena:
        mock_run_athena.return_value = {"rows": [{"value": "1"}], "row_count": 1}
        response = main.handler({"body": json.dumps({"query": "sales?"})}, context={})

    body = json.loads(response["body"])
    assert response["statusCode"] == 200
    assert "Athenaスタブ実行成功: 1 rows" in body["result"]
