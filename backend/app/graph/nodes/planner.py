from __future__ import annotations

from app.graph.state import AgentState
from app.services.llm_mock import mock_llm


async def plan_topics(state: AgentState) -> dict:
    topics = await mock_llm.plan_topics(
        state["topic_direction"], state.get("target_audience", "skincare")
    )
    return {"generated_topics": topics, "status": "awaiting_selection"}
