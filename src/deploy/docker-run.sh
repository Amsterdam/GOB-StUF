#!/usr/bin/env bash
set -u   # crash on missing env variables
set -e   # stop on any error
set -x

# Print sha1 of pkcs12 file
sha1sum $PKCS12_FILENAME

# Temporarily override url to test if this makes oauth2 work with hc.
export OAUTH2_PROXY_REDIRECT_URL=https://acc.hc.data.amsterdam.nl/gob_stuf/oauth/callback

echo "Checking health keycloak..."
wget "${OAUTH2_PROXY_OIDC_ISSUER_URL}/.well-known/openid-configuration" -O /dev/null -q
echo "Keycloak is active"

echo "Wait 10 seconds until keycloak is ready..."
sleep 10

# Secure endpoints
./oauth2-proxy --config oauth2-proxy.cfg 2>&1 | tee /var/log/oauth2-proxy/oauth2proxy.log &

# Start web server
exec uwsgi
