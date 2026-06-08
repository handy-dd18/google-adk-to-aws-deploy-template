"""
Preprocessing Agent：取得したデータを pandas で前処理する。
"""
from __future__ import annotations

import os

from google.adk.agents import Agent
from google.adk.models.lite_llm import LiteLlm

from tools.python_preprocess_tool import preprocess_data


_INSTRUCTION = """
あなたはデータサイエンスの前処理エージェントです。
data_retrieval_agent から受け取った JSON データを pandas で前処理してください。

実施可能な前処理:
- 欠損値の確認・補完（中央値 / 最頻値 / 削除）
- 外れ値の検出（IQR法）
- データ型変換
- 基本統計量の算出（件数・平均・標準偏差・最小・最大）
- カテゴリ変数の集計

処理結果は JSON 形式で返してください。
"""


def create_preprocessing_agent() -> Agent:
    """Preprocessing エージェントを生成して返す。"""
    model_id = os.environ.get("BEDROCK_MODEL_ID", "anthropic.claude-3-5-sonnet-20241022-v2:0")
    aws_region = os.environ.get("AWS_REGION", "ap-northeast-1")

    return Agent(
        name="preprocessing_agent",
        model=LiteLlm(model=f"bedrock/{model_id}", aws_region_name=aws_region),
        instruction=_INSTRUCTION,
        tools=[preprocess_data],
    )
