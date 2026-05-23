# Ekachi

English | [中文](README_zh.md)

Ekachi is a self-hosted AI agent workspace with a Vue frontend, a FastAPI backend, Docker-based per-session sandboxes, and integrated OpenClaw support. This repository is the standalone home for the Ekachi deployment running at `https://ekachi.com`.

## Live Production

- App: `https://ekachi.com`
- API: `https://api.ekachi.com`
- Runtime model access: OpenAI-compatible upstream configured through `API_BASE`

## Core Capabilities

- Task-oriented chat UI with persistent sessions
- Per-session Docker sandbox creation for tool execution
- Browser, file, shell, and web-search tool orchestration
- MongoDB-backed persistence and Redis-backed background coordination
- Password authentication
- OpenClaw companion flow with isolated container runtime

## Repository Layout

- `frontend`: Vue 3 + TypeScript + Vite web app
- `backend`: FastAPI application, orchestration, auth, session APIs
- `sandbox`: Runtime image used for agent tool execution
- `claw`: OpenClaw integration image and bridge logic
- `deploy/aws`: AWS EC2 production deployment path
- `deploy/azure`: Legacy deployment reference material

## Local Development

1. Clone the repository.
2. Copy `.env.example` to `.env`.
3. Set at least:

```ini
API_KEY=sk-xxxx
API_BASE=https://api.openai.com/v1
MODEL_NAME=gpt-4o
```

4. Start the development stack:

```bash
./dev.sh up
```

When dependencies change, rebuild with:

```bash
./dev.sh down -v
./dev.sh build
./dev.sh up
```

## Deployment

The current production deployment uses:

- Vercel for the frontend
- AWS EC2 in `us-east-1` for the backend, MongoDB, Redis, and Docker runtime
- Caddy for TLS termination and reverse proxying on `api.ekachi.com`
- AWS Secrets Manager for runtime secrets
- Direct OpenAI-compatible upstream model access configured through `API_BASE`

See [production-system-architecture.md](production-system-architecture.md) for the full production topology, request flows, secrets, and operational notes.

## Frontend Build

```bash
cd frontend
npm install
npm run build
```

For production frontend builds, set:

```ini
VITE_API_URL=https://api.ekachi.com
```
