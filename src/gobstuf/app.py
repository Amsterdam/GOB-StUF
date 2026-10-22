from gobstuf.api import get_flask_app

from gobstuf.config import GOB_STUF_PORT


def get_app():
    # Start messagedriven_service in separate thread

    # DISABLED FOR NOW. Won't be supported in the old environment anymore.
    # t = Thread(target=run_message_thread)
    # t.start()

    return get_flask_app()


def run():
    """
    Get the Flask app and run it at the port as defined in config

    :return: None
    """
    app = get_app()
    app.run(port=GOB_STUF_PORT)
