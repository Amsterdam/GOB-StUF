#!/usr/bin/env bash
set -u   # crash on missing env variables
set -e   # stop on any error
set -x

DOMAIN_NAME=$(echo "${OAUTH2_PROXY_OIDC_ISSUER_URL}" | sed -e 's|^[^/]*//||' -e 's|/.*$||')
timeout 60 bash -c "until cat < /dev/null > /dev/tcp/${DOMAIN_NAME}/443; do sleep 5; done"
# Secure endpoints
./oauth2-proxy --config oauth2-proxy.cfg 2>&1 | tee /var/log/oauth2-proxy/oauth2proxy.log &

# Start web server
exec uwsgi
