"""
python_preprocess_tool のユニットテスト。
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "app"))

from tools.python_preprocess_tool import preprocess_data


SAMPLE_ROWS = [
    {"age": "25", "salary": "50000", "dept": "Engineering"},
    {"age": "30", "salary": "60000", "dept": "Marketing"},
    {"age": None, "salary": "55000", "dept": "Engineering"},
    {"age": "45", "salary": None, "dept": "HR"},
]


def _make_json(rows):
    return json.dumps({"rows": rows})


def test_basic_stats():
    result = preprocess_data(_make_json(SAMPLE_ROWS), ["basic_stats"])
    assert "basic_stats" in result["result"]
    assert result["processed_rows"] == 4


def test_drop_missing():
    result = preprocess_data(_make_json(SAMPLE_ROWS), ["drop_missing"])
    info = result["result"]["drop_missing"]
    assert info["removed_rows"] == 2
    assert info["remaining_rows"] == 2


def test_fill_missing_median():
    result = preprocess_data(_make_json(SAMPLE_ROWS), ["fill_missing_median"])
    assert "filled_columns" in result["result"]["fill_missing_median"]


def test_detect_outliers():
    rows = [{"val": str(i)} for i in range(10)] + [{"val": "1000"}]
    result = preprocess_data(_make_json(rows), ["detect_outliers"])
    counts = result["result"]["detect_outliers"]["outlier_counts"]
    assert "val" in counts


def test_empty_data_returns_error():
    result = preprocess_data(json.dumps({"rows": []}), ["basic_stats"])
    assert "error" in result
