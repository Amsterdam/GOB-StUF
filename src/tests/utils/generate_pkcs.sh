#!/usr/bin/env bash
export KEY=test_key.key
export PEM=test_pem.pem
export PW=gobstuf

export PKCS=test_pkcs.p12

openssl req \
  -x509 \
  -sha256 \
  -nodes \
  -newkey rsa:4096 \
  -keyout $KEY \
  -out $PEM \
  -days 3650

openssl pkcs12 \
  -export \
  -out $PKCS \
  -inkey $KEY \
  -in $PEM \
  -passout "pass:$PW"

rm $KEY $PEM
