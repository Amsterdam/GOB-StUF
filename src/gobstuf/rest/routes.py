from gobstuf.rest.brp.views import (
    IngeschrevenpersonenBsnView,
    IngeschrevenpersonenBsnPartnerDetailView,
    IngeschrevenpersonenBsnPartnerListView,
    IngeschrevenpersonenFilterView,
    IngeschrevenpersonenBsnOudersDetailView,
    IngeschrevenpersonenBsnOudersListView,
    IngeschrevenpersonenBsnKinderenDetailView,
    IngeschrevenpersonenBsnKinderenListView
)

REST_ROUTES = [
    ('/brp/ingeschrevenpersonen', IngeschrevenpersonenFilterView.as_view('brp_ingeschrevenpersonen_list')),
    ('/brp/ingeschrevenpersonen/<bsn>', IngeschrevenpersonenBsnView.as_view('brp_ingeschrevenpersonen_bsn')),
    ('/brp/ingeschrevenpersonen/<bsn>/partners',
     IngeschrevenpersonenBsnPartnerListView.as_view('brp_ingeschrevenpersonen_bsn_partners_list')),
    ('/brp/ingeschrevenpersonen/<bsn>/partners/<partners_id>',
     IngeschrevenpersonenBsnPartnerDetailView.as_view('brp_ingeschrevenpersonen_bsn_partners_detail')),
    ('/brp/ingeschrevenpersonen/<bsn>/ouders',
     IngeschrevenpersonenBsnOudersListView.as_view('brp_ingeschrevenpersonen_bsn_ouders_list')),
    ('/brp/ingeschrevenpersonen/<bsn>/ouders/<ouders_id>',
     IngeschrevenpersonenBsnOudersDetailView.as_view('brp_ingeschrevenpersonen_bsn_ouders_detail')),
    ('/brp/ingeschrevenpersonen/<bsn>/kinderen',
     IngeschrevenpersonenBsnKinderenListView.as_view('brp_ingeschrevenpersonen_bsn_kinderen_list')),
    ('/brp/ingeschrevenpersonen/<bsn>/kinderen/<kinderen_id>',
     IngeschrevenpersonenBsnKinderenDetailView.as_view('brp_ingeschrevenpersonen_bsn_kinderen_detail')),
]
