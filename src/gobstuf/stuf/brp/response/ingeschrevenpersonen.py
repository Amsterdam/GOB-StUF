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
    answer_code = "npsLa01"
    answer_section = f"soapenv:Envelope soapenv:Body BG:{answer_code} BG:antwoord"
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
    answer_code = "npsLa07"
    answer_section = f"soapenv:Envelope soapenv:Body BG:{answer_code} BG:antwoord"
    object_elm = "BG:object"

    response_filters = [VerblijfplaatsHistorieFilter]

    def get_all_answer_objects(self) -> list[dict]:
        """
        Returns verblijfsplaatshistorie objects as a list of dictionaries.

        Because we are actually mapping 1 NPS and returning multiple Verblijfplaats,
        we need to fetch the first object here.
        Otherwise the return value will be list[list[dict, ...]]
        """
        answer_objects = super().get_all_answer_objects()
        return answer_objects[0] if answer_objects else answer_objects
