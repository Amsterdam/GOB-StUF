from gobstuf.stuf.brp.base_response import StufMappedResponse, VerblijfplaatsHistorieFilter
from gobstuf.stuf.brp.response.filters import (
    PartnersDetailResponseFilter,
    PartnersListResponseFilter,
    OudersDetailResponseFilter,
    OudersListResponseFilter,
    KinderenDetailResponseFilter,
    KinderenListResponseFilter
)


class IngeschrevenpersonenStufResponse(StufMappedResponse):
    answer_section = 'soapenv:Envelope soapenv:Body BG:npsLa01 BG:antwoord'
    object_elm = 'BG:object'

    # These properties are passed to the filter method of the mapped object
    filter_kwargs = ['inclusiefoverledenpersonen']


class IngeschrevenpersonenStufPartnersDetailResponse(IngeschrevenpersonenStufResponse):
    response_filters = [PartnersDetailResponseFilter]


class IngeschrevenpersonenStufPartnersListResponse(IngeschrevenpersonenStufResponse):
    response_filters = [PartnersListResponseFilter]


class IngeschrevenpersonenStufOudersDetailResponse(IngeschrevenpersonenStufResponse):
    response_filters = [OudersDetailResponseFilter]


class IngeschrevenpersonenStufOudersListResponse(IngeschrevenpersonenStufResponse):
    response_filters = [OudersListResponseFilter]


class IngeschrevenpersonenStufKinderenDetailResponse(IngeschrevenpersonenStufResponse):
    response_filters = [KinderenDetailResponseFilter]


class IngeschrevenpersonenStufKinderenListResponse(IngeschrevenpersonenStufResponse):
    response_filters = [KinderenListResponseFilter]


class IngeschrevenpersonenStufHistorieResponse(IngeschrevenpersonenStufResponse):
    answer_section = 'soapenv:Envelope soapenv:Body BG:npsLa07 BG:antwoord'

    response_filters = [VerblijfplaatsHistorieFilter]

    def get_all_answer_objects(self) -> list[dict]:
        """
        Returns verblijfsplaatshistorie objects as a list of dictionaries.

        Because we are actually mapping 1 NPS and returning multiple Verblijfplaats, we need to fetch the first object here.
        Otherwise the return value will be list[list[dict, ...]]
        """
        return super().get_all_answer_objects()[0]
