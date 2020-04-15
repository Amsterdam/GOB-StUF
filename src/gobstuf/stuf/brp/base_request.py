import os
import pytz
import datetime

from abc import ABC, abstractmethod

from gobstuf.stuf.message import StufMessage

TEMPLATE_DIR = os.path.join(os.path.dirname(__file__), 'request_template')


class StufRequest(ABC):
    """Creates a new StUF request, based on a template from an *.xml file.

    Replaces gebruiker and applicatie in the XML file, as well as the key/values defined in values.

    """
    default_tz = 'Europe/Amsterdam'

    # Paths within the template
    applicatie_path = 'BG:stuurgegevens StUF:zender StUF:applicatie'
    gebruiker_path = 'BG:stuurgegevens StUF:zender StUF:gebruiker'
    tijdstip_bericht_path = 'BG:stuurgegevens StUF:tijdstipBericht'
    referentienummer_path = 'BG:stuurgegevens StUF:referentienummer'

    def __init__(self, gebruiker: str, applicatie: str, values: dict):
        """

        :param gebruiker: MKS gebruiker
        :param applicatie: MKS applicatie
        :param values: dict with key/values. Key paths are defined in replace_paths
        """
        self.gebruiker = gebruiker
        self.applicatie = applicatie
        self.stuf_message = None

        self._load()

        self._set_applicatie(applicatie)
        self._set_gebruiker(gebruiker)
        self._set_values(values)

    def _set_applicatie(self, applicatie: str):
        self.set_element(self.applicatie_path, applicatie)

    def _set_gebruiker(self, gebruiker: str):
        self.set_element(self.gebruiker_path, gebruiker)

    def _set_values(self, values: dict):
        """Sets values in XML. Accepts a dict with {key: value} pairs, where key exists in
        replace_paths and value is the new value of the matching path.

        :param values:
        :return:
        """
        assert values.keys() == self.replace_paths.keys()  # Should never fail

        for key, value in values.items():
            self.set_element(self.replace_paths[key], value)

    def _load(self):
        """Loads xml template file.

        :return:
        """
        with open(self._template_path(), 'r') as f:
            self.stuf_message = StufMessage(f.read())

    def _template_path(self):
        """Returns absolute path to the template file

        :return:
        """
        return os.path.join(TEMPLATE_DIR, self.template)

    def time_str(self, dt: datetime.datetime):
        """Returns formatted time string

        :param dt:
        :return:
        """
        # %f returns microseconds. We want milliseconds precision, so cut off at 17 characters:
        # yyyy mm dd hh mm ss mmm = 4 + 2 + 2 + 2 + 2 + 2 + 3 = 17 characters
        return dt.strftime('%Y%m%d%H%M%S%f')[:17]

    def ref_str(self, dt: datetime.datetime):
        """Returns the reference for this message based on dt

        :param dt:
        :return:
        """
        return f"GOB{dt.strftime('%Y%m%d%H%M%S%f')}"

    def set_element(self, path: str, value: str):
        full_path = self.content_root_elm + " " + path
        self.stuf_message.set_elm_value(full_path, value)

    def to_string(self):
        """String (XML) representation of this request. Sets tijdstip_bericht and referentienummer to
        current datetime value.

        :return:
        """
        now = datetime.datetime.utcnow().astimezone(tz=pytz.timezone(self.default_tz))
        self.set_element(self.tijdstip_bericht_path, self.time_str(now))
        self.set_element(self.referentienummer_path, self.ref_str(now))

        return self.stuf_message.to_string()

    def __str__(self):
        return self.to_string()

    @property
    @abstractmethod
    def template(self) -> str:
        """The XML file in the TEMPLATE_DIR that serves as basis for this request.

        :return:
        """
        pass  # pragma: no cover

    @property
    @abstractmethod
    def content_root_elm(self) -> str:
        """Defines the root of the content in the XML file (serves as basis for other paths)

        :return:
        """
        pass  # pragma: no cover

    @property
    @abstractmethod
    def replace_paths(self) -> dict:
        """key -> path pairs, for example:

        {'bsn': 'BG:gelijk BG:inp.bsn'}

        :return:
        """
        pass  # pragma: no cover

    @property
    @abstractmethod
    def soap_action(self) -> str:
        """SOAP action to pass in the header

        :return:
        """
        pass  # pragma: no cover