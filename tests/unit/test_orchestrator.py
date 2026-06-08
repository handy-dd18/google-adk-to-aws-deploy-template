"""
orchestrator エージェントのユニットテスト。
依存サービス（Bedrock / Athena）はモックで代替する。
"""
from __future__ import annotations

import sys
import types
from pathlib import Path
from unittest.mock import MagicMock

# app ディレクトリを検索パスに追加
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "app"))

# strands-agents が未インストールの環境向けにスタブを用意
for _mod_name in [
    "strands",
    "strands.models",
]:
    if _mod_name not in sys.modules:
        sys.modules[_mod_name] = types.ModuleType(_mod_name)

sys.modules["strands"].Agent = MagicMock()
sys.modules["strands.models"].BedrockModel = MagicMock()


def test_create_orchestrator_returns_agent():
    """create_orchestrator が Agent オブジェクトを返すことを確認する。"""
    # キャッシュをクリアして再インポート
    for mod in list(sys.modules.keys()):
        if mod.startswith("agents"):
            del sys.modules[mod]

    mock_agent_cls = MagicMock()
    mock_bedrock_model_cls = MagicMock()
    sys.modules["strands"].Agent = mock_agent_cls
    sys.modules["strands.models"].BedrockModel = mock_bedrock_model_cls

    import agents.orchestrator as orch_mod

    orch_mod.create_orchestrator()

    mock_bedrock_model_cls.assert_called_once()
    mock_agent_cls.assert_called_once()
    kwargs = mock_agent_cls.call_args.kwargs
    assert kwargs["name"] == "orchestrator"
    assert kwargs["tools"] == [orch_mod.run_athena_query, orch_mod.preprocess_data]
