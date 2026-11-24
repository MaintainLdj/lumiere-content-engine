from __future__ import annotations

from app.graph.state import AgentState
from app.services.llm_mock import mock_llm


async def write_draft(state: AgentState) -> dict:
    content = await mock_llm.write_draft(
        state["selected_topic"], state.get("review_feedback", "")
    )
    # 写完后清空 review_feedback，进入新一轮审稿循环
    return {
        "article_content": content,
        "review_feedback": "",
        "status": "awaiting_review",
    }
