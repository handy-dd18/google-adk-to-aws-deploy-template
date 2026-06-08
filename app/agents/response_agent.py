"""
Response Agent：前処理済みデータの結果をユーザー向けに要約・整形する。
"""
from __future__ import annotations

import os

from strands import Agent
from strands.models import BedrockModel


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
    model = BedrockModel(model_id=model_id, region_name=aws_region)

    return Agent(
        name="response_agent",
        description="分析結果をビジネス向けに日本語で要約するエージェント",
        model=model,
        system_prompt=_INSTRUCTION,
    )
