# Role (角色设定)

你是一位精通 Python 的高级后端架构师，专注于 Generative AI 工作流开发。
你非常熟悉 **LangGraph(1.0 架构)**、`FastAPI`、`PostgreSQL` 以及异步编程模式。

---

# Goal (项目目标)

为一家 **美妆公司** 构建 "AI 内容运营助手" 的后端服务。

**核心目标：** 实现一个自动化的工作流，用于生成微信公众号美妆长文（测评/教程/种草/成分科普）和小红书配图文案。

**关键特性：**
- 必须包含 **Human-in-the-loop (人工介入)** 机制，允许运营人员在"选题阶段"和"审稿阶段"介入决策。
- 内容覆盖护肤、彩妆、成分科普等美妆方向，受众维度包含护肤党/彩妆党/成分党/新手小白/敏感肌。
- **合规红线**：美妆内容禁止绝对化用词（最好/第一/顶级）、医疗暗示（治疗/治愈/药用/特效）、夸大宣传。生成文案时需在 prompt 中体现此约束。

---

# Tech Stack (技术栈)

1. **Language**: Python 3.10+
2. **Web Framework**: FastAPI (Async)
3. **Orchestration**: **LangGraph 1.0+** (必须使用 `StateGraph`, `AsyncPostgresSaver` 进行持久化, 以及 `interrupt_before` 中断模式)。
4. **Database**: 本地 PostgreSQL (不使用 Docker，假设本地已安装，连接串为 localhost)。推荐使用 **DBeaver** 作为图形化客户端进行连接与日常管理（DBeaver 仅是 GUI 工具，不改变数据库本身的连接逻辑）。
5. **ORM**: SQLAlchemy (Async) + Pydantic。
6. **Services**: 使用 Mock (模拟) 服务来代替真实的 LLM/绘图 API，以便快速跑通逻辑。

请注意 langChain 和 langGraph 的版本一定要 1.0 以上。

---

# Workflow Logic (工作流逻辑)

这是一个包含循环的状态机（State Machine）：

1. **Start** -> 节点: `plan_topics` (AI 生成 3-5 个美妆选题)。
2. **INTERRUPT (中断)**: 等待人工选题。
3. **Human Action**: 用户通过 API 选择一个选题（更新 State）。
4. **Resume** -> 节点: `write_draft` (AI 根据选题写美妆长文)。
5. **INTERRUPT (中断)**: 等待人工审稿。
6. **Human Action**: 用户通过 API 提交审核结果。
   - *情况 A (通过)*: -> 节点: `extract_visuals` (提炼图片要点) -> 节点: `generate_images` -> **End**。
   - *情况 B (驳回)*: -> 更新 State 中的反馈意见 -> 路由回退到 节点: `write_draft` (重写)。

---

# Project Structure (项目结构)

请保持模块化设计，**先在本地跑 PostgreSQL（建议用 DBeaver 作为图形化客户端进行连接与管理）**。请严格遵循以下目录结构：

```text
backend/
├── app/
│   ├── api/
│   │   └── v1/
│   │       └── workflow.py       # 核心接口：启动、查看状态、恢复运行
│   ├── core/
│   │   ├── config.py             # 配置 (数据库URL等)
│   │   └── db.py                 # 数据库连接 (AsyncEngine)
│   ├── graph/                    # LangGraph 核心逻辑
│   │   ├── state.py              # State 定义 (TypedDict)
│   │   ├── nodes/                # 节点逻辑 (Planner, Writer, Visualizer)
│   │   │   ├── __init__.py
│   │   │   ├── planner.py
│   │   │   ├── writer.py
│   │   │   └── visualizer.py
│   │   ├── workflow.py           # Graph 组装 & Checkpointer 配置
│   │   └── utils.py              # 用于初始化 Checkpointer 数据库表的工具函数
│   ├── services/                 # Mock 服务
│   │   ├── __init__.py
│   │   ├── llm_mock.py
│   │   └── image_mock.py
│   └── main.py                   # App 入口
├── requirements.txt
└── .env
```

---

# Implementation Instructions (分步实施指南)

请按照以下步骤生成代码。请确保使用 LangGraph 1.0+ 的最新语法。

## Step 1: 依赖与配置

- **requirements.txt**: 必须包含 `fastapi`, `uvicorn`, `langgraph`, `langchain-openai`, `langchain-postgres`, `psycopg-binary`, `sqlalchemy`, `pydantic-settings`。
- **.env**: 提供 `DATABASE_URL` 模板 (例如: `postgresql+asyncpg://postgres:password@localhost:5432/aicontent`)。
- **app/core/db.py**: 配置 SQLAlchemy 的 AsyncSession。

## Step 2: 状态定义 (app/graph/state.py)

使用 TypedDict 定义 `AgentState`，必须包含：

