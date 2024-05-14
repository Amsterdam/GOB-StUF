from unittest import TestCase
from unittest.mock import patch, MagicMock

from gobstuf.app import run, get_app


class TestApp(TestCase):

    @patch("gobstuf.app.get_flask_app")
    def test_get_app(self, mock_flask_app):
        self.assertEqual(mock_flask_app(), get_app())

    @patch("gobstuf.app.GOB_STUF_PORT", 1234)
    @patch("gobstuf.app.get_app")
    def test_run(self, mock_get_app):
        mock_app = MagicMock()
        mock_get_app.return_value = mock_app
        run()
        mock_app.run.assert_called_with(port=1234)
