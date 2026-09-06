#!/usr/bin/env sh
set -eu

: "${DEPLOY_PATH:?DEPLOY_PATH must be set}"

secret_file="$DEPLOY_PATH/secrets/allowed_api_keys"
if [ ! -f "$secret_file" ]; then
    echo "Missing $secret_file" >&2
    exit 1
fi

mode="$(stat -c '%a' "$secret_file")"
case "$mode" in
    400|600) ;;
    *)
        echo "Secret file must have mode 400 or 600" >&2
        exit 1
        ;;
esac

normalized="$(tr -d '\r\n' < "$secret_file")"
if [ -z "$normalized" ] || ! printf '%s' "$normalized" | grep -Eq '^[^[:space:],]+(,[^[:space:],]+)*$'; then
    echo "Secret file must contain one or more comma-separated API keys" >&2
    exit 1
fi
