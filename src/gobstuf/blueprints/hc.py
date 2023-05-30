from flask import Blueprint

from gobstuf.config import HC_BASE_PATH
from gobstuf.logger import get_default_logger

logger = get_default_logger()

hc_bp = Blueprint('hc', __name__, url_prefix=HC_BASE_PATH)
