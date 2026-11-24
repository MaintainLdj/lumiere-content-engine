from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.v1.workflow import router as workflow_router
from app.core.db import engine
from app.graph.utils import setup_checkpointer
from app.graph.workflow import build_workflow


@asynccontextmanager
async def lifespan(app: FastAPI):
    # 启动：初始化 checkpointer（自动建表）并编译 Graph
    checkpointer = await setup_checkpointer()
    app.state.graph = build_workflow(checkpointer)
    try:
        yield
    finally:
        await engine.dispose()


app = FastAPI(title="Lumiere 内容引擎", version="0.1.0", lifespan=lifespan)
app.include_router(workflow_router, prefix="/api/v1")


@app.get("/health")
async def health() -> dict:
    return {"status": "ok"}
