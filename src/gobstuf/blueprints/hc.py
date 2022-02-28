from flask import Blueprint

from gobstuf.auth.routes import secure_route
from gobstuf.config import HC_BASE_PATH
from gobstuf.logger import get_default_logger
from gobstuf.rest.routes import REST_ROUTES

logger = get_default_logger()

hc_bp = Blueprint('hc', __name__, url_prefix=HC_BASE_PATH)


for rule, view_func in REST_ROUTES:
    hc_bp.add_url_rule(rule=rule, methods=['GET'], view_func=secure_route(rule, view_func))
    logger.info(hc_bp.url_prefix + rule)
