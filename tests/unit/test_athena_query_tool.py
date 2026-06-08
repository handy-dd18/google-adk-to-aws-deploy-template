"""
athena_query_tool のユニットテスト（boto3 をモック）。
"""
from __future__ import annotations

import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "app"))

from tools.athena_query_tool import run_athena_query


def _make_boto3_mock(query_state: str = "SUCCEEDED", rows: list | None = None):
    """boto3 athena クライアントのモックを生成する。"""
    mock_client = MagicMock()
    mock_client.start_query_execution.return_value = {"QueryExecutionId": "test-id"}
    mock_client.get_query_execution.return_value = {
        "QueryExecution": {"Status": {"State": query_state, "StateChangeReason": "test"}}
    }

    header = {"Data": [{"VarCharValue": "col1"}, {"VarCharValue": "col2"}]}
    data_row = {"Data": [{"VarCharValue": "val1"}, {"VarCharValue": "val2"}]}
    mock_paginator = MagicMock()
    mock_paginator.paginate.return_value = [
        {"ResultSet": {"Rows": [header, data_row]}}
    ]
    mock_client.get_paginator.return_value = mock_paginator
    return mock_client


def test_success():
    with patch("tools.athena_query_tool.boto3") as mock_boto3:
        mock_boto3.client.return_value = _make_boto3_mock()
        result = run_athena_query("SELECT * FROM test_table")
    assert result["row_count"] == 1
    assert result["rows"][0]["col1"] == "val1"


def test_non_select_rejected():
    result = run_athena_query("DROP TABLE test_table")
    assert "error" in result


def test_query_failed():
    with patch("tools.athena_query_tool.boto3") as mock_boto3:
        mock_boto3.client.return_value = _make_boto3_mock(query_state="FAILED")
        result = run_athena_query("SELECT 1")
    assert "error" in result
