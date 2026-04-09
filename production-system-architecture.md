# Production System Architecture

This document describes the production architecture currently used for Ekachi.

## Overview

Ekachi is deployed as a split-stack system:

- `ekachi.com` serves the Vue frontend from Vercel
- `api.ekachi.com` serves the FastAPI backend from an Azure VM
- MongoDB and Redis run on the same Azure VM as managed Docker containers
- The backend creates per-session sandbox containers and Claw containers through the host Docker daemon
- Model traffic is routed to an OpenAI-compatible LiteLLM proxy at `https://api.vm.jaideepch.com/v1`

## Production Topology

```mermaid
flowchart LR
    user[End User Browser]
    vercel[Vercel Project\nFrontend SPA]
    caddy[Caddy on Azure VM\napi.ekachi.com]
    backend[FastAPI Backend Container]
    mongo[(MongoDB Container)]
    redis[(Redis Container)]
    docker[Docker Daemon]
    sandbox[Ephemeral Sandbox Containers]
    claw[Ephemeral Claw Containers]
    litellm[LiteLLM-Compatible Proxy\napi.vm.jaideepch.com/v1]

    user -->|HTTPS| vercel
    user -->|HTTPS /api calls| caddy
    caddy --> backend
    backend --> mongo
    backend --> redis
    backend --> docker
    docker --> sandbox
    docker --> claw
    backend -->|LLM requests| litellm
    claw -->|callback to backend| backend
```

## Production Infrastructure

### Frontend

- Platform: Vercel
- Domain: `ekachi.com`
- Build input: `frontend/`
- Runtime model: static SPA served by Vercel CDN
- Required frontend environment variable:
  - `VITE_API_URL=https://api.ekachi.com`

### Backend

- Platform: Azure VM
- Reverse proxy: Caddy
- Public API origin: `https://api.ekachi.com`
- Private backend port: `127.0.0.1:8000`
- Deployment mode: Docker Compose

### Data Services

- MongoDB container for persistent application state
- Redis container with AOF enabled for task coordination and transient state

### Runtime Services

- Docker socket mounted read-only into the backend container
- Backend creates isolated sandbox containers on demand
- Backend creates Claw containers on demand

### Model Layer

- Provider pattern: OpenAI-compatible base URL
- Gateway: `https://api.vm.jaideepch.com/v1`
- Primary production model: `openai/gpt-5.4`
- Other configured models available through the same proxy:
  - `gemini/gemini-3.1-pro-preview`
  - `github_copilot/gpt-5.4`

## Deployment Layout On Azure VM

```mermaid
flowchart TD
    subgraph VM[Azure VM]
        caddy[Caddy Service]
        subgraph compose[Docker Compose Stack]
            backend[backend]
            mongo[mongodb]
            redis[redis]
            sandboxpull[sandbox image pull helper]
            clawpull[claw image pull helper]
        end
        docker[Host Docker Daemon]
        vols[(Docker Volumes)]
    end

    caddy --> backend
    backend --> mongo
    backend --> redis
    backend --> docker
    mongo --> vols
    redis --> vols
```

## Request Flows

### 1. User Authentication

```mermaid
sequenceDiagram
    participant U as User Browser
    participant F as Frontend on Vercel
    participant B as Backend API
    participant M as MongoDB

    U->>F: Load ekachi.com
    F->>B: POST /api/v1/auth/register or /login
    B->>M: Create or verify user
    B-->>F: JWT access/refresh tokens
    F-->>U: Authenticated session
```

Notes:

- Current auth provider is `password`
- Public registration is enabled
- Password reset email requires SMTP and is not part of the current live setup

### 2. Agent Session Creation

```mermaid
sequenceDiagram
    participant U as User Browser
    participant F as Frontend
    participant B as Backend
    participant D as Docker Daemon
    participant S as Sandbox Container
    participant R as Redis
    participant M as MongoDB

    U->>F: Submit task
    F->>B: Create session
    B->>M: Persist session metadata
    B->>D: Create sandbox container
    D-->>B: Sandbox address
    B->>R: Initialize task state
    B-->>F: Session id
    F->>B: Start streaming task events
    B-->>F: SSE event stream
    B->>S: Execute tool calls as needed
```

### 3. LLM Invocation Path

```mermaid
sequenceDiagram
    participant B as Backend
    participant G as LiteLLM Proxy
    participant P as Model Provider

    B->>G: Chat completion request
    G->>P: Routed model request
    P-->>G: Model response
    G-->>B: OpenAI-compatible response
```

## Runtime Configuration

The live system depends on these configuration groups:

### Required Application Secrets

- `API_KEY`
- `API_BASE`
- `MODEL_NAME`
- `JWT_SECRET_KEY`
- `PASSWORD_SALT`

### Required Service Configuration

- `MONGODB_URI`
- `REDIS_HOST`
- `REDIS_PORT`
- `SANDBOX_IMAGE`
- `SANDBOX_NETWORK`
- `SANDBOX_NAME_PREFIX`
- `CLAW_IMAGE`
- `MANUS_API_BASE_URL`

### Frontend Configuration

- `VITE_API_URL`

## Operations

### Deploy Process

1. Push code to the standalone GitHub repository.
2. Vercel rebuilds and redeploys the frontend from GitHub.
3. Backend changes are deployed on the Azure VM via Docker Compose.
4. Caddy continues to terminate TLS and proxy traffic to the backend container.

### Observability State

Current production setup includes basic service availability checks only. It does not yet include:

- centralized log aggregation
- metrics dashboards
- automated backups verification
- alerting
- blue/green or rolling backend deployment

## Known Architectural Constraints

- The backend is stateful and Docker-dependent, so it cannot be moved unchanged to Vercel Functions.
- MongoDB, Redis, backend, and Docker runtime currently share one Azure VM, which is operationally simple but a single point of failure.
- Domain routing for the frontend currently depends on Vercel project/domain configuration and should remain attached to the Ekachi project for automatic production cutover.

## Current Live Endpoints

- `https://ekachi.com`
- `https://api.ekachi.com`
- `https://api.vm.jaideepch.com/v1`
