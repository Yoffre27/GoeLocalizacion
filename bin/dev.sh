#!/usr/bin/env bash
set -euo pipefail
cd /workspace/GoeLocalizacion
# Conserva las credenciales existentes; solo genera valores locales la primera vez.
if [ ! -f .env ]; then
 python3 - <<'PY'
import secrets,os
fd=os.open('.env',os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600)
with os.fdopen(fd,'w') as f:
 f.write('DB_PASSWORD='+secrets.token_hex(24)+'\nMYSQL_ROOT_PASSWORD='+secrets.token_hex(24)+'\n')
PY
fi
docker compose up -d --wait
curl --fail --silent --show-error 'http://127.0.0.1:8080/?page=api' >/dev/null
printf 'GeoChavín: PHP y MySQL iniciados; API verificada.\n'
