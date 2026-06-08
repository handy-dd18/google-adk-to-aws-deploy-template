"""
Orchestrator Agent：ユーザーの自然言語クエリを解釈し、
データ取得ツールと前処理ツールを組み合わせて回答を生成する。
"""
from __future__ import annotations

import os

from strands import Agent
from strands.models import BedrockModel
from tools.athena_query_tool import run_athena_query
from tools.python_preprocess_tool import preprocess_data


_ORCHESTRATOR_INSTRUCTION = """
あなたはデータ分析AIアシスタントの司令官です。
ユーザーの自然言語クエリを受け取り、以下の手順でタスクを処理してください。

1. ユーザーの意図を把握する
2. run_athena_query を使って必要なデータを取得する
3. preprocess_data を使って必要な前処理を行う
4. 結果をビジネス観点でわかりやすく日本語で要約する

データソースは Amazon S3 Tables (Iceberg) 上にあり、Amazon Athena でクエリします。
SQLを直接ユーザーに見せる必要はありません。結果に集中してください。
"""


def create_orchestrator() -> Agent:
    """Orchestrator エージェントを生成して返す。"""
    model_id = os.environ.get("BEDROCK_MODEL_ID", "anthropic.claude-3-5-sonnet-20241022-v2:0")
    aws_region = os.environ.get("AWS_REGION", "ap-northeast-1")

    model = BedrockModel(model_id=model_id, region_name=aws_region)

    return Agent(
        name="orchestrator",
        description="Athena と pandas ツールを使って分析回答を返す Orchestrator Agent",
        model=model,
        system_prompt=_ORCHESTRATOR_INSTRUCTION,
        tools=[run_athena_query, preprocess_data],
    )
