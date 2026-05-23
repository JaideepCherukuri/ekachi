#!/usr/bin/env bash
set -euo pipefail

AWS_REGION="${AWS_REGION:-us-east-1}"
SECRET_ID="${SECRET_ID:?SECRET_ID is required}"
REPO_DIR="${REPO_DIR:-/opt/ekachi}"
REPO_URL="${REPO_URL:-https://github.com/JaideepCherukuri/ekachi.git}"
BRANCH="${BRANCH:-main}"

if [[ ! -d "${REPO_DIR}/.git" ]]; then
  mkdir -p "$(dirname "${REPO_DIR}")"
  git clone --branch "${BRANCH}" "${REPO_URL}" "${REPO_DIR}"
else
  git -C "${REPO_DIR}" fetch origin "${BRANCH}"
  git -C "${REPO_DIR}" checkout "${BRANCH}"
  git -C "${REPO_DIR}" reset --hard "origin/${BRANCH}"
fi

secret_file="$(mktemp)"
trap 'rm -f "${secret_file}"' EXIT
aws secretsmanager get-secret-value \
  --region "${AWS_REGION}" \
  --secret-id "${SECRET_ID}" \
  --query SecretString \
  --output text > "${secret_file}"

REPO_DIR="${REPO_DIR}" SECRET_FILE="${secret_file}" python3 - <<'PY'
import json
import os
import pathlib
import secrets
import sys

repo_dir = pathlib.Path(os.environ["REPO_DIR"])
secret = json.loads(pathlib.Path(os.environ["SECRET_FILE"]).read_text())

defaults = {
    "API_DOMAIN": "api.ekachi.com",
    "ACME_EMAIL": "jaideep.cherukuri7@gmail.com",
    "MODEL_PROVIDER": "openai",
    "TEMPERATURE": "0.7",
    "MAX_TOKENS": "2000",
    "MONGODB_URI": "mongodb://mongodb:27017",
    "MONGODB_DATABASE": "manus",
    "REDIS_HOST": "redis",
    "REDIS_PORT": "6379",
    "REDIS_DB": "0",
    "SANDBOX_IMAGE": "simpleyyt/manus-sandbox:latest",
    "SANDBOX_NAME_PREFIX": "sandbox",
    "SANDBOX_TTL_MINUTES": "30",
    "SANDBOX_NETWORK": "manus-network",
    "SEARCH_PROVIDER": "bing_web",
    "AUTH_PROVIDER": "password",
    "PASSWORD_HASH_ROUNDS": "600000",
    "JWT_ALGORITHM": "HS256",
    "JWT_ACCESS_TOKEN_EXPIRE_MINUTES": "30",
    "JWT_REFRESH_TOKEN_EXPIRE_DAYS": "7",
    "CLAW_ENABLED": "true",
    "CLAW_IMAGE": "simpleyyt/manus-claw:latest",
    "CLAW_NAME_PREFIX": "manus-claw",
    "CLAW_TTL_SECONDS": "1800",
    "CLAW_NETWORK": "manus-network",
    "CLAW_READY_TIMEOUT": "300",
    "MANUS_API_BASE_URL": "http://backend:8000",
    "SHOW_GITHUB_BUTTON": "false",
    "GITHUB_REPOSITORY_URL": "https://github.com/JaideepCherukuri/ekachi",
    "LOG_LEVEL": "INFO",
}

merged: dict[str, str] = {k: str(v) for k, v in defaults.items()}
for key, value in secret.items():
    if value is not None:
        merged[key] = str(value)

if not merged.get("AVAILABLE_MODELS"):
    merged["AVAILABLE_MODELS"] = merged.get("MODEL_NAME", "")

for generated_key in ("JWT_SECRET_KEY", "PASSWORD_SALT"):
    if not merged.get(generated_key) or merged[generated_key] == "replace-me":
        merged[generated_key] = secrets.token_urlsafe(48)

required = [
    "API_DOMAIN",
    "ACME_EMAIL",
    "API_KEY",
    "API_BASE",
    "MODEL_NAME",
    "JWT_SECRET_KEY",
    "PASSWORD_SALT",
]
missing = [key for key in required if not merged.get(key)]
if missing:
    print(f"Missing required deployment values: {', '.join(missing)}", file=sys.stderr)
    sys.exit(1)

ordered_keys = [
    "API_DOMAIN",
    "ACME_EMAIL",
    "API_KEY",
    "API_BASE",
    "MODEL_NAME",
    "AVAILABLE_MODELS",
    "MODEL_PROVIDER",
    "TEMPERATURE",
    "MAX_TOKENS",
    "MONGODB_URI",
    "MONGODB_DATABASE",
    "REDIS_HOST",
    "REDIS_PORT",
    "REDIS_DB",
    "SANDBOX_IMAGE",
    "SANDBOX_NAME_PREFIX",
    "SANDBOX_TTL_MINUTES",
    "SANDBOX_NETWORK",
    "SEARCH_PROVIDER",
    "AUTH_PROVIDER",
    "PASSWORD_SALT",
    "PASSWORD_HASH_ROUNDS",
    "JWT_SECRET_KEY",
    "JWT_ALGORITHM",
    "JWT_ACCESS_TOKEN_EXPIRE_MINUTES",
    "JWT_REFRESH_TOKEN_EXPIRE_DAYS",
    "CLAW_ENABLED",
    "CLAW_IMAGE",
    "CLAW_NAME_PREFIX",
    "CLAW_TTL_SECONDS",
    "CLAW_NETWORK",
    "CLAW_READY_TIMEOUT",
    "MANUS_API_BASE_URL",
    "SHOW_GITHUB_BUTTON",
    "GITHUB_REPOSITORY_URL",
    "LOG_LEVEL",
]

env_path = repo_dir / "deploy" / "aws" / ".env.production"
lines = []
seen = set()
for key in ordered_keys:
    if key in merged:
        lines.append(f"{key}={merged[key]}")
        seen.add(key)

for key in sorted(set(merged) - seen):
    lines.append(f"{key}={merged[key]}")

env_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
PY

cd "${REPO_DIR}"
docker compose --env-file deploy/aws/.env.production -f deploy/aws/docker-compose.prod.yml pull caddy sandbox claw mongodb redis
docker compose --env-file deploy/aws/.env.production -f deploy/aws/docker-compose.prod.yml build backend
docker compose --env-file deploy/aws/.env.production -f deploy/aws/docker-compose.prod.yml up -d --remove-orphans
docker compose --env-file deploy/aws/.env.production -f deploy/aws/docker-compose.prod.yml ps
