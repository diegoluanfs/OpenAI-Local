#!/usr/bin/env sh
set -eu

: "${DEPLOY_PATH:?DEPLOY_PATH must be set}"
DEPLOY_ENV="${DEPLOY_ENV:-staging}"

cd "$DEPLOY_PATH"
if [ ! -s .previous-image-tag ]; then
    echo "No previous image tag is available" >&2
    exit 1
fi

export IMAGE_TAG="$(cat .previous-image-tag)"
export IMAGE_REPOSITORY="${IMAGE_REPOSITORY:-ghcr.io/diegoluanfs/openai-local}"
compose="docker compose --env-file .env.production -f docker-compose.production.yml"
$compose config --quiet
$compose pull local-llm-server
$compose up -d local-llm-server
printf '%s\n' "$IMAGE_TAG" > .deployed-image-tag

domain="$(sed -n 's/^DOMAIN=//p' .env.production | tail -n 1)"
api_key="$(cut -d ',' -f 1 secrets/allowed_api_keys | tr -d '\r\n')"
base_url="https://$domain"
curl --fail --silent --show-error "$base_url/health/live" >/dev/null
curl --fail --silent --show-error "$base_url/health/ready" >/dev/null
curl --fail --silent --show-error -H "Authorization: Bearer $api_key" "$base_url/v1/models" >/dev/null

echo "$DEPLOY_ENV rollback completed and authenticated: $IMAGE_TAG"