- `topic_direction: str` — 用户初始输入（如"秋冬保湿精华推荐"）
- `target_audience: str` — 目标受众（skincare / makeup / ingredient / beginner / sensitive）
- `generated_topics: List[str]` — AI 推荐的选题
- `selected_topic: str` — 用户选中的选题
- `article_content: str` — 文章内容
- `review_feedback: str` — 用户的修改意见
- `visual_points: List[str]` — 图片文案要点
- `image_urls: List[str]` — 图片链接
- `status: str` — 当前状态描述

## Step 3: Mock 服务 (app/services/)

为了开发方便，请实现 `MockLLMService`：

- **plan_topics**: 返回固定列表 `["秋冬敏感肌保湿精华推荐", "平价彩妆好物清单｜学生党必看", "烟酰胺成分科普｜美白真相", "早C晚A护肤步骤详解", "通勤5分钟妆容教程"]`。
- **write_draft**: 返回一段 500 字的伪美妆文章（护肤/彩妆主题均可）。如果检测到 `review_feedback`，请在文章开头加上 "【根据意见已修改】" 字样以验证逻辑。文章中不得出现合规红线禁用词（最好/治疗/治愈/药用/特效等）。
- **extract_visuals**: 返回固定的图片文案要点列表，如 `["核心成分解析", "适用肤质说明", "使用步骤要点"]`。
- **generate_images**: 返回占位符图片 URL（如 `https://placehold.co/1080x1350?text=Card+1`）。

## Step 4: 构建 LangGraph (app/graph/workflow.py)

这是最关键的部分。

**持久化 (Checkpointer):** 使用 `langgraph.checkpoint.postgres.aio.AsyncPostgresSaver`。

**关键要求:** 请编写一个 `setup_checkpointer` 函数，确保在应用启动时自动在本地数据库创建 checkpoints 所需的表结构。

**节点 (Nodes):** 调用上面的 Mock 服务。

**图逻辑 (Graph Logic):**
- 使用 `interrupt_before=["human_selection_node", "human_review_node"]` (或者你认为在 1.0 中更优的写法，如明确的 Human Node)。
- 条件边 (Conditional Edge): 在审稿节点之后，判断是 Approve 还是 Reject，决定是向下走还是回退。

## Step 5: FastAPI 接口 (app/api/v1/workflow.py)

实现 3 个核心接口来驱动 Graph：

**POST /start:**
- 接收 `topic_direction` 和 `target_audience`。
- 调用 `graph.invoke`，运行直到第一个中断点。
- 返回 `thread_id` 和当前的选题列表。

**GET /state/{thread_id}:**
- 调用 `graph.get_state(config)` 获取当前快照（用于前端展示草稿或选题）。

**POST /resume/{thread_id}:**
- 接收 `action` (比如 "select_topic" 或 "approve" 或 "reject") 和 `data`。
- 核心逻辑:
  - 使用 `graph.update_state(config, {"selected_topic": ...})` 或 `{"review_feedback": ...}` 更新用户的选择/意见。
  - 使用 `graph.stream(None, config)` 恢复运行，直到下一个中断或结束。

## Step 6: 入口与初始化 (main.py)

- 初始化 FastAPI。
- 使用 `@asynccontextmanager` 定义 `lifespan`。在启动时，必须初始化数据库连接池并确保持久化所需的表 (checkpoints) 已经创建。

---

# Constraints (约束条件)

- **Local DB**: 代码应假设连接的是本地 localhost 的 Postgres，无需 Docker 配置，但要提供 SQL 建表语句或 Python 自动建表逻辑。
- **DBeaver（GUI 客户端）**: 数据库本身仍是 PostgreSQL，DBeaver 只是用作连接与管理的图形化工具——**不改变任何代码逻辑**（驱动、连接串、表结构均与直接连 PostgreSQL 一致）。在文档（README）中需补充：用 DBeaver 连接 PostgreSQL 的步骤、创建 `aicontent` 数据库的步骤（GUI 方式或 SQL 编辑器执行 `CREATE DATABASE aicontent;`），以及如何通过 DBeaver 查看 LangGraph 自动生成的 checkpoints 表。
- **LangGraph Version**: 必须严格遵循 LangGraph 1.0 语法（例如 State Management 和 Persistence 的正确用法）。使用 `AsyncPostgresSaver` 而非同步版 `PostgresSaver`。
- **Code Quality**: 代码必须包含完整的 Type Hints (类型注解) 和 异常处理。
- **合规性**: Mock 文案中不得出现美妆合规红线禁用词，以此验证合规逻辑可被注入。
- **不实现前端**: 本次只做后端，前端不在范围内。
- **不接入真实 API**: LLM 和图片生成都用 Mock，便于快速跑通流程。
