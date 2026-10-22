from typing import Any

import requests
from requests import Response

from gobstuf.config import CLIENT_CERT_CRT, CLIENT_CERT_KEY
from gobstuf.logger import get_default_logger

logger = get_default_logger()


def cert_get(url: str, **kwargs) -> Response:
    """
    Get request with certificate

    :param url: url to get
    :return: request response
    """
    logger.info(f"GET {url}")
    response = requests.get(url, cert=(CLIENT_CERT_CRT, CLIENT_CERT_KEY), **kwargs)
    logger.info(f"RESPONSE {response.status_code}, {response.reason}")
    return response


def cert_post(url: str, data: Any, **kwargs) -> Response:
    """
    Post request with certificate

    :param url: url to post
    :param data: data to post
    :return: request response
    """
    logger.info(f"POST {url}")
    response = requests.post(url, data, cert=(CLIENT_CERT_CRT, CLIENT_CERT_KEY), **kwargs)
    logger.info(f"RESPONSE {response.status_code}, {response.reason}")
    return response
