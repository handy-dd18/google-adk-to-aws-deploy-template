"""
Orchestrator Agent：ユーザーの自然言語クエリを解釈し、
Data Retrieval Agent と Preprocessing Agent へタスクを委譲する。
"""
from __future__ import annotations

import os

from google.adk.agents import Agent
from google.adk.models.lite_llm import LiteLlm

from agents.data_retrieval_agent import create_data_retrieval_agent
from agents.preprocessing_agent import create_preprocessing_agent
from agents.response_agent import create_response_agent


_ORCHESTRATOR_INSTRUCTION = """
あなたはデータ分析AIアシスタントの司令官です。
ユーザーの自然言語クエリを受け取り、以下の手順でタスクを処理してください。

1. ユーザーの意図を把握する
2. data_retrieval_agent にデータ取得を依頼する
3. preprocessing_agent に前処理を依頼する
4. response_agent に結果の要約・整形を依頼する

データソースは Amazon S3 Tables (Iceberg) 上にあり、Amazon Athena でクエリします。
SQLを直接ユーザーに見せる必要はありません。結果に集中してください。
"""


def create_orchestrator() -> Agent:
    """Orchestrator エージェントを生成して返す。"""
    model_id = os.environ.get("BEDROCK_MODEL_ID", "anthropic.claude-3-5-sonnet-20241022-v2:0")
    aws_region = os.environ.get("AWS_REGION", "ap-northeast-1")

    return Agent(
        name="orchestrator",
        model=LiteLlm(model=f"bedrock/{model_id}", aws_region_name=aws_region),
        instruction=_ORCHESTRATOR_INSTRUCTION,
        sub_agents=[
            create_data_retrieval_agent(),
            create_preprocessing_agent(),
            create_response_agent(),
        ],
    )
