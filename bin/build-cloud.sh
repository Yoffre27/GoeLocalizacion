#!/usr/bin/env bash
set -euo pipefail
cd /workspace/GoeLocalizacion
: "${CODEX_PROXY_CERT:?Se requiere el certificado de confianza del entorno administrado}"
env -u DOCKER_HOST -u DOCKER_CONTEXT -u DOCKER_TLS -u DOCKER_TLS_VERIFY -u DOCKER_CERT_PATH \
 docker --host=unix:///var/run/docker.sock build \
 --secret "id=proxy_ca,src=$CODEX_PROXY_CERT" -t geochavin-php:local .
