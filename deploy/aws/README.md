# AWS Deployment

This deployment target restores Ekachi as a single control-plane host on AWS,
matching the current runtime assumptions in the codebase:

- one backend process that keeps in-memory active task state
- host Docker socket access for per-session sandbox creation
- host Docker socket access for OpenClaw container creation
- local MongoDB and Redis containers for persistence and coordination

## Architecture

- AWS region: `us-east-1`
- Compute: single EC2 instance
- Public ingress: `api.ekachi.com`
- TLS: Caddy container with automatic ACME
- Runtime services:
  - `backend` built from this repository
  - `sandbox` pulled from `simpleyyt/manus-sandbox:latest`
  - `claw` pulled from `simpleyyt/manus-claw:latest`
  - `mongodb`
  - `redis`

## Secrets Manager Shape

Create one JSON secret and point `deploy.sh` at it with `SECRET_ID`.

Minimum shape:

```json
{
  "API_DOMAIN": "api.ekachi.com",
  "ACME_EMAIL": "you@example.com",
  "API_KEY": "provider-key",
  "API_BASE": "https://api.openai.com/v1",
  "MODEL_NAME": "gpt-4o"
}
```

Recommended additions:

```json
{
  "AVAILABLE_MODELS": "gpt-4o",
  "JWT_SECRET_KEY": "generated-or-supplied",
  "PASSWORD_SALT": "generated-or-supplied",
  "SEARCH_PROVIDER": "bing_web"
}
```

## Host Bootstrap

Run as root on an Amazon Linux 2023 EC2 host:

```bash
bash ./deploy/aws/install-host.sh
AWS_REGION=us-east-1 SECRET_ID=ekachi/prod/app bash ./deploy/aws/deploy.sh
```

## Notes

- The backend now exposes `GET /health` for reverse-proxy and operator checks.
- Azure OpenAI-compatible upstreams require `api-key` auth headers in the Claw proxy path; the backend has been updated to handle that automatically based on `API_BASE`.
