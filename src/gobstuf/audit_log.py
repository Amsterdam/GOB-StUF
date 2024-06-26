from functools import reduce
import json
import logging
import uuid

from flask import request

from flask_audit_log.util import get_client_ip

from gobstuf.config import CORRELATION_ID_HEADER, UNIQUE_ID_HEADER
from gobstuf.logger import get_default_logger

logger = get_default_logger()


def get_log_handler():
    return GOBAuditLogHandler()


class GOBAuditLogHandler(logging.StreamHandler):

    def emit(self, record):
        """
        Format the data received from the audit log middleware to match the current temporay storage
        in the database. The source and destination of the message are extracted and the msg is split
        in separate request and response logs.

        Once the audit logs can be stored in Elastic, the handler can be changed.

        The middleware logs message in the following format:
        {
            'audit': {
                'http_request': ....,
                'http_response': ....,
                'user': ....,
                ...
            }
        }
        """
        try:
            msg = json.loads(self.format(record))
        except (json.JSONDecodeError, TypeError) as exception:
            on_audit_log_exception(exception, record)
            return

        request_uuid = request.headers.get(CORRELATION_ID_HEADER, str(uuid.uuid4()))
        # Get the source and destination from the middleware log message
        source = get_nested_item(msg, 'audit', 'http_request', 'url')
        destination = get_nested_item(msg, 'audit', 'user', 'ip')
        # Strip the response data from the msg to create request only data and vice versa
        request_data = {k: v for k, v in msg.get('audit', {}).items() if k != 'http_response'}
        response_data = {k: v for k, v in msg.get('audit', {}).items() if k != 'http_request'}

        request_data.update({
            CORRELATION_ID_HEADER: request.headers.get(CORRELATION_ID_HEADER),
            UNIQUE_ID_HEADER: request.headers.get(UNIQUE_ID_HEADER),
        })

        log_request(
            source=source,
            destination=destination,
            extra_data=request_data,
            request_uuid=request_uuid)

        log_response(
            source=source,
            destination=destination,
            extra_data=response_data,
            request_uuid=request_uuid)


def log_request(**kwargs):
    logger.info(f"request: {json.dumps(kwargs)}", kwargs)


def log_response(**kwargs):
    logger.info(f"response: {json.dumps(kwargs)}", kwargs)


def on_audit_log_exception(exception, msg):
    """
    If for any reason the audit log should fail
    an error message is printed
    and the message that ought to be logged is printed

    :param exception:
    :param msg:
    :return:
    """
    logger.error(f"ERROR: Audit log request/response failed: {str(exception)}")
    logger.error("AUDIT LOG", msg)


def get_user_from_request() -> dict:
    """
    Gets the user information from the request header set by keycloak
    and returns a dict with the user information for the Datapunt Audit Logger
    """
    # Update the user info when Keycloak is going to be used
    user = {
        'authenticated': False,
        'provider': '',
        'realm': '',
        'email': '',
        'roles': [],
        'ip': get_client_ip(request)
    }
    return user


def get_nested_item(data, *keys):
    """
    Get a nested item from a dictionary

    Example: get_nested_item({'a': {'b': {'c': 5}}}, 'a', 'b', 'c') = 5
    The function eliminates ugly code like dict.get('a', {}).get('b', {}).get('c')

    :param data:
    :param keys:
    :return:
    """
    return reduce(lambda d, key: d.get(key, None) if isinstance(d, dict) else None, keys, data)
