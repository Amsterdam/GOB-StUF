from unittest import TestCase
from unittest.mock import patch

from requests.exceptions import HTTPError, ConnectionError

from gobstuf.reference_data.code_resolver import CodeResolver, CodeNotFoundException


class TestCodeResolver(TestCase):

    def test_initialize(self):
        # Assert that landen table has been initialised
        self.assertTrue(CodeResolver._landen)

    @patch("builtins.open")
    def test_load_landen(self, mock_open):
        mock_open.side_effect = FileNotFoundError
        with self.assertRaises(CodeNotFoundException):
            CodeResolver._load_data(CodeResolver.LANDEN)
        with self.assertRaises(CodeNotFoundException):
            CodeResolver._load_data(CodeResolver.GEMEENTEN)

    def test_get_land(self):
        for method_name in ['get_land', 'get_gemeente']:
            method = getattr(CodeResolver, method_name)

            result = method("")
            self.assertIsNone(result)

            result = method(None)
            self.assertIsNone(result)

            result = method("any code")
            self.assertIsNone(result)

        CodeResolver._landen['any code'] = {'omschrijving': 'any land'}
        result = CodeResolver.get_land("any code")
        self.assertEqual(result, 'any land')

        # Pad codes to 4 characters
        CodeResolver._landen['0002'] = {'omschrijving': 'any land'}
        for code in ['2', '02', '002']:
            CodeResolver.get_land(code)
            self.assertIsNone(CodeResolver._landen.get(code))
