"""Checkpointer 初始化：启动时自动建表。"""

from __future__ import annotations

from psycopg_pool import AsyncConnectionPool
from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver

from app.core.config import settings


async def setup_checkpointer() -> AsyncPostgresSaver:
    # SQLAlchemy 用的是 +asyncpg；psycopg 用裸 postgresql://
    conninfo = settings.DATABASE_URL.replace("+asyncpg", "")
    pool = AsyncConnectionPool(conninfo=conninfo, open=False, kwargs={"autocommit": True})
    await pool.open()

    checkpointer = AsyncPostgresSaver(pool)
    await checkpointer.setup()  # 自动创建 checkpoints 所需表
    return checkpointer
