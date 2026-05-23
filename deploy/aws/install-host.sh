#!/usr/bin/env bash
set -euo pipefail

dnf -y update
dnf -y install git docker jq curl python3
systemctl enable --now docker

if id ec2-user >/dev/null 2>&1; then
  usermod -aG docker ec2-user
fi

if ! docker compose version >/dev/null 2>&1; then
  install -d /usr/local/lib/docker/cli-plugins
  curl -fsSL "https://github.com/docker/compose/releases/download/v2.39.4/docker-compose-linux-x86_64" \
    -o /usr/local/lib/docker/cli-plugins/docker-compose
  chmod +x /usr/local/lib/docker/cli-plugins/docker-compose
fi

mkdir -p /opt/ekachi
