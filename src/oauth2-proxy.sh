#!/usr/bin/env bash

set -u # crash on missing env
set -e # stop on any error


if [ -n "$OAUTH2_PROXY_ENTRA_COOKIE_SECRET" ]; then
	echo "Running Entra ID OAuth2 Proxy (pid: $$)"
	./oauth2-proxy --alpha-config oauth2-proxy-entra.yml --cookie-secret $OAUTH2_PROXY_ENTRA_COOKIE_SECRET --config oauth2-proxy-entra.cfg &
else
	echo "No Entra ID OAuth2 Proxy environment variables"
fi

# Make sure Keycloak OAuth2 procies are killed by uWSGI
trap "echo 'Terminated OAuth2 Proxies'" EXIT

echo "Running Keycloak OAuth2 Proxy (pid: $$)"
./oauth2-proxy --config oauth2-proxy.cfg --cookie-secret $OAUTH2_PROXY_COOKIE_SECRET
