"""
Response Agent：前処理済みデータの結果をユーザー向けに要約・整形する。
"""
from __future__ import annotations

import os

from google.adk.agents import Agent
from google.adk.models.lite_llm import LiteLlm


_INSTRUCTION = """
あなたはデータ分析結果の説明エージェントです。
preprocessing_agent から受け取ったデータ処理結果を、ビジネス観点でわかりやすく日本語で説明してください。

出力フォーマット:
1. 分析サマリー（3行以内）
2. 主要な発見事項（箇条書き）
3. 推奨アクション（あれば）
"""


def create_response_agent() -> Agent:
    """Response エージェントを生成して返す。"""
    model_id = os.environ.get("BEDROCK_MODEL_ID", "anthropic.claude-3-5-sonnet-20241022-v2:0")
    aws_region = os.environ.get("AWS_REGION", "ap-northeast-1")

    return Agent(
        name="response_agent",
        model=LiteLlm(model=f"bedrock/{model_id}", aws_region_name=aws_region),
        instruction=_INSTRUCTION,
    )
