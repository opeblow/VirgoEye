#!/bin/sh
# Run on the VPS after building both images and installing backend.env (mode 600).
set -eu
release=${1:?Usage: start-vps.sh IMAGE_TAG}
base=/opt/virgoeye
test -s "$base/backend.env"
mkdir -p "$base/data"
chown 10001:10001 "$base/data"
docker network inspect virgoeye >/dev/null 2>&1 || docker network create virgoeye
for service in backend frontend; do
  if docker container inspect "virgoeye-$service" >/dev/null 2>&1; then
    docker stop "virgoeye-$service"
    docker rm "virgoeye-$service"
  fi
done
docker run -d --name virgoeye-backend --network virgoeye \
  --restart unless-stopped --memory 768m --cpus 0.8 --pids-limit 128 \
  --cap-drop ALL --security-opt no-new-privileges --read-only \
  --tmpfs /tmp:rw,noexec,nosuid,size=64m \
  --log-opt max-size=5m --log-opt max-file=2 \
  --env-file "$base/backend.env" -v "$base/data:/data" \
  "virgoeye-backend:$release"
docker run -d --name virgoeye-frontend --network virgoeye \
  --restart unless-stopped --memory 512m --cpus 0.8 --pids-limit 128 \
  --cap-drop ALL --security-opt no-new-privileges --read-only \
  --tmpfs /tmp:rw,noexec,nosuid,size=32m \
  --tmpfs /app/.next/cache:rw,noexec,nosuid,uid=1000,gid=1000,size=32m \
  --log-opt max-size=5m --log-opt max-file=2 \
  -p 127.0.0.1:3011:3000 "virgoeye-frontend:$release"
