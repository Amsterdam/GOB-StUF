KEY=test_key.key
PEM=test_pem.pem
PW=gobstuf

PKCS=test_pkcs.p12

openssl req \
  -x509 \
  -sha256 \
  -nodes \
  -newkey rsa:4096 \
  -keyout $KEY \
  -out $PEM

openssl pkcs12 \
  -export \
  -out $PKCS \
  -inkey $KEY \
  -in $PEM \
  -passout "pass:$PW"

rm $KEY $PEM
