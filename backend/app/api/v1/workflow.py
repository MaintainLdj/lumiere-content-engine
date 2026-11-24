from __future__ import annotations

import uuid
from typing import Any

from fastapi import APIRouter, HTTPException, Request
from langgraph.graph.state import CompiledStateGraph
from pydantic import BaseModel

router = APIRouter(prefix="/workflow", tags=["workflow"])


class StartRequest(BaseModel):
    topic_direction: str
    target_audience: str = "skincare"


class ResumeRequest(BaseModel):
    action: str  # select_topic | approve | reject
    data: str = ""


def _get_graph(request: Request) -> CompiledStateGraph:
    graph = getattr(request.app.state, "graph", None)
    if graph is None:
        raise HTTPException(status_code=500, detail="graph not initialized")
    return graph


def _config(thread_id: str) -> dict[str, Any]:
    return {"configurable": {"thread_id": thread_id}}


@router.post("/start")
async def start(req: StartRequest, request: Request) -> dict:
    graph = _get_graph(request)
    thread_id = uuid.uuid4().hex
    config = _config(thread_id)

    await graph.ainvoke(
        {
            "topic_direction": req.topic_direction,
            "target_audience": req.target_audience,
            "review_feedback": "",
        },
        config=config,
    )

    snapshot = await graph.aget_state(config)
    return {
        "thread_id": thread_id,
        "next": list(snapshot.next),
        "status": snapshot.values.get("status"),
        "generated_topics": snapshot.values.get("generated_topics", []),
    }


@router.get("/state/{thread_id}")
async def get_state(thread_id: str, request: Request) -> dict:
    graph = _get_graph(request)
    snapshot = await graph.aget_state(_config(thread_id))
    return {
        "values": snapshot.values,
        "next": list(snapshot.next),
    }


@router.post("/resume/{thread_id}")
async def resume(thread_id: str, req: ResumeRequest, request: Request) -> dict:
    graph = _get_graph(request)
    config = _config(thread_id)

    if req.action == "select_topic":
        await graph.aupdate_state(config, {"selected_topic": req.data})
    elif req.action == "approve":
        await graph.aupdate_state(config, {"review_feedback": "APPROVE"})
    elif req.action == "reject":
        if not req.data:
            raise HTTPException(status_code=400, detail="reject 需要提供修改意见 data")
        await graph.aupdate_state(config, {"review_feedback": req.data})
    else:
        raise HTTPException(
            status_code=400,
            detail="action 仅支持 select_topic / approve / reject",
        )

    # 恢复执行，直到下一个中断点或结束
    async for _ in graph.astream(None, config=config):
        pass

    snapshot = await graph.aget_state(config)
    return {
        "values": snapshot.values,
        "next": list(snapshot.next),
        "status": snapshot.values.get("status"),
    }
