from typing import Any

import jwt

# Headers as set by OAuth2 Proxy
ACCESS_TOKEN_HEADER = "X-Forwarded-Access-Token"
USER_EMAIL_HEADER = "X-Forwarded-Email"
USER_NAME_HEADER = "X-Forwarded-Preferred-Username"


def decode_token(headers: dict) -> dict[str, Any]:
    try:
        if token_str := headers.get(ACCESS_TOKEN_HEADER):
            return jwt.decode(token_str, options={"verify_signature": False}, algorithms=["RS256", "HS256"])
    except jwt.exceptions.DecodeError:
        pass
    return {}


def extract_roles(headers: dict) -> list[str]:
    """Extracts roles from given request headers

    :param headers:
    :return:
    """
    decoded = decode_token(headers)

    # Keycloak case
    if realm := decoded.get("realm_access"):
        return realm.get("roles", [])

    return decoded.get("roles", [])


def is_secured_request(headers: dict):
    return bool(headers.get(ACCESS_TOKEN_HEADER))
