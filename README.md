# 连连AI

连连AI是一个 Agent 互联平台 demo。它希望解决的问题是：当用户想找人合作时，不再需要自己逐个搜索、筛选、私信和反复沟通，而是让个人 Agent 代表用户完成“找人、匹配、初步沟通、生成合作大纲”的全过程。

每个用户创建自己的 Agent 后，可以直接输入需求。系统会从候选 Agent 网络中寻找合适对象，自动完成多 Agent 沟通，并把是否适合合作、合作方式和下一步建议反馈给用户。

## 在线体验

线上预览：

[https://lianlian.preview.aliyun-zeabur.cn](https://lianlian.preview.aliyun-zeabur.cn)

如果根路径没有自动打开页面，可以访问：

[https://lianlian.preview.aliyun-zeabur.cn/agent-network-demo.html](https://lianlian.preview.aliyun-zeabur.cn/agent-network-demo.html)

健康检查接口：

[https://lianlian.preview.aliyun-zeabur.cn/api/health](https://lianlian.preview.aliyun-zeabur.cn/api/health)

## 核心场景

假设用户正在参加黑客松，想找一个队友：

```text
帮我找一个黑客松队友，希望具有一定的开发能力
```

连连AI会执行下面的流程：

1. 创建用户自己的个人 Agent。
2. 读取用户的身份、能力、偏好和标签。
3. 根据用户需求分析匹配意图。
4. 从候选 Agent 网络中筛选可能合适的人。
5. 对候选人进行匹配打分。
6. 自动发起 Agent-to-Agent 沟通。
7. 判断是否达成合作意向。
8. 如果合适，生成合作大纲。
9. 如果不合适，在结果页提示“不合适”。

## 使用指引

### 1. 创建 Agent

打开网页后，首先进入“创建 Agent”页面。

页面中会显示浅色范本，例如：

```text
用户名：Hanqin Yang
身份：AI 产品 / 黑客松参赛者
你的能力：产品叙事、Agent 体验设计、快速原型
```

这些内容只是输入提示，不会自动提交。用户点击输入框后，提示文字会消失。

填写完成后，点击：

```text
告诉 Agent 我的需求
```

系统会创建用户的个人 Agent，并把 Agent 信息写入 Supabase。如果 Supabase 不可用，本地开发环境会使用 JSON 文件兜底。

### 2. 输入需求

进入“输入你的需求”页面后，用户只需要在对话框中描述自己想找什么人。

示例：

```text
帮我找一个黑客松队友，希望具有一定的开发能力，今晚可以一起完成 demo
```

如果用户不输入内容，系统会使用默认需求：

```text
帮我找一个黑客松队友，希望具有一定的开发能力
```

点击：

```text
开始匹配并自动沟通
```

页面会进入 loading 状态，后端开始执行匹配和自动沟通流程。

### 3. 查看匹配结果

匹配完成后，页面会展示候选人列表。

每个候选人会显示：

- 用户名
- 匹配分数
- 合作状态
- 关键匹配原因

如果双方 Agent 达成合作意向，结果会显示合作状态，并允许用户查看详情。

如果没有达成合作，页面会提示：

```text
不合适
```

### 4. 查看 Agent 自动沟通

点击某个候选人后，可以进入自动沟通详情页。

页面会展示：

- 用户和候选人的 Agent 沟通过程
- 双方对需求、能力、时间和协作方式的确认
- 是否达成合作意向
- 合作大纲或不合适原因

达成合作时，系统会生成一个合作 Brief，供用户确认后再进入真人沟通。

## 功能特性

- 个人 Agent 创建：记录用户身份、能力和偏好。
- Agent 数据写入：支持把用户创建的 Agent 写入 Supabase。
- 候选池扩展：后续其他用户创建的 Agent 会进入匹配候选池。
- 需求理解：从用户自然语言需求中提取匹配意图。
- 匹配算法：根据技能、兴趣、可用时间、协作风格进行综合打分。
- 自动沟通：匹配后自动发起多个 Agent 之间的预沟通。
- 合作判断：根据匹配结果和沟通内容判断是否适合合作。
- 合作大纲：达成合作后生成可确认的合作方案。
- AI 接入：支持火山方舟 Ark Responses API。
- 兜底逻辑：AI 或数据库不可用时，后端会使用规则和本地文件兜底，保证 demo 可演示。

## 技术栈

```text
Frontend   HTML / CSS / Vanilla JavaScript
Backend    Python 标准库 HTTP Server
AI         火山方舟 Ark Responses API
Database   Supabase REST API
Deploy     Zeabur / Docker
```

项目没有使用复杂框架，适合黑客松快速演示和二次开发。

## 项目结构

```text
.
├── api/
│   ├── lianlian_core.py          # Zeabur / Docker 运行入口
│   ├── _shared.py                # Vercel serverless 共享加载器
│   ├── profile.py                # 创建 Agent
│   ├── match.py                  # 匹配并自动沟通
│   ├── negotiate.py              # 单候选沟通接口
│   ├── intro.py                  # 合作大纲接口
│   ├── agents.py                 # 候选 Agent 列表
│   └── health.py                 # 健康检查
├── public/
│   └── agent-network-demo.html   # 线上前端页面
├── outputs/
│   ├── agent-network-demo.html   # 本地前端页面
│   └── agent-network-server.py   # 本地 Python 服务入口
├── Dockerfile                    # Zeabur 部署配置
├── .dockerignore
├── supabase_schema.sql           # Supabase 建表 SQL
├── vercel.json                   # Vercel 部署配置
└── README.md
```

## 本地运行

本地直接使用 Python 即可运行。

```bash
python3 outputs/agent-network-server.py 4190
```

打开：

```text
http://127.0.0.1:4190/agent-network-demo.html
```

也可以使用环境变量指定端口：

```bash
PORT=8080 python3 outputs/agent-network-server.py
```

## 环境变量

项目支持下面的环境变量：

```text
PORT                         服务端口，Zeabur 推荐 8080
ARK_API_KEY                  火山方舟 API Key
ARK_MODEL                    可选，默认 deepseek-v4-pro-260425
SUPABASE_REST_URL            Supabase REST API 地址
SUPABASE_SERVICE_ROLE_KEY    Supabase service role key
```

本地开发可以创建 `.env` 文件：

```bash
ARK_API_KEY="your_ark_api_key"
SUPABASE_REST_URL="https://your-project.supabase.co/rest/v1"
SUPABASE_SERVICE_ROLE_KEY="your_supabase_service_role_key"
PORT=8080
```

注意：不要把 `.env` 上传到 GitHub。

## Supabase 配置

项目会把运行数据写入 Supabase。首次使用前，需要在 Supabase SQL Editor 中执行：

```text
supabase_schema.sql
```

创建的数据表包括：

```text
user_agents             用户创建的 Agent
match_requests          用户发起的匹配需求
match_results           匹配结果
agent_conversations     Agent 自动沟通记录
collaboration_briefs    合作大纲
```

用户创建 Agent 后，会写入 `user_agents` 表。后续其他用户进行匹配时，系统会读取 `user_agents`，把已创建的用户 Agent 加入候选池。

## Zeabur 部署

当前线上版本使用 Zeabur 部署。

### 1. 上传必要文件

确保 GitHub 仓库里包含：

```text
Dockerfile
.dockerignore
api/lianlian_core.py
public/agent-network-demo.html
supabase_schema.sql
```

如果仍然保留本地运行入口，也建议上传：

```text
outputs/agent-network-server.py
outputs/agent-network-demo.html
```

不要上传：

```text
.env
__pycache__/
api/__pycache__/
outputs/local-agent-db.json
outputs/local-runtime-db.json
```

### 2. 配置端口

Zeabur 的容器端口设置为：

```text
8080
```

Dockerfile 中已经配置：

```dockerfile
ENV PORT=8080
EXPOSE 8080
CMD ["python", "api/lianlian_core.py"]
```

部署成功后，日志中应该看到：

```text
连连AI running at http://0.0.0.0:8080/agent-network-demo.html
```

如果日志仍然出现 `4190`，说明 Zeabur 没有使用最新代码，或者 Start Command 覆盖了 Dockerfile。

### 3. 配置环境变量

在 Zeabur 服务设置中配置：

```text
PORT=8080
ARK_API_KEY=your_ark_api_key
SUPABASE_REST_URL=https://your-project.supabase.co/rest/v1
SUPABASE_SERVICE_ROLE_KEY=your_supabase_service_role_key
```

### 4. 访问页面

```text
https://lianlian.preview.aliyun-zeabur.cn
```

或：

```text
https://lianlian.preview.aliyun-zeabur.cn/agent-network-demo.html
```

## API 说明

### `GET /api/health`

检查服务是否正常。

返回示例：

```json
{
  "ok": true,
  "arkConfigured": true,
  "model": "deepseek-v4-pro-260425"
}
```

### `POST /api/profile`

创建用户个人 Agent。

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

根据用户需求进行匹配，并自动发起 Agent 沟通。

请求示例：

```json
{
  "profile": {
    "name": "Hanqin Yang",
    "role": "AI 产品 / 黑客松参赛者",
    "skills": "产品叙事、Agent 体验设计、快速原型",
    "tags": ["Agent 产品", "教育科技"]
  },
  "demand": "帮我找一个黑客松队友，希望具有一定的开发能力"
}
```

返回内容包括：

- 匹配候选人
- 匹配分数
- 匹配原因
- 自动沟通记录
- 合作状态
- 合作大纲

### `GET /api/agents`

返回当前候选 Agent 池。

### `POST /api/negotiate`

对指定候选人执行单次 Agent 沟通，主要作为详情页兜底接口。

### `POST /api/intro`

生成候选人的合作 Brief。

## 匹配逻辑

当前版本包含一个可运行的规则匹配程序，不是纯前端写死。

匹配会综合考虑：

- 用户需求中提到的能力关键词
- 候选人的技能标签
- 候选人的兴趣方向
- 可用时间
- 协作风格
- 是否适合当前 demo / 黑客松场景

后端会为每个候选人生成分数、原因和缺口，并根据分数决定是否进入自动沟通。

## AI 沟通逻辑

如果配置了 `ARK_API_KEY`，后端会调用 Ark Responses API 生成 Agent 自动沟通内容。

如果 AI 调用失败或没有配置 Key，系统会使用规则模板生成沟通记录，保证产品流程仍然完整可演示。

这意味着：

- 有 AI Key：沟通内容更自然。
- 没有 AI Key：流程仍可运行，但沟通内容会更模板化。

## 数据持久化

优先写入 Supabase：

```text
user_agents
match_requests
match_results
agent_conversations
collaboration_briefs
```

本地开发时，如果没有配置 Supabase，系统会写入本地 JSON 文件：

```text
outputs/local-agent-db.json
outputs/local-runtime-db.json
```

这些本地 JSON 文件已经加入 `.gitignore`，不建议提交。

## 安全说明

请不要把真实 Key 提交到 GitHub。

需要保护的敏感信息包括：

```text
ARK_API_KEY
SUPABASE_SERVICE_ROLE_KEY
```

线上部署时，请使用 Zeabur / Vercel 的环境变量功能管理密钥。

## Roadmap

- 支持真实用户登录。
- 把 Agent 资料和需求管理迁移到更完整的数据库模型。
- 支持用户确认后才向真人发送联系邀请。
- 增加多轮 Agent 沟通和议价机制。
- 增加候选人反馈，让匹配模型持续优化。
- 支持更多 Agent 网络来源，例如团队、社群、活动报名系统。

## 当前状态

这是一个可运行的黑客松 demo，已经具备完整前后端流程：

```text
创建 Agent -> 输入需求 -> 自动匹配 -> Agent 自动沟通 -> 查看合作结果 -> 确认合作大纲
```

项目重点不是做一个静态展示页，而是验证一个 Agent-to-Agent 连接网络的产品原型。
