from abc import ABC, abstractmethod
from flask import request
from typing import List, Optional
from xml.etree.ElementTree import Element

from gobstuf.stuf.message import StufMessage
from gobstuf.stuf.exception import NoStufAnswerException
from gobstuf.stuf.brp.response_mapping import StufObjectMapping, Mapping, RelatedMapping


class StufResponse(ABC):
    """Base class. Wraps a StUF response.
    """

    # Predefined namespaces
    namespaces = {
        'soapenv': 'http://schemas.xmlsoap.org/soap/envelope/',
        'BG': 'http://www.egem.nl/StUF/sector/bg/0310',
        'StUF': 'http://www.egem.nl/StUF/StUF0301',
        'xsi': 'http://www.w3.org/2001/XMLSchema-instance',
    }

    def __init__(self, msg: str, **kwargs):
        """

        :param msg: The string representation of the XML StUF message
        """
        self.stuf_message = None

        # Set kwargs as properties. For example inclusiefoverledenpersonen on the IngeschrevenpersonenStufResponse
        # class
        for k, v in kwargs.items():
            self.__setattr__(k, v)

        self.load(msg)

    def load(self, msg: str):
        self.stuf_message = StufMessage(msg, self.namespaces)

    def to_string(self):
        return self.stuf_message.pretty_print()


class MappedObjectWrapper:
    """
    Wraps the dict representation of a mapped object along with the used mapping class and the root element.

    If requesting the dict representation, use get_filtered_object instead of accessing the mapped_object property
    directly
    """

    def __init__(self, mapped_object: dict, mapping_class: Mapping, element: Element):
        self.mapped_object = mapped_object
        self.mapping_class = mapping_class
        self.element = element

    def get_filtered_object(self, **kwargs):
        # Important that get_links is called before filter, as get_links may need data that is filtered out
        # (This case is handled in the tests)
        links = self.mapping_class.get_links(self.mapped_object)

        filtered = self.mapping_class.filter(self.mapped_object, **kwargs)
        if filtered is not None:
            filtered['_links'] = links
        return filtered


