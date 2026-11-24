from __future__ import annotations

from app.graph.state import AgentState
from app.services.llm_mock import mock_llm
from app.services.image_mock import mock_image


async def extract_visuals(state: AgentState) -> dict:
    points = await mock_llm.extract_visuals(state["article_content"])
    return {"visual_points": points, "status": "generating_images"}


async def generate_images(state: AgentState) -> dict:
    urls = await mock_image.generate_images(state["visual_points"])
    return {"image_urls": urls, "status": "completed"}
