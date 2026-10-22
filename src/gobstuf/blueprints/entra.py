from flask import Blueprint

from gobstuf.auth.routes import secure_route
from gobstuf.config import ENTRA_BASE_PATH
from gobstuf.logger import get_default_logger
from gobstuf.rest.routes import REST_ROUTES

logger = get_default_logger()

entra_bp = Blueprint("entra", __name__, url_prefix=ENTRA_BASE_PATH)


for rule, view_func, methods in REST_ROUTES:
    entra_bp.add_url_rule(rule=rule, methods=methods, view_func=secure_route(rule, view_func))
    logger.info(entra_bp.url_prefix + rule)
