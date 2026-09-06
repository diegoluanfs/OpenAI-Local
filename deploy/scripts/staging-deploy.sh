#!/usr/bin/env sh
set -eu

: "${IMAGE_TAG:?IMAGE_TAG must be set}"
: "${DEPLOY_PATH:?DEPLOY_PATH must be set}"

cd "$DEPLOY_PATH"

if [ ! -f .env.production ]; then
    echo "Missing $DEPLOY_PATH/.env.production" >&2
    exit 1
fi
if [ ! -f secrets/allowed_api_keys ]; then
    echo "Missing $DEPLOY_PATH/secrets/allowed_api_keys" >&2
    exit 1
fi

if [ -f .deployed-image-tag ]; then
    cp .deployed-image-tag .previous-image-tag
fi
printf '%s\n' "$IMAGE_TAG" > .deployed-image-tag

export IMAGE_TAG
export IMAGE_REPOSITORY="${IMAGE_REPOSITORY:-ghcr.io/diegoluanfs/openai-local}"

compose="docker compose --env-file .env.production -f docker-compose.production.yml"
$compose config --quiet
$compose pull local-llm-server caddy
$compose up -d local-llm-server caddy

for attempt in $(seq 1 30); do
    if curl --fail --silent --show-error "http://127.0.0.1:8000/health/live" >/dev/null; then
        echo "Staging deployment healthy: $IMAGE_TAG"
        exit 0
    fi
    sleep 2
done

echo "Staging deployment did not become healthy" >&2
$compose logs --tail=100 local-llm-server caddy >&2
exit 1
