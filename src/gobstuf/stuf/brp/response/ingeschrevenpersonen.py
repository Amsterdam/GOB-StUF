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
    answer_type = "La01"
    answer_section = f'soapenv:Envelope soapenv:Body BG:nps{answer_type} BG:antwoord'
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


class IngeschrevenpersonenStufHistorieResponse(StufMappedResponse):
    answer_type = "La07"
    answer_section = f"soapenv:Envelope soapenv:Body BG:nps{answer_type} BG:antwoord"
    object_elm = "BG:object"

    response_filters = [VerblijfplaatsHistorieFilter]

    def get_answer_object(self):
        """Return a list of verblijfplaatsen from single response object."""
        answer = super().get_answer_object()
        return [vbl for vbl in [answer.get("verblijfplaats"), *answer.get("historieMaterieel", [])] if vbl]
