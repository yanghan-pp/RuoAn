# 连连AI

连连AI是一个 Agent 互联平台 demo。它的核心想法是：每个用户都有自己的个人 Agent，当用户提出需求后，Agent 会替用户寻找合适的人、筛选候选、与对方 Agent 自动沟通，并把合作结论和合作大纲反馈给用户确认。

这个项目适合用于黑客松、产品原型演示和 Agent-to-Agent 协作流程验证。

## 功能亮点

- 创建个人 Agent：记录用户身份、能力和偏好。
- 输入需求：用户只需要描述自己想找什么样的人。
- 自动匹配：后端根据技能、兴趣、时间和协作风格对候选 Agent 打分。
- 多 Agent 沟通：匹配后自动发起 Agent 间沟通，不需要用户逐个点击触发。
- 合作结论：候选人会被标记为“已达成合作意向”或“不合适”。
- 合作大纲：达成合作后生成可供用户确认的合作 Brief。
- 本地记录：每次创建用户 Agent 都会写入本地 JSON 文件，后续可替换为真实数据库。
- AI 接入：支持通过火山方舟 Ark Responses API 生成 Agent 沟通内容。

## 产品流程

1. 用户创建自己的个人 Agent。
2. 用户输入需求，例如“帮我找一个黑客松队友，希望具有一定的开发能力”。
3. 系统自动匹配候选 Agent。
4. 多个候选 Agent 自动进行沟通。
5. 前端展示匹配结果：
   - 已达成合作意向，等待用户确认
   - 不合适
6. 用户点击候选人，查看自动沟通记录和合作大纲。
7. 用户确认合作大纲后，再进入真人沟通或引荐。

## 项目结构

```text
outputs/
  agent-network-demo.html      # 前端单页应用
  agent-network-server.py      # Python 后端服务
  local-agent-db.json          # 本地 Agent 创建记录
  local-runtime-db.json        # 本地匹配和沟通记录 fallback
api/
  profile.py                   # Vercel API: 创建 Agent
  match.py                     # Vercel API: 匹配并自动沟通
  negotiate.py                 # Vercel API: 单候选沟通兜底
  intro.py                     # Vercel API: 合作大纲
  agents.py                    # Vercel API: 候选池
  health.py                    # Vercel API: 健康检查
public/
  agent-network-demo.html      # Vercel 静态前端入口
supabase_schema.sql            # Supabase 建表 SQL
vercel.json                    # Vercel 根路径跳转配置
```

## 本地运行

项目不依赖复杂框架，直接使用 Python 标准库即可运行。

```bash
python3 outputs/agent-network-server.py 4190
```

启动后访问：

```text
http://127.0.0.1:4190/agent-network-demo.html
```

## AI 配置

后端支持通过环境变量配置 Ark API Key：

```bash
ARK_API_KEY="your_api_key_here" python3 outputs/agent-network-server.py 4190
```

默认模型配置在 `outputs/agent-network-server.py` 中：

```python
ARK_MODEL = "deepseek-v4-pro-260425"
```

如果 AI 调用失败，系统会自动使用后端规则和模板兜底，保证 demo 流程仍然可以完成。

## Supabase 配置

项目支持把运行数据写入 Supabase。先在 Supabase SQL Editor 中执行：

```text
supabase_schema.sql
```

然后用环境变量启动服务：

```bash
SUPABASE_REST_URL="https://your-project.supabase.co/rest/v1" \
SUPABASE_SERVICE_ROLE_KEY="your_service_role_key" \
ARK_API_KEY="your_api_key_here" \
python3 outputs/agent-network-server.py 4190
```

写入 Supabase 的数据包括：

- 用户创建的 Agent：`user_agents`
- 用户需求：`match_requests`
- 匹配结果：`match_results`
- Agent 沟通记录：`agent_conversations`
- 合作大纲：`collaboration_briefs`

如果没有配置 Supabase，或者写入失败，系统会自动写入本地 JSON fallback。

## Vercel 部署

项目已经包含 Vercel 友好的结构：

```text
api/       # Python serverless functions
public/    # 静态前端页面
vercel.json
```

部署步骤：

1. 把这些文件上传到 GitHub：

```text
README.md
.gitignore
supabase_schema.sql
vercel.json
api/
public/
outputs/agent-network-server.py
outputs/agent-network-demo.html
```

2. 在 Vercel 导入这个 GitHub 仓库。

3. 在 Vercel Project Settings -> Environment Variables 中配置：

```text
SUPABASE_REST_URL
SUPABASE_SERVICE_ROLE_KEY
ARK_API_KEY
```

4. 部署完成后访问：

```text
https://your-vercel-domain.vercel.app/agent-network-demo.html
```

根路径 `/` 也会跳转到这个页面。

## 后端接口

### `POST /api/profile`

创建用户的个人 Agent，并写入本地记录文件。

请求示例：

```json
{
  "profile": {
    "name": "Hanqin Yang",
    "role": "AI 产品 / 黑客松参赛者",
    "skills": "产品叙事、Agent 体验设计、快速原型",
    "tags": ["Agent 产品", "教育科技", "快速原型"]
  }
}
```

### `POST /api/match`

根据用户需求匹配候选 Agent，并自动完成多个 Agent 间的沟通。

请求示例：

```json
{
  "profile": {
    "name": "Hanqin Yang"
  },
  "demand": "帮我找一个黑客松队友，希望具有一定的开发能力"
}
```

返回内容包括候选人、匹配分数、沟通结果和合作结论。

### `POST /api/negotiate`

对单个候选 Agent 发起沟通，主要用于详情页兜底。

### `POST /api/intro`

生成候选人的引荐 Brief。

## 本地数据

当前版本会把创建过的用户 Agent 写入：

```text
outputs/local-agent-db.json
```

匹配、沟通和合作大纲会写入：

```text
outputs/local-runtime-db.json
```

这两个文件可以视为临时本地数据库。接入 Supabase 后，它们会作为 fallback 继续保留。

## 安全注意事项

不要把真实 API Key 提交到 GitHub。

发布前建议：

- 删除或替换源码里的真实 Key。
- 使用 `ARK_API_KEY` 环境变量管理密钥。
- 使用 `SUPABASE_SERVICE_ROLE_KEY` 环境变量管理 Supabase service role。
- 将本地 JSON 数据文件加入 `.gitignore`，避免提交本地用户数据。

## 当前状态

这是一个可运行的黑客松 demo，已经具备完整前后端流程：

- 前端：单页网页应用
- 后端：Python HTTP 服务
- AI：Ark Responses API
- 数据：Supabase，失败时 fallback 到本地 JSON
- 流程：创建 Agent → 输入需求 → 自动匹配与沟通 → 查看结果与合作大纲
