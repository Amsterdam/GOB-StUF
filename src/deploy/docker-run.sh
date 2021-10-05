#!/usr/bin/env bash
set -u   # crash on missing env variables
set -e   # stop on any error
set -x

# Print sha1 of pkcs12 file
sha1sum $PKCS12_FILENAME

echo "Checking health keycloak..."
wget "${OAUTH2_PROXY_OIDC_ISSUER_URL}/.well-known/openid-configuration" -O /dev/null -q
echo "Keycloak is active"

# Secure endpoints
./oauth2-proxy --config oauth2-proxy.cfg 2>&1 | tee /var/log/oauth2-proxy/oauth2proxy.log &

# Start web server
exec uwsgi
