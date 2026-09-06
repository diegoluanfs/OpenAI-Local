#!/usr/bin/env sh
set -eu

: "${DEPLOY_PATH:?DEPLOY_PATH must be set}"

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

echo "Rollback completed: $IMAGE_TAG"
