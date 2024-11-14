import socket

from flask import Flask
from flask_audit_log.middleware import AuditLogMiddleware
from flask_cors import CORS

from gobstuf.config import AUDIT_LOG_CONFIG, ROUTE_NETLOC
from gobstuf.logger import get_default_logger

logger = get_default_logger()


def _health() -> str:
    """Message telling the StUF API is OK."""
    host, port = ROUTE_NETLOC.split(":")

    try:
        s = socket.create_connection((host, int(port)), timeout=5.0)
        s.close()
    except Exception:
        return "Backend not available"

    return "Connectivity OK"


def get_flask_app():
    """
    Initializes the Flask App that serves the SOAP endpoint(s)

    :return: Flask App
    """
    app = Flask(__name__)
    # Fake origins for testing. Cross-origin resource sharing not allowed for now.
    CORS(app, resources={r"/brp/*": {"origins": ["https://bp.data.amsterdam.nl"]}})

    # Add the AuditLogMiddleware
    app.config["AUDIT_LOG"] = AUDIT_LOG_CONFIG
    AuditLogMiddleware(app)

    logger.info("Available endpoints:")

    # Health check route for HC endpoint (/brp prefix is required)
    # see oauth2-proxy.cfg for bypass
    app.route(rule="/brp/status/health/")(_health)

    # import blueprints, prints endpoints
    from gobstuf.blueprints import hc_bp, secure_bp, entra_bp

    app.register_blueprint(secure_bp)
    app.register_blueprint(hc_bp)
    app.register_blueprint(entra_bp)

    return app
