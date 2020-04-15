import datetime

from unittest import TestCase
from unittest.mock import patch, MagicMock, call

from gobstuf.stuf.brp.base_request import StufRequest


class StufRequestImpl(StufRequest):
    template = 'template.xml'
    content_root_elm = 'A B C'
    replace_paths = {
        'attr1': 'PATH TO ATTR1',
        'attr2': 'PATH TO ATTR2',
    }
    soap_action = 'SOAP ACTION'


@patch("gobstuf.stuf.brp.base_request.TEMPLATE_DIR", "/template/dir")
class StufRequestTestInit(TestCase):
    """ Tests initialisation of StufRequest """

    @patch("builtins.open")
    @patch("gobstuf.stuf.brp.base_request.StufMessage")
    @patch("gobstuf.stuf.brp.base_request.StufRequest.set_element")
    def test_init(self, mock_set_element, mock_message, mock_open):
        values = {
            'attr1': 'value1',
            'attr2': 'value2',
        }

        req = StufRequestImpl('USERNAME', 'APPLICATION_NAME', values)

        mock_set_element.assert_has_calls([
            call(req.applicatie_path, 'APPLICATION_NAME'),
            call(req.gebruiker_path, 'USERNAME'),
            call('PATH TO ATTR1', 'value1'),
            call('PATH TO ATTR2', 'value2'),
        ])

        self.assertEqual(mock_message.return_value, req.stuf_message)
        mock_message.assert_called_with(mock_open().__enter__().read())
        mock_open.assert_any_call('/template/dir/template.xml', 'r')


@patch("gobstuf.stuf.brp.base_request.TEMPLATE_DIR", "/template/dir")
@patch("gobstuf.stuf.brp.base_request.StufRequest._load", MagicMock())
@patch("gobstuf.stuf.brp.base_request.StufRequest._set_applicatie", MagicMock())
@patch("gobstuf.stuf.brp.base_request.StufRequest._set_gebruiker", MagicMock())
@patch("gobstuf.stuf.brp.base_request.StufRequest._set_values", MagicMock())
class StufRequestTest(TestCase):
    """ All initialisation methods are mocked; initialisation is tested in StufRequestTestInit """

    def test_time_str(self):
        dt = datetime.datetime.utcnow().replace(2020, 4, 9, 12, 59, 59, 88402, tzinfo=None)
        req = StufRequestImpl('', '', {})

        self.assertEqual('20200409125959088', req.time_str(dt))

    def test_ref_str(self):
        dt = datetime.datetime.utcnow().replace(2020, 4, 9, 12, 59, 59, 88402, tzinfo=None)

        req = StufRequestImpl('', '', {})
        self.assertEqual('GOB20200409125959088402', req.ref_str(dt))

    def test_set_element(self):
        req = StufRequestImpl('', '', {})
        req.stuf_message = MagicMock()

        req.set_element('THE PATH', 'the value')
        req.stuf_message.set_elm_value.assert_called_with('A B C THE PATH', 'the value')

    @patch("gobstuf.stuf.brp.base_request.datetime")
    def test_to_string(self, mock_datetime):
        req = StufRequestImpl('', '', {})
        req.stuf_message = MagicMock()
        req.set_element = MagicMock()
        req.time_str = MagicMock()
        req.ref_str = MagicMock()

        self.assertEqual(req.stuf_message.to_string(), req.to_string())

        req.set_element.assert_has_calls([
            call(req.tijdstip_bericht_path, req.time_str()),
            call(req.referentienummer_path, req.ref_str()),
        ])

    def test_str(self):
        req = StufRequestImpl('', '', {})
        req.to_string = MagicMock(return_value='sttrrrrring')

        self.assertEqual(req.to_string(), str(req))
