"""
Data Retrieval Agent：自然言語クエリを SQL に変換して Athena で実行し、結果を返す。
"""
from __future__ import annotations

import os

from strands import Agent
from strands.models import BedrockModel

from tools.athena_query_tool import run_athena_query


_INSTRUCTION = """
あなたは Amazon Athena のデータ取得エージェントです。
ユーザーの意図に基づいて SQL クエリを生成し、athena_query ツールを使ってデータを取得してください。

注意事項:
- SELECT 文のみ使用してください。DDL/DML は禁止です。
- スキャンデータ量が最小になるよう WHERE 句で絞り込んでください。
- 結果は JSON 形式で返してください。
"""


def create_data_retrieval_agent() -> Agent:
    """Data Retrieval エージェントを生成して返す。"""
    model_id = os.environ.get("BEDROCK_MODEL_ID", "anthropic.claude-3-5-sonnet-20241022-v2:0")
    aws_region = os.environ.get("AWS_REGION", "ap-northeast-1")
    model = BedrockModel(model_id=model_id, region_name=aws_region)

    return Agent(
        name="data_retrieval_agent",
        description="自然言語要求をAthenaクエリとして実行するデータ取得エージェント",
        model=model,
        system_prompt=_INSTRUCTION,
        tools=[run_athena_query],
    )
