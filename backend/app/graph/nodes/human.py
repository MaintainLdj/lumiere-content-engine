"""人工介入节点（pass-through）。

实际的选择/审稿结果由 API 通过 `graph.update_state` 注入，
这些节点只是为了让 `interrupt_before` 有可命中的节点名。
"""

from __future__ import annotations

from app.graph.state import AgentState


async def human_selection(state: AgentState) -> dict:
    return {}


async def human_review(state: AgentState) -> dict:
    return {}
