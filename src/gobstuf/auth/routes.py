from typing import Optional, Callable

from flask import g, request, url_for

from gobcore.secure.request import is_secured_request, extract_roles, USER_NAME_HEADER


REQUIRED_ROLE_PREFIX = 'fp_'
REQUIRED_ROLE = 'brp_r'

MKS_USER_KEY = 'MKS_GEBRUIKER'
MKS_APPLICATION_KEY = 'MKS_APPLICATIE'


def secure_route(rule: str, func: Callable, name: str = None) -> Callable:
    """
    Secure routes are protected by oauth2-proxy.
    The headers that are used to identify the user and/or role should be present.

    :param rule: route/rule to secure
    :param func: view function
    :param name: (optional) route name
    :return: 403 if access is not allowed, else `func`
    """
    def wrapper(*args, **kwargs) -> tuple[str, int]:
        # Check that the endpoint is protected by oauth2-proxy and check access
        if is_secured_request(request.headers) and _allows_access(rule, *args, **kwargs):
            return func(*args, **kwargs)
        else:
            return "Forbidden", 403

    wrapper.__name__ = func.__name__ if name is None else name
    return wrapper


def _get_roles() -> list[str]:
    """Gets the user roles from the request headers."""
    try:
        return extract_roles(request.headers)
    except AttributeError:
        return []


def _get_role_fp(roles: list[str]) -> Optional[str]:
    """Get the first active `functieprofiel` role, which starts with 'fp_'."""
    return next((role for role in roles if role.startswith(REQUIRED_ROLE_PREFIX)), None)


def _allows_access(rule, *args, **kwargs) -> bool:
    """
    Check access to paths with variable catalog/collection names
    """
    roles = _get_roles()
    fp_role = _get_role_fp(roles)

    if REQUIRED_ROLE in roles and fp_role:
        # Store the MKS USER and APPLICATION in the global object and allow access
        setattr(g, MKS_APPLICATION_KEY, fp_role)
        setattr(g, MKS_USER_KEY, request.headers.get(USER_NAME_HEADER, ""))
        return True

    return False


def get_auth_url(view_name, **kwargs):
    url = url_for(view_name, **kwargs)
    return f"{request.scheme}://{request.host}{url}"
