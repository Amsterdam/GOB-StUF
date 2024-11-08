#!/usr/bin/env bash

set -u # crash on missing env
set -e # stop on any error


echo "Running Keycloak OAuth2 Proxy (pid: $$)"
./oauth2-proxy --config oauth2-proxy.cfg &

# Make sure Keycloak OAuth2 procies are killed by uWSGI
trap "echo 'Terminated OAuth2 Proxies'" EXIT

echo "Running Entra ID OAuth2 Proxy (pid: $$)"
./oauth2-proxy --alpha-config oauth2-proxy-entra.yml --config oauth2-proxy-entra.cfg
