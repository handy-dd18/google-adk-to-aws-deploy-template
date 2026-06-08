"""
SAM local start-api で起動した /query の最小E2Eテスト。
"""
from __future__ import annotations

import json
import os
import urllib.request
from urllib.parse import urlparse

import pytest


@pytest.mark.integration
def test_query_endpoint_on_local_sam():
    base_url = os.environ.get("LOCAL_API_BASE_URL", "").strip()
    if not base_url:
        pytest.skip("LOCAL_API_BASE_URL が未設定のためスキップ")

    parsed = urlparse(base_url)
    if parsed.hostname not in {"127.0.0.1", "localhost"}:
        pytest.skip("LOCAL_API_BASE_URL は localhost 系のみ許可")

    req = urllib.request.Request(
        url=f"{base_url}/query",
        data=json.dumps({"query": "売上を要約して"}).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    with urllib.request.urlopen(req, timeout=10) as resp:
        body = json.loads(resp.read().decode("utf-8"))
        assert resp.status == 200
        assert "result" in body
