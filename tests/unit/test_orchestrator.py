"""
orchestrator エージェントのユニットテスト。
依存サービス（Bedrock / Athena）はモックで代替する。
"""
from __future__ import annotations

import sys
import types
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

# app ディレクトリを検索パスに追加
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "app"))

# google.adk が未インストールの環境向けにスタブを用意
for _mod_name in [
    "google",
    "google.adk",
    "google.adk.agents",
    "google.adk.models",
    "google.adk.models.lite_llm",
]:
    if _mod_name not in sys.modules:
        sys.modules[_mod_name] = types.ModuleType(_mod_name)

sys.modules["google.adk.agents"].Agent = MagicMock()
sys.modules["google.adk.models.lite_llm"].LiteLlm = MagicMock()


def test_create_orchestrator_returns_agent():
    """create_orchestrator が Agent オブジェクトを返すことを確認する。"""
    # キャッシュをクリアして再インポート
    for mod in list(sys.modules.keys()):
        if mod.startswith("agents"):
            del sys.modules[mod]

    mock_agent_cls = MagicMock()
    mock_litelm_cls = MagicMock()
    sys.modules["google.adk.agents"].Agent = mock_agent_cls
    sys.modules["google.adk.models.lite_llm"].LiteLlm = mock_litelm_cls

    import agents.orchestrator as orch_mod

    with (
        patch.object(orch_mod, "create_data_retrieval_agent", return_value=MagicMock()),
        patch.object(orch_mod, "create_preprocessing_agent", return_value=MagicMock()),
        patch.object(orch_mod, "create_response_agent", return_value=MagicMock()),
    ):
        orch_mod.create_orchestrator()

    mock_agent_cls.assert_called_once()
    kwargs = mock_agent_cls.call_args.kwargs
    assert kwargs["name"] == "orchestrator"
    assert len(kwargs["sub_agents"]) == 3
