_decode_base64_url() {
  local len=$((${#1} % 4))
  local result="$1"
  if [ $len -eq 2 ]; then result="$1"'=='
  elif [ $len -eq 3 ]; then result="$1"'='
  fi
  echo "$result" | tr '_-' '/+' | base64 -d
}
decode_jwt() { _decode_base64_url "$(echo -n "$1" | cut -d "." -f "${2:-2}")" | jq .; }

ENDPOINT=''
REQUEST=''
CLIENT_ID=''
USERNAME=''
PW=''

BEARER=$(
curl --silent --location --request POST "$ENDPOINT" \
--header 'Content-Type: application/x-www-form-urlencoded' \
--data-urlencode "username=$USERNAME" \
--data-urlencode "password=$PW" \
--data-urlencode "client_id=$CLIENT_ID" \
--data-urlencode 'grant_type=password' \
| jq --raw-output '.access_token' \
)

# Header
decode_jwt "$BEARER" 1
# Body
decode_jwt "$BEARER" 2

printf '=============== RESPONSE ===============\n'

bash -c 'curl --silent --location --request GET '"$REQUEST"' --header "Authorization: Bearer '"$BEARER"'" --header "Content-type: application/json" | jq'
