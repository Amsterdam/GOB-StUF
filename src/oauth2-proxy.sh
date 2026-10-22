#!/usr/bin/env bash

set -u # crash on missing env
set -e # stop on any error


if [ -n "$OAUTH2_PROXY_ENTRA_COOKIE_SECRET" ]; then
	echo "Running OAuth2 Proxy Entra ID (pid: $$)"
	./oauth2-proxy \
		--alpha-config oauth2-proxy-entra.yml \
		--cookie-secret $OAUTH2_PROXY_ENTRA_COOKIE_SECRET \
		--config oauth2-proxy-entra.cfg &
else
	echo "No OAuth2 Proxy Entra ID environment variables"
fi

# Make sure Keycloak OAuth2 procies are killed by uWSGI
trap "echo 'Terminated OAuth2 Proxies'" EXIT

echo "Running OAuth2 Proxy Keycloak (pid: $$)"
./oauth2-proxy \
	--config oauth2-proxy.cfg \
	--cookie-secret $OAUTH2_PROXY_COOKIE_SECRET