class StufMappedResponse(StufResponse):
    """StufResponse with mapping for further use; maps paths to keys (as used in
    the REST API for example)

    """

    # Class properties to pass to the mapped object filter
    filter_kwargs = []

    response_type = None

    def __init__(self, msg: str, **kwargs):
        if 'expand' in kwargs:
            self.expand = kwargs['expand'].split(',') if kwargs['expand'] else []
            del kwargs['expand']
        else:
            self.expand = []

        # If the response type is one of Related detail or list, we need to expand the specific relation
        if isinstance(self.response_type, (RelatedDetailResponse, RelatedListResponse)):
            expand_parameter = self.response_type.related_type
            self.expand.append(expand_parameter) if expand_parameter not in self.expand else self.expand

        super().__init__(msg, **kwargs)

    def get_object_elm(self):
        """Returns the object wrapper element from the response message.

        :return:
        """
        answer_object = self.stuf_message.find_elm(self.answer_section)

        if not answer_object:
            raise NoStufAnswerException()

        return self.stuf_message.find_elm(self.object_elm, answer_object)

    def get_all_object_elms(self):
        """Returns all objects from the response message.

        Works like get_object_elm, but does not raise an Exception when there are no results.

        :return:
        """
        return self.stuf_message.find_all_elms(self.answer_section + ' ' + self.object_elm)

    def get_links(self, data):
        """
        Return the HAL links that correspond with the (self) mapped object

        Default implementation is to return no links

        :param data: the mapped and filtered object
        :return:
        """
        return {}

    def _get_filter_kwargs(self):
        """Get the kwargs to pass to the filter method for filtering objects

        :return:
        """
        return {prop: getattr(self, prop, None) for prop in self.filter_kwargs}

    def _add_embedded_objects(self, mapped_object: MappedObjectWrapper):
        """Adds the _embedded objects to :mapped_object:

        :param mapped_object:
        :return:
        """
        mapping = mapped_object.mapping_class
        embedded = {}
        for related_attr, root_obj in mapping.related.items():
            if related_attr not in self.expand:
                continue

            embedded[related_attr] = self.create_objects_from_elements(
                self.stuf_message.find_all_elms(root_obj, mapped_object.element)
            )

        mapped_object.mapped_object['_embedded'] = embedded

    def get_answer_object(self):
        """
        The answer object is created from the StUF response

        The response is mapped on the response object
        and then filtered

        If multiple answer objects are present, only the first item is returned.

        :return: the object to be returned as answer to the REST call
        :raises: NoStufAnswerException if the object is empty
        """
        object = self.get_object_elm()
        answer_object = self.create_object_from_element(object)

        # Filter the response if a response type is defined
        if self.response_type:
            answer_object = self.response_type.filter_response(self, answer_object)

        if not answer_object:
            raise NoStufAnswerException()

        return answer_object

    def create_object_from_element(self, element: Element) -> Optional[dict]:
        """Creates the dictionary representation of :element: based on its StUF:entiteittype attribute.

        :param element:
        :return:
        """
        mapped_object = self.get_mapped_object(element)
        if not mapped_object:
            return None
        self._add_embedded_objects(mapped_object)
        return mapped_object.get_filtered_object(**self._get_filter_kwargs())

    def create_objects_from_elements(self, object_elements: list) -> List[dict]:
        """Create a list of objects from a list of XMLtree elements

        :param object_elements:
        :return:
        """
        result = []
        for obj in object_elements:
            elm = self.create_object_from_element(obj)

            if elm:
                result.append(elm)
        return result

    def get_all_answer_objects(self):
        """
        Returns all objects from the StUF response. Works like get_answer_object, but does not raise an Exception when
        the response is empty.

        :return:
        """
        return self.create_objects_from_elements(self.get_all_object_elms())

    def _get_mapping(self, element: Element) -> Mapping:
        """Finds the mapping for the given XML Element, based on the value of StUF:entiteittype

        :param element:
        :return:
        """
        stuf_entity_type = element.attrib.get('{%s}entiteittype' % self.namespaces['StUF'])
        return StufObjectMapping.get_for_entity_type(stuf_entity_type)

    def _get_mapped_related_object(self, mapping: RelatedMapping, wrapper_element: Element):
        """Returns the mapping for the inner entity of RelatedMapping

        For example, NPSNPSHUW contains an inner NPS entity.
        wrapper_element is the NPSNPSHUW element, we return the mapped inner NPS object

        :param mapping:
        :param wrapper_element:
        :return:
        """
        related_obj = self.stuf_message.find_elm(mapping.related_entity_wrapper, wrapper_element)

        return self.get_mapped_object(related_obj).get_filtered_object(**{
            **self._get_filter_kwargs(),
            **mapping.override_related_filters
        }) if related_obj else None

    def get_mapped_object(self, obj, mapping=None):  # noqa: C901
        """
        Returns a dict with key -> value pairs for the keys in mapping with the value extracted
        from the response message.

        The mapping is a (possibly nested) dictionary. If no mapping is provided, the mapping will be inferred from
        the StUF:entiteittype attribute on the object.

        Each key is mapped upon the specified element value

        Optionally a tuple can be specified (method, element value).
        The element value is the passed as an argument to the given method

        Nested mappings are resolved by recursive calls to this method

        :return:
        """
        # If mapping is None, get from obj
        mapping = mapping or self._get_mapping(obj)

        if isinstance(mapping, Mapping):
            dict_mapping = {}

            if isinstance(mapping, RelatedMapping):
                """RelatedMapping.

                First get the mapping of the related_object it contains. For example, for a NPSNPSHUW mapping the
                related object would be an NPS entity.
                """
                # Get inner entity
                dict_mapping = self._get_mapped_related_object(mapping, obj)

                if dict_mapping is None:
                    # Object is filtered out. Return None
                    return None

            # Initial call. Return mapped dictionary and Mapping class
            dict_mapping.update(self.get_mapped_object(obj, mapping.mapping))
            return MappedObjectWrapper(dict_mapping, mapping, obj)
        elif isinstance(mapping, dict):
            # the values are resolved at a nested level by recursively calling this method
            # Example: 'naam': {'voornamen': '<attribute>', 'geslachtsnaam': '<attribute>'}
            return {k: self.get_mapped_object(obj, v) for k, v in mapping.items()}
        elif isinstance(mapping, tuple):
            # The value is resolved by a function call with the attribute value(s) as parameter(s)
            # Example: 'naamlengte': (len, '<attribute>')
            # will result in 'naamlengte': len(<attribute value>)
            method, *mappings = mapping
            attributes = [self.get_mapped_object(obj, v) for v in mappings]
            return method(*attributes)
        elif isinstance(mapping, list):
            # Iterate over a list of items
            # The main key is the first element in the list
            # The mapping to be resolved for every instance of this key is the second element
            elms = self.stuf_message.find_all_elms(mapping[0], obj)
            subobj = mapping[1]
            return [self.get_mapped_object(elm, subobj) for elm in elms]
        elif mapping and mapping[0] == '=':
            # Literal value, eg: =value results in value
            return mapping[1:]
        elif mapping and '!' in mapping:
            # XPath value, eg !.//<element>...
            mapping, path = mapping.split('!')
            return self.stuf_message.get_elm_value_by_path(mapping, path, obj)
        elif mapping and '@' in mapping:
            # Element attribute value, eg: element@attribute
            mapping, attr = mapping.split('@')
            return self.stuf_message.get_elm_attr(mapping, attr, obj)
        else:
            # Plain element value
            return self.stuf_message.get_elm_value(mapping, obj)

    @property
    @abstractmethod
    def answer_section(self):
        """The root element of the answer in the StUF message.

        :return:
        """
        pass  # pragma: no cover

    @property
    @abstractmethod
    def object_elm(self):
        """The root element of the answer object, relative to the answer_secion

        :return:
        """
        pass  # pragma: no cover


