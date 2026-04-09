# Ekachi Frontend

[English](README.md) | 中文

这是 Ekachi 的 Vite 前端，负责任务聊天工作台、会话历史、认证流程、文件上传体验、工具面板以及 OpenClaw 入口。

## 环境变量

创建 `.env.development`：

```ini
VITE_API_URL=http://127.0.0.1:8000
```

生产环境当前使用：

```ini
VITE_API_URL=https://api.ekachi.com
```

## 常用命令

```bash
npm install
npm run dev
npm run build
```

## 部署说明

- 生产前端托管在 Vercel
- SPA 路由重写配置见 `vercel.json`
- 自动部署目标仓库为独立的 `ekachi` GitHub 仓库
