# 项目：LUMIÈRE · 妆光内容中台

# Lumiere 内容引擎（后端）

美妆公司 AI 内容运营助手 · LangGraph 1.0 + FastAPI + PostgreSQL。

## 前置条件

数据库本身仍是 PostgreSQL，**DBeaver 只是用来连接和操作 PostgreSQL 的图形化客户端工具**——代码里的连接逻辑（驱动、连接串、表结构）和直接连 PostgreSQL 时完全一致，无需修改。

### 1. 安装并启动 PostgreSQL

本地安装 PostgreSQL 15+ 并运行在 `localhost:5432`（macOS 推荐 Postgres.app，Windows 推荐官方安装包）。

### 2. 用 DBeaver 连接数据库

1. 下载安装 [DBeaver Community Edition](https://dbeaver.io/)（免费版即可）。
2. 打开 DBeaver → 左上角"新建连接"按钮（插头图标）→ 选择 **PostgreSQL**。
3. 填写连接参数：

   | 字段 | 值 |
   |---|---|
   | Host | `localhost` |
   | Port | `5432` |
   | Database | `postgres`（默认库，连上后再建业务库） |
   | Username | `postgres` |
   | Password | 你的 postgres 密码 |

4. 点击"测试连接"，首次会提示下载 PostgreSQL JDBC 驱动，点下载即可。
5. 测试通过 → 完成，左侧导航出现连接。

### 3. 用 DBeaver 创建业务数据库

1. 左侧右键你的 PostgreSQL 连接 → **创建 → 数据库**。
2. 数据库名填 `aicontent` → 确定。
3. （可选）展开 `aicontent` 数据库 → 右键 → **SQL 编辑器 → 新建 SQL 编辑器**，可执行 SQL：

   ```sql
   CREATE DATABASE aicontent;
   ```
   > 若通过上面 GUI 已建库，此 SQL 无需再执行。

### 4. 确认 `.env` 中的 `DATABASE_URL` 用户名密码正确

```env
DATABASE_URL=postgresql+asyncpg://postgres:你的密码@localhost:5432/aicontent
```

启动应用后，LangGraph 的 `AsyncPostgresSaver` 会自动在 `aicontent` 库下创建 checkpoints 相关表（`checkpoints`、`checkpoints_writes`、`checkpoints_blobs` 等），可在 DBeaver 左侧 `aicontent → Schemas → public → Tables` 下查看。

## 安装与启动

```bash
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

启动时会自动创建 LangGraph checkpoints 所需表结构。

## 工作流

```
START → plan_topics
        → INTERRUPT(human_selection)   等待运营选题
        → write_draft
        → INTERRUPT(human_review)      等待审稿
            ├─ approve → extract_visuals → generate_images → END
            └─ reject  → 回到 write_draft（带 feedback 重写）
```

## API

### 1. 发起任务

```bash
curl -X POST http://localhost:8000/api/v1/workflow/start \
  -H "Content-Type: application/json" \
  -d '{"topic_direction":"秋冬保湿精华推荐","target_audience":"skincare"}'
```

返回 `thread_id` + 选题列表，流程暂停在 `human_selection`。

### 2. 查看状态

```bash
curl http://localhost:8000/api/v1/workflow/state/{thread_id}
```

### 3. 恢复（选题 / 审稿）

选题：
```bash
curl -X POST http://localhost:8000/api/v1/workflow/resume/{thread_id} \
  -H "Content-Type: application/json" \
  -d '{"action":"select_topic","data":"秋冬敏感肌保湿精华推荐"}'
```

审稿通过：
```bash
curl -X POST http://localhost:8000/api/v1/workflow/resume/{thread_id} \
  -H "Content-Type: application/json" \
  -d '{"action":"approve"}'
```

审稿驳回（带修改意见，触发重写）：
```bash
curl -X POST http://localhost:8000/api/v1/workflow/resume/{thread_id} \
  -H "Content-Type: application/json" \
  -d '{"action":"reject","data":"第三段太干，补充敏感肌适用性说明"}'
```

## 目录结构

```
backend/
├── app/
│   ├── api/v1/workflow.py      # 核心接口：start / state / resume
│   ├── core/                   # config + db
│   ├── graph/                  # LangGraph：state / nodes / workflow / utils
│   ├── services/               # Mock LLM + Mock 图片
│   └── main.py
├── requirements.txt
└── .env
```

## 扩展位

- 真实 LLM：替换 `app/services/llm_mock.py`，实现相同接口即可，graph 层不动。
- 真实图片：替换 `app/services/image_mock.py`。
- 公众号发布：在 `services/` 加 `publisher`，接 `wechat` 官方 API。
- 小红书：无官方 API，仅打包发布物供人工发布。