class RelatedDetailResponse:

    def __init__(self, related_type: str):
        self.related_type = related_type

    def filter_response(self, response: StufMappedResponse, response_object: dict):
        """Filter the response object to only return the requested relation from _embedded

        For example a RelatedDetailResponse for partners with id 1:
        {'_embedded': {
            'partners': [{'id': 1}, {'id': 2}, {'id': 3}],
            'kinderen': [],
        }}

        Will return

        {'id': 1}

        The correct link to self is added to make it a valid HAL response.

        :param response: The StufMappedResponse
        :param response_obj: The mapped and filtered response object
        :return: A filtered responsed object
        """
        # Get the requested relation id passed from the URL, e.g. partner_id = 1
        related_id = int(getattr(response, f'{self.related_type}_id'))
        try:
            response_object = response_object['_embedded'][self.related_type][related_id-1]
        except (KeyError, IndexError):
            return
        # Add the link to self in the new response object
        response_object['_links'] = {
            **response_object.get('_links', {}),
            'self': {
                'href': request.base_url
            }
        }

        return response_object


class RelatedListResponse(RelatedDetailResponse):

    def filter_response(self, response: StufMappedResponse, response_object: dict):
        """Filter the response object to only return the requested relations from _embedded

        For example a RelatedListResponse for partners:
        {'_embedded': {
            'partners': [],
            'kinderen': [],
        }}

        Will return

        {'_embedded': {
            'partners': [],
        }}

        The correct link to self is added to make it a valid HAL response

        :param response: The StufMappedResponse
        :param response_obj: The mapped and filtered response object
        :return: A filtered responsed object
        """
        relations = response_object.get('_embedded', {}).get(self.related_type, [])
        response_object = {
            '_embedded': {
                self.related_type: relations
            }
        }

        # Add the link to self in the new response object
        response_object['_links'] = {
            'self': {
                'href': request.base_url
            }
        }
        return response_object
