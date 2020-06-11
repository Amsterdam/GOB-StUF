import re

from abc import ABC

from gobstuf.reference_data.code_resolver import CodeResolver
from gobstuf.rest.brp.argument_checks import ArgumentCheck
from gobstuf.stuf.brp.base_request import StufRequest

# Defined at the module level so it's only compiled once
date_match = re.compile(r'^\d{4}-\d{2}-\d{2}$')


class IngeschrevenpersonenStufRequest(StufRequest, ABC):
    BSN_LENGTH = 9

    bsn_check = [ArgumentCheck.has_min_length(BSN_LENGTH), ArgumentCheck.has_max_length(BSN_LENGTH)]

    template = 'ingeschrevenpersonen.xml'
    content_root_elm = 'soapenv:Body BG:npsLv01'
    soap_action = 'http://www.egem.nl/StUF/sector/bg/0310/npsLv01Integraal'


class IngeschrevenpersonenFilterStufRequest(IngeschrevenpersonenStufRequest):
    parameter_paths = {
        'burgerservicenummer': 'BG:gelijk BG:inp.bsn',
        'verblijfplaats__postcode': 'BG:gelijk BG:verblijfsadres BG:aoa.postcode',
        'verblijfplaats__huisnummer': 'BG:gelijk BG:verblijfsadres BG:aoa.huisnummer',
        'verblijfplaats__naamopenbareruimte': 'BG:gelijk BG:verblijfsadres BG:gor.openbareRuimteNaam',
        'verblijfplaats__gemeentevaninschrijving': 'BG:gelijk BG:gem.gemeenteCode',
        'geboorte__datum': 'BG:gelijk BG:geboortedatum',
        'naam__geslachtsnaam': 'BG:gelijk BG:geslachtsnaam',
    }

    parameter_checks = {
        'inclusiefoverledenpersonen': ArgumentCheck.is_boolean,
        'verblijfplaats__postcode': ArgumentCheck.is_postcode,
        'verblijfplaats__huisnummer': [ArgumentCheck.is_integer, ArgumentCheck.is_positive_integer],
        'verblijfplaats__gemeentevaninschrijving': [ArgumentCheck.is_valid_gemeente],
        'geboorte__datum': [ArgumentCheck.is_valid_date_format, ArgumentCheck.is_valid_date],
        'naam__geslachtsnaam': [ArgumentCheck.has_max_length(200)],
        'burgerservicenummer': IngeschrevenpersonenStufRequest.bsn_check
    }

    def convert_param_geboorte__datum(self, value: str):
        """Transforms the YYYY-MM-DD value to YYYYMMDD

        :param value:
        :return:
        """
        assert date_match.match(value), "This value should already be validated here"

        return value.replace('-', '')

    def convert_param_verblijfplaats__gemeentevaninschrijving(self, value: str):
        """Transforms the supplied gemeente value to a valid gemeentecode

        :param value:
        :return:
        """
        return CodeResolver.get_gemeente_code(value).lstrip('0')


class IngeschrevenpersonenBsnStufRequest(IngeschrevenpersonenStufRequest):
    BSN_LENGTH = 9

    parameter_paths = {
        'bsn': 'BG:gelijk BG:inp.bsn'
    }

    parameter_checks = {
        'bsn': IngeschrevenpersonenStufRequest.bsn_check,
        'inclusiefoverledenpersonen': ArgumentCheck.is_boolean,
    }


class IngeschrevenpersonenBsnPartnerStufRequest(IngeschrevenpersonenStufRequest):
    BSN_LENGTH = 9

    parameters = ['partners_id']

    parameter_paths = {
        'bsn': 'BG:gelijk BG:inp.bsn',
    }

    parameter_checks = {
        'bsn': IngeschrevenpersonenStufRequest.bsn_check,
        'inclusiefoverledenpersonen': ArgumentCheck.is_boolean,
    }
