# Ekachi

[English](README.md) | 中文

Ekachi 是一个可自托管的 AI Agent 工作台，包含 Vue 前端、FastAPI 后端、按会话创建的 Docker 沙盒，以及集成的 OpenClaw 能力。这个仓库现在是 Ekachi 的独立源码仓库，对应线上站点 `https://ekachi.com`。

## 线上环境

- 应用：`https://ekachi.com`
- API：`https://api.ekachi.com`
- 模型入口：兼容 LiteLLM 的代理 `https://api.vm.jaideepch.com/v1`
- 主模型：`openai/gpt-5.4`

## 核心能力

- 面向任务的聊天界面与持久化会话
- 为每个会话动态创建 Docker 沙盒执行工具
- 浏览器、文件、终端、搜索等工具编排
- MongoDB 持久化与 Redis 后台协调
- 密码登录认证
- 集成 OpenClaw，并为其分配独立容器运行环境

## 仓库结构

- `frontend`：Vue 3 + TypeScript + Vite 前端
- `backend`：FastAPI 后端、鉴权、会话与编排逻辑
- `sandbox`：Agent 工具执行所用的运行时镜像
- `claw`：OpenClaw 集成镜像与桥接逻辑
- `deploy/azure`：生产部署 compose 文件与参考资料

## 本地开发

1. 克隆仓库。
2. 将 `.env.example` 复制为 `.env`。
3. 至少设置以下配置：

```ini
API_KEY=sk-xxxx
API_BASE=https://api.openai.com/v1
MODEL_NAME=gpt-4o
```

4. 启动开发环境：

```bash
./dev.sh up
```

依赖变更后可重新构建：

```bash
./dev.sh down -v
./dev.sh build
./dev.sh up
```

## 生产部署

当前线上部署使用：

- Vercel 托管前端
- Azure VM 托管后端、MongoDB、Redis 与 Docker 运行时
- Caddy 负责 `api.ekachi.com` 的 TLS 与反向代理
- LiteLLM 兼容代理作为模型访问入口

完整的生产拓扑、请求链路、密钥与运维说明见 [production-system-architecture.md](production-system-architecture.md)。
