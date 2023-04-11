from __future__ import annotations

import datetime
from collections import defaultdict

from typing import Type, Optional, Union
from abc import ABC, abstractmethod

from gobstuf.auth.routes import get_auth_url
from gobstuf.config import BAG_NAG_ENDPOINT, BAG_VBO_ENDPOINT, BAG_LPS_ENDPOINT, BAG_SPS_ENDPOINT
from gobstuf.indications import Geslachtsaanduiding
from gobstuf.mks_utils import MKSConverter
from gobstuf.lib.utils import get_value


class Mapping(ABC):
    """Defines a mapping between a dict (used for REST responses) and a StUF message.

    Provides a filter method to filter out attributes and/or objects
    """

    @property
    def related(self) -> dict:
        return {}

    @property
    @abstractmethod
    def mapping(self) -> dict:  # pragma: no cover
        pass

    @property
    @abstractmethod
    def answer_code(self) -> str:  # pragma: no cover
        pass

    @property
    @abstractmethod
    def entity_type(self) -> str:  # pragma: no cover
        pass

    def get_links(self, mapped_object) -> dict:
        return {}

    def filter(self, mapped_object: dict, **kwargs):  # noqa: C901
        """
        Filter the mapped object on the mapped attribute values
        Default implementation is to filter out any null values

        Any derived class that implements this method should call this super method on its result
        super().filter(result)

        :param mapped_object:
        :return:
        """

        def filter_none_values(obj):
            """
            Recursively filter out any None values of the given object

            :param obj:
            :return:
            """
            result = {}
            for k, v in obj.items():
                if isinstance(v, dict):
                    value = filter_none_values(v)
                    if value:
                        result[k] = value
                elif isinstance(v, list):
                    result[k] = [item for item in [filter_none_values(obj) for obj in v] if item]
                elif v is not None:
                    result[k] = v
            return result

        return filter_none_values(mapped_object) if mapped_object else mapped_object


class StufObjectMapping:
    """Class holding all Mapping objects. Call register() with each Mapping to make the mapping available."""
    mappings = defaultdict(dict)

    @classmethod
    def get_for_entity_type(cls, answer_code: str, entity_type: str) -> Mapping:
        try:
            return cls.mappings[answer_code][entity_type]()
        except KeyError:
            raise Exception(f"Can't find mapping for answer/entity type combination: {answer_code} / {entity_type}")

    @classmethod
    def register(cls, mapping: Type[Mapping]):
        map_obj = mapping()
        cls.mappings[map_obj.answer_code] |= {map_obj.entity_type: mapping}


class NPSMapping(Mapping):
    """NPS mapping, for Natuurlijke Personen."""

    DUMMY = (lambda dummy: None, "BG:dummy")

    @property
    def answer_code(self):
        return "npsLa01"

    @property
    def entity_type(self):
        return 'NPS'

    @property
    def mapping_verblijfplaats(self):
        return {
            'adresseerbaarObjectIdentificatie': 'BG:inp.verblijftIn BG:gerelateerde BG:identificatie',
            'woonadres': {
                'naamOpenbareRuimte': 'BG:verblijfsadres BG:gor.openbareRuimteNaam',
                'straat': 'BG:verblijfsadres BG:gor.straatnaam',
                'huisnummer': 'BG:verblijfsadres BG:aoa.huisnummer',
                'huisletter': 'BG:verblijfsadres BG:aoa.huisletter',
                'huisnummertoevoeging': 'BG:verblijfsadres BG:aoa.huisnummertoevoeging',
                'postcode': 'BG:verblijfsadres BG:aoa.postcode',
                'woonplaats': 'BG:verblijfsadres BG:wpl.woonplaatsNaam',
                'nummeraanduidingIdentificatie': 'BG:verblijfsadres BG:aoa.identificatie',
                'locatiebeschrijving': 'BG:verblijfsadres BG:inp.locatiebeschrijving'
            },
            'briefadres': {
                'naamOpenbareRuimte': 'BG:sub.correspondentieAdres BG:gor.openbareRuimteNaam',
                'straat': 'BG:sub.correspondentieAdres BG:gor.straatnaam',
                'huisnummer': 'BG:sub.correspondentieAdres BG:aoa.huisnummer',
                'huisletter': 'BG:sub.correspondentieAdres BG:aoa.huisletter',
                'huisnummertoevoeging': 'BG:sub.correspondentieAdres BG:aoa.huisnummertoevoeging',
                'postcode': 'BG:sub.correspondentieAdres BG:postcode',
                'woonplaats': 'BG:sub.correspondentieAdres BG:wpl.woonplaatsNaam',
                'nummeraanduidingIdentificatie': 'BG:sub.correspondentieAdres BG:aoa.identificatie',
                'locatiebeschrijving': 'BG:sub.correspondentieAdres BG:inp.locatiebeschrijving'
            },
            'indicatieVestigingVanuitBuitenland':
                (MKSConverter.true_if_exists, 'BG:inp.datumVestigingInNederland'),
            'vanuitVertrokkenOnbekendWaarheen':
                (MKSConverter.true_if_equals('0000'), (MKSConverter.as_code(4), 'BG:inp.immigratieLand')),
            'datumAanvangAdreshouding':
                (MKSConverter.get_first_date_from_various,
                 'BG:verblijfsadres BG:begindatumVerblijf',
                 'BG:inp.verblijftIn StUF:tijdvakRelatie StUF:beginRelatie'
                 ),
            # only available for verblijfplaatshistorie, dummy to maintain ordering
            'datumIngangGeldigheid': self.DUMMY,
            'datumTot': self.DUMMY,

            'datumInschrijvingInGemeente': (MKSConverter.as_datum_broken_down, 'BG:inp.datumInschrijving'),
            'datumVestigingInNederland':
                (MKSConverter.as_datum_broken_down, 'BG:inp.datumVestigingInNederland',
                 'BG:inp.datumVestigingInNederland@StUF:indOnvolledigeDatum'),
            'gemeenteVanInschrijving': {
                'code': (MKSConverter.as_gemeente_code, 'BG:inp.gemeenteVanInschrijving'),
                'omschrijving': (MKSConverter.get_gemeente_omschrijving, 'BG:inp.gemeenteVanInschrijving')
            },
            'landVanwaarIngeschreven': {
                'code': (MKSConverter.as_code(4), 'BG:inp.immigratieLand'),
                'omschrijving': (MKSConverter.get_land_omschrijving, 'BG:inp.immigratieLand')
            },
            'verblijfBuitenland': (MKSConverter.get_verblijf_buitenland, {
                'adresRegel1': 'BG:sub.verblijfBuitenland BG:sub.adresBuitenland1',
                'adresRegel2': 'BG:sub.verblijfBuitenland BG:sub.adresBuitenland2',
                'adresRegel3': 'BG:sub.verblijfBuitenland BG:sub.adresBuitenland3',
                'land': {
                    'code':
                        (MKSConverter.as_code(4), 'BG:sub.verblijfBuitenland BG:lnd.landcode'),
                    # Find omschrijving from codetabel like we do with geboorteland, although MKS does return the
                    # 'landnaam' in this case (as opposed to geboorteland for example). Just for consistency sake
                    'omschrijving':
                        (MKSConverter.get_land_omschrijving, 'BG:sub.verblijfBuitenland BG:lnd.landcode'),
                },
            }),
            # BG:inOnderzoek returns multiple nodes.
            # Returns the value for the node with groepsnaam attribute 'Verblijfplaats', otherwise None
            "inOnderzoek": (NPSMapping.in_onderzoek, ["BG:inOnderzoek", ".!.[@groepsnaam='Verblijfsplaats']"]),
        }

    @property
    def mapping(self):
        communicatie_parameters = {
            'persoon': {
                'geslachtsaanduiding': (MKSConverter.as_geslachtsaanduiding,
                                        'BG:geslachtsaanduiding',
                                        'BG:geslachtsaanduiding@StUF:noValue'),
                'naam': {
                    'aanduidingNaamgebruik': (MKSConverter.as_aanduiding_naamgebruik, 'BG:aanduidingNaamgebruik'),
                    'voorletters': 'BG:voorletters',
                    'geslachtsnaam': 'BG:geslachtsnaam',
                    'voorvoegsel': 'BG:voorvoegselGeslachtsnaam',
                }
            },
            'partners': ['BG:inp.heeftAlsEchtgenootPartner', {
                'naam': {
                    'geslachtsnaam': 'BG:gerelateerde BG:geslachtsnaam',
                    'voorvoegsel': 'BG:gerelateerde BG:voorvoegselGeslachtsnaam',
                },
                'aangaanHuwelijkPartnerschap': {
                    'datum': (MKSConverter.as_datum_broken_down, 'BG:datumSluiting')
                },
                'ontbindingHuwelijkPartnerschap': {
                    'datum': (MKSConverter.as_datum_broken_down, 'BG:datumOntbinding')
                }
            }]
        }

        nationaliteit_parameters = {
            'aanduidingBijzonderNederlanderschap': (MKSConverter.as_aanduiding_bijzonder_nederlanderschap,
                                                    'BG:inp.aanduidingBijzonderNederlanderschap'),
            'nationaliteiten': ['BG:inp.heeftAlsNationaliteit', {
                'datumIngangGeldigheid': (MKSConverter.as_datum_broken_down,
                                          'BG:inp.datumVerkrijging',
                                          'BG:inp.datumVerkrijging@StUF:indOnvolledigeDatum'),
                'datumVerlies': 'BG:inp.datumVerlies',
                'nationaliteit': {
                    'code': (MKSConverter.as_code(4), 'BG:gerelateerde BG:code'),
                    'omschrijving': 'BG:gerelateerde BG:omschrijving',
                },
                'inOnderzoek': 'BG:inOnderzoek'
            }]
        }

        return {
            'burgerservicenummer': 'BG:inp.bsn',
            'aNummer': 'BG:inp.a-nummer',
            'geheimhoudingPersoonsgegevens':
                (MKSConverter.true_if_in(['1', '2', '3', '4', '5', '6', '7']), 'BG:inp.indicatieGeheim'),
            'geslachtsaanduiding': (MKSConverter.as_geslachtsaanduiding,
                                    'BG:geslachtsaanduiding',
                                    'BG:geslachtsaanduiding@StUF:noValue'),
            'leeftijd': (MKSConverter.as_leeftijd, 'BG:geboortedatum',
                         'BG:geboortedatum@StUF:indOnvolledigeDatum',
                         'BG:overlijdensdatum'),
            'naam': {
                'geslachtsnaam': 'BG:geslachtsnaam',
                'voorletters': 'BG:voorletters',
                'voornamen': 'BG:voornamen',
                'voorvoegsel': 'BG:voorvoegselGeslachtsnaam',
                'adellijkeTitelPredikaat': {
                    'code': (MKSConverter.get_adellijke_titel_code, 'BG:adellijkeTitelPredikaat'),
                    'omschrijving': 'BG:adellijkeTitelPredikaat'
                },
                'aanhef': (MKSConverter.get_aanhef, communicatie_parameters),
                'aanschrijfwijze': (MKSConverter.get_aanschrijfwijze, communicatie_parameters),
                'aanduidingNaamgebruik': (MKSConverter.as_aanduiding_naamgebruik, 'BG:aanduidingNaamgebruik')
                },
            'nationaliteiten': (MKSConverter.get_nationaliteit, nationaliteit_parameters),
            'geboorte': {
                'datum': (
                    MKSConverter.as_datum_broken_down,
                    'BG:geboortedatum',
                    'BG:geboortedatum@StUF:indOnvolledigeDatum'
                ),
                'land': {
                    'code': (MKSConverter.as_code(4), 'BG:inp.geboorteLand'),
                    'omschrijving': (MKSConverter.get_land_omschrijving, 'BG:inp.geboorteLand'),
                },
                'plaats': {
                    'code': (MKSConverter.as_gemeente_code, 'BG:inp.geboorteplaats'),
                    'omschrijving': (MKSConverter.get_gemeente_omschrijving, 'BG:inp.geboorteplaats'),
                },
                },
            'overlijden': {
                'indicatieOverleden': (MKSConverter.true_if_exists, 'BG:overlijdensdatum'),
                'datum': (
                    MKSConverter.as_datum_broken_down,
                    'BG:overlijdensdatum',
                    'BG:overlijdensdatum@StUF:indOnvolledigeDatum'
                ),
                'land': {
                    'code': (MKSConverter.as_code(4), 'BG:inp.overlijdenLand'),
                    'omschrijving': (MKSConverter.get_land_omschrijving, 'BG:inp.overlijdenLand')
                },
                'plaats': {
                    'code': (MKSConverter.as_gemeente_code, 'BG:inp.overlijdenplaats'),
                    'omschrijving': (MKSConverter.get_gemeente_omschrijving, 'BG:inp.overlijdenplaats')
                }
                },
            'verblijfplaats': self.mapping_verblijfplaats,  # verblijfplaats is reordered in `NPSMapping.filter`
            'verblijfstitel': (
                    NPSMapping.verblijfstitel,
                    "BG:vbt.aanduidingVerblijfstitel",
                    "BG:ing.datumVerkrijgingVerblijfstitel",
                    "BG:ing.datumVerliesVerblijfstitel",
                    ["BG:inOnderzoek", ".!.[@elementnaam='aanduidingVerblijfstitel']"],
                    ["StUF:extraElementen", ".!.//StUF:extraElement[@naam='omschrijvingVerblijfstitel']"],
                )
        }

    @staticmethod
    def _filter_verblijfplaats(verblijfplaats: dict) -> dict:
        adres = {}
        functie = None

        for functie_adres in ['woonadres', 'briefadres']:
            cur_adres = verblijfplaats.pop(functie_adres, {})

            if any(cur_adres.values()):
                adres = cur_adres
                functie = functie_adres

        reordered = {
            'adresseerbaarObjectIdentificatie': verblijfplaats.pop('adresseerbaarObjectIdentificatie', None),
            'nummeraanduidingIdentificatie': adres.pop('nummeraanduidingIdentificatie', None),
            'functieAdres': functie,
            'indicatieVestigingVanuitBuitenland': verblijfplaats.pop('indicatieVestigingVanuitBuitenland', None),
            'locatiebeschrijving': adres.pop('locatiebeschrijving', None),
        }

        # dont return datumAanvangAdreshouding when address is foreign, see #66932
        # ie gemeenteVanInschrijving == {"code": "1999","omschrijving": "Registratie Niet Ingezetenen (RNI)"}
        if verblijfplaats["gemeenteVanInschrijving"]["code"] == "1999":
            verblijfplaats.pop("datumAanvangAdreshouding")

        return {**adres, **reordered, **verblijfplaats}

    @property
    def related(self):  # pragma: no cover
        return {
            'partners': 'BG:inp.heeftAlsEchtgenootPartner',
            'ouders': 'BG:inp.heeftAlsOuders',
            'kinderen': 'BG:inp.heeftAlsKinderen',
        }

    @classmethod
    def in_onderzoek(cls, values: Optional[list[Optional[str]]]) -> Optional[dict[str, bool]]:
        """Set all keys to True for each kenmerk. BG:inOnderzoek can return multiple nodes with different attributes.
        Currently, we only want the 'groepsnaam=Verblijfplaats' node, which is filtered in the xpath.
        If a 'J' value is in `values`, a dict of kenmerk: True is returned.

        :param values: A list of `str` or `None` if BG:inOnderzoek was found, else `None`.
        :return: A dictionary with all keys set to True or None.
        """
        if values is None or "J" not in values:
            return None

        return {
            "aanduidingBijHuisnummer": True,
            "datumAanvangAdreshouding": True,
            "datumIngangGeldigheid": True,
            "datumInschrijvingInGemeente": True,
            "datumVestigingInNederland": True,
            "functieAdres": True,
            "gemeenteVanInschrijving": True,
            "huisletter": True,
            "huisnummer": True,
            "huisnummertoevoeging": True,
            "nummeraanduidingIdentificatie": True,
            "adresseerbaarObjectIdentificatie": True,
            "landVanwaarIngeschreven": True,
            "locatiebeschrijving": True,
            "straat": True,
            "postcode": True,
            "korteNaam": True,
            "verblijfBuitenland": True,
            "woonplaats": True
        }

    @classmethod
    def verblijfstitel(
            cls, verblijfstitel: Optional[int], datum_verkrijging: Optional[str],
            datum_verlies: Optional[str], inonderzoek: list[str],
            omschrijving: list[Optional[str]]
    ) -> Optional[dict[str, Union[dict, str]]]:
        """Returns verblijfstitel when correctly set.

        :param verblijfstitel: code of the aanduiding.
        :param datum_verkrijging: A date formatted YYYYMMDD
        :param datum_verlies: A date formatted YYYYMMDD
        :param inonderzoek: In onderzoek values
        :param omschrijving: Description of verblijfstitel
        :return: A dict with all the verblijfstitel details.
        """
        today = datetime.date.today()
        if datum_verlies is not None and MKSConverter.to_date(datum_verlies) < today:
            return None

        if verblijfstitel is None or datum_verkrijging is None:
            return None

        verblijfstitel = {
            "aanduiding": {
                "code": f"{verblijfstitel}",
                "omschrijving": omschrijving[0] if omschrijving else None
            },
            "datumIngang": MKSConverter.as_datum_broken_down(datum_verkrijging),
            "datumEinde": MKSConverter.as_datum_broken_down(datum_verlies),
        }

        inonderzoek = [io for io in inonderzoek if io is not None]
        if len(inonderzoek) == 1 and inonderzoek[0] == 'J':
            verblijfstitel["inOnderzoek"] = {
                "aanduiding": True,
                "datumIngang": True,
                "datumEinde": True,
            }

        return verblijfstitel

    def sort_ouders(self, ouders: list):
        """Sorts ouders by:

        - geboortedatum descending
        - geslachtsaanduiding (vrouw, man, onbekend, ..)
        - geslachtsnaam ascending
        - voornamen ascending

        Adds ouderAanduiding attribute based on the ordering (ouder1, ouder2)

        :param ouders:
        :return:
        """

        def ouder_sorter(ouder):
            MAX_NAAM = 'zzzzzzzzzz'  # Value that is expected to compare above any real naam
            geslachtsaanduiding_order = {
                Geslachtsaanduiding.VROUW_FULL: 0,
                Geslachtsaanduiding.MAN_FULL: 1,
                Geslachtsaanduiding.ONBEKEND_FULL: 2,
                None: 3
            }

            # First sort key is geboortedatum descending
            geboorte = (get_value(ouder, 'geboorte', 'datum', 'datum') or '9999-99-99').replace('-', '')
            geboorte = int(geboorte)  # oldest first

            # Second key is geslachtsaanduiding on geslachtsaanduiding_order
            geslacht = geslachtsaanduiding_order[get_value(ouder, 'geslachtsaanduiding')]

            # Third key is geslachtsnaam ascending
            geslachtsnaam = get_value(ouder, 'naam', 'geslachtsnaam')
            geslachtsnaam = geslachtsnaam.lower() if geslachtsnaam else MAX_NAAM

            # Fourth key is voornamen ascending
            voornamen = get_value(ouder, 'naam', 'voornamen')
            voornamen = voornamen.lower() if voornamen else MAX_NAAM

            return (geboorte, geslacht, geslachtsnaam, voornamen)

        # Use Python sorted function with key argument. The ouder_sorter function returns a tuple that determines the
        # ordering, where lower numbers are sorted first.
        # First the first element of the tuple is evaluated, and only
        # if values for the first element are equal, the second element of the tuple is compared.
        #
        # For example: For three ouders, the lambda function below evaluates to the following tuples:
        # ouder 1: (-20200501, 1, 'geslachtsnaam', 'voornamen')
        # ouder 2: (-20200403, 1, 'geslachtsnaam', 'voornamen')
        # ouder 3: (-20200403, 0, 'geslachtsnaam', 'voornamen')
        #
        # The ordering will be: ouder 1, ouder 3, ouder 2, because ouder 1 has the lowest first element of the tuple.
        # Ouder 2 and 3 match on the first element, so are sorted on the second element.
        sorted_ouders = sorted(ouders, key=ouder_sorter)

        return [{**ouder, 'ouderAanduiding': f'ouder{idx + 1}'} for idx, ouder in enumerate(sorted_ouders)]

    def sort_kinderen(self, kinderen: list):
        """Sorts kinderen by:

        - geboortedatum descending
        - geslachtsnaam ascending
        - voornamen ascending

        :param kinderen:
        :return:
        """

        def kinderen_sorter(kind):
            MAX_NAAM = 'zzzzzzzzzz'  # Value that is expected to compare above any real naam

            # First sort key is geboortedatum descending
            geboorte = (get_value(kind, 'geboorte', 'datum', 'datum') or '9999-99-99').replace('-', '')
            geboorte = int(geboorte)  # oldest first

            # Second key is geslachtsnaam ascending
            geslachtsnaam = get_value(kind, 'naam', 'geslachtsnaam')
            geslachtsnaam = geslachtsnaam.lower() if geslachtsnaam else MAX_NAAM

            # Third key is voornamen ascending
            voornamen = get_value(kind, 'naam', 'voornamen')
            voornamen = voornamen.lower() if voornamen else MAX_NAAM

            return (geboorte, geslachtsnaam, voornamen)

        # See comments in sort_ouders for more info on sorted with key
        return sorted(kinderen, key=kinderen_sorter)

    def filter(self, mapped_object: dict, **kwargs) -> dict | None:
        """
        Filter the mapped object on overlijdensdatum
        Overleden personen are returned based on the inclusiefoverledenpersonen kwarg

        Filter the mapped object on either woonadres or briefadres.
        When the mapped object contains both, only use the the briefadres.

        :param mapped_object: The mapped response object
        :return:
        """
        if (
            mapped_object.get('overlijden', {}).get('indicatieOverleden')
            and not kwargs.get('inclusiefoverledenpersonen', False)
        ):
            return

        mapped_object['verblijfplaats'] = self._filter_verblijfplaats(mapped_object['verblijfplaats'])
        return super().filter(mapped_object)

    def _add_related_object_links(self, mapped_object: dict, links: dict, embedded_type: str, route: str):
        """Adds links to embedded objects of the form /ingeschrevenpersonen/<bsn>/embedded_type/<n> for each object.
        Adds links to top level, as well as self links to the embedded objects

        Expects mapped_object to contain a burgerservicenummer (should always be the case for objects in this class).

        :param mapped_object:
        :param links:
        :param embedded_type: e.g. ouders, partners
        :param route: the route name that is used to generate the link. Should accept route parameters 'bsn' and
        embedded_type_id (e.g. ouders_id, partners_id)
        :return:
        """
        url_param = f"{embedded_type}_id"

        def url_for_object(index):
            return get_auth_url(route,
                                bsn=mapped_object['burgerservicenummer'],
                                **{url_param: index}
                                )

        if mapped_object.get('_links', {}).get(embedded_type):
            objects = mapped_object['_links'][embedded_type]

            # Add the link to all embedded objects
            links[embedded_type] = [{'href': url_for_object(c)} for c, o in enumerate(objects, 1)]

            # Add the links to the embedded objects, if present
            for c, object in enumerate(mapped_object.get('_embedded', {}).get(embedded_type, []), 1):
                object['_links'] = {
                    **object.get('_links', {}),
                    'self': {
                        'href': url_for_object(c)
                    }
                }

    def get_links(self, mapped_object: dict) -> dict:
        """
        Return the HAL links that correspond with the mapped and filtered object (data)

        :param mapped_object: the mapped and filtered object
        :return:
        """
        links = super().get_links(mapped_object)

        if mapped_object.get('burgerservicenummer'):
            links['self'] = {
                'href': get_auth_url('brp_ingeschrevenpersonen_bsn', bsn=mapped_object['burgerservicenummer'])
            }

        self._add_related_object_links(
            mapped_object,
            links,
            'ouders',
            'brp_ingeschrevenpersonen_bsn_ouders_detail'
        )

        self._add_related_object_links(
            mapped_object,
            links,
            'kinderen',
            'brp_ingeschrevenpersonen_bsn_kinderen_detail'
        )
        self._add_related_object_links(
            mapped_object,
            links,
            'partners',
            'brp_ingeschrevenpersonen_bsn_partners_detail'
        )

        if self_url := links.get('self'):
            links["verblijfplaatshistorie"] = {"href": f"{self_url['href']}/verblijfplaatshistorie"}

        # 'verblijfplaatsNummeraanduiding' is deprecated, the HC api uses 'adres' now
        if mapped_object.get("verblijfplaats", {}).get("woonadres", {}).get("nummeraanduidingIdentificatie"):
            nummeraanduiding = mapped_object["verblijfplaats"]["woonadres"]["nummeraanduidingIdentificatie"]
            links["verblijfplaatsNummeraanduiding"] = {"href": f"{BAG_NAG_ENDPOINT}/{nummeraanduiding}"}

        return links


StufObjectMapping.register(NPSMapping)


class RelatedMapping(Mapping):
    """RelatedMapping is the mapping of a StUF element holding a related element.

    For example:

    <BG:inp.heeftAlsEchtgenootPartner StUF:entiteittype="NPSNPSHUW">
        <BG:gerelateerde StUF:entiteittype="NPS">
        ...
        </BG:gerelateerde>
        <other attrs />
    </BG:inp.heeftAlsEchtgenootPartner>

    The RelatedMapping has the element with type NPSNPSHUW as root. The embedded element with type NPS is the related
    object. All attributes that are defined in the NPSMapping are included in this mapping, based on the
    include_related property of this class.
    On top of these inherited attributes, a RelatedMapping can define its own mapping.

    The result is a combination of attributes from the embedded type (NPS) and the attributes defined on the
    NPSNPSHUW class.
    """

    @property
    def related_entity_wrapper(self):  # pragma: no cover
        return 'BG:gerelateerde'

    @property
    def include_related(self):  # pragma: no cover
        return []

    @property
    def override_related_filters(self):  # pragma: no cover
        return {}

    def filter(self, mapped_object: dict, **kwargs):
        """Filters :mapped_object:. Only keeps the keys present in self.mapping and self.include_related.

        The mapped_object includes ALL keys from the related mapping, plus the keys we defined in this instance.
        However, we only need the keys from the related mapping defined in include_related, plus our own mapped
        attributes.

        This method filters out all keys from the related entity we don't need.

        :param mapped_object:
        :param kwargs:
        :return:
        """
        mapped_object = {k: v for k, v in mapped_object.items() if k in
                         self.include_related + list(self.mapping.keys())
                         }

        return super().filter(mapped_object)


class NPSNPSHUWMapping(RelatedMapping):

    @property
    def answer_code(self) -> str:
        return "npsLa01"

    @property
    def entity_type(self):  # pragma: no cover
        return 'NPSNPSHUW'

    @property
    def override_related_filters(self):  # pragma: no cover
        return {
            'inclusiefoverledenpersonen': True,
        }

    # Include these attributes from the embedded (NPS) object
    @property
    def include_related(self):  # pragma: no cover
        return [
            'burgerservicenummer',
            'geslachtsaanduiding',
            'geboorte',
            'naam',
            'adellijkeTitelPredikaat',
            'geheimhoudingPersoonsgegevens'
        ]

    # And add these attributes
    @property
    def mapping(self):  # pragma: no cover
        return {
            'soortVerbintenis': (MKSConverter.as_soort_verbintenis, 'BG:soortVerbintenis'),
            'aangaanHuwelijkPartnerschap': {
                'datum': (MKSConverter.as_datum_broken_down,
                          'BG:datumSluiting',
                          'BG:datumSluiting@StUF:indOnvolledigeDatum'),
                'plaats': {
                    'code': (MKSConverter.as_gemeente_code, 'BG:plaatsSluiting'),
                    'omschrijving': (MKSConverter.get_gemeente_omschrijving, 'BG:plaatsSluiting'),
                },
                'land': {
                    'code': (MKSConverter.as_code(4), 'BG:landSluiting'),
                    'omschrijving': (MKSConverter.get_land_omschrijving, 'BG:landSluiting'),
                },
            },
            # datumOntbinding is used to filter out 'ontbonden huwelijken'.
            # Note that this field will never be exposed because its value will be None on exposed objects.
            'datumOntbinding': 'BG:datumOntbinding'
        }

    def filter(self, mapped_object: dict, **kwargs):
        """Filters out 'ontbonden huwelijken'

        :param mapped_object:
        :param kwargs:
        :return:
        """
        if mapped_object.get('datumOntbinding'):
            # Filter out 'ontbonden huwelijk'
            return None

        return super().filter(mapped_object, **kwargs)

    def get_links(self, mapped_object: dict) -> dict:
        links = super().get_links(mapped_object)

        if mapped_object.get('burgerservicenummer'):
            links['ingeschrevenPersoon'] = {
                'href': get_auth_url('brp_ingeschrevenpersonen_bsn', bsn=mapped_object['burgerservicenummer'])
            }
        return links


StufObjectMapping.register(NPSNPSHUWMapping)


class NPSFamilieRelatedMapping(RelatedMapping):
    """Acts as a parent class for family relations NPSNPSOUD and NPSNPSKND. Both classes share a large part of
    configuration that's placed in this class.
    """

    @property
    def override_related_filters(self):  # pragma: no cover
        return {
            'inclusiefoverledenpersonen': True,
        }

    # Include these attributes from the embedded (NPS) object
    @property
    def include_related(self):  # pragma: no cover
        return [
            'burgerservicenummer',
            'naam',
            'geboorte',
            'adellijkeTitelPredikaat',
            'geheimhoudingPersoonsgegevens'
        ]

    # And add these attributes
    @property
    def mapping(self):
        return {
            'aanduidingStrijdigheidNietigheid': 'BG:aanduidingStrijdigheidNietigheid',
            'datumIngangFamilierechtelijkeBetrekking': (
                MKSConverter.as_datum_broken_down, 'BG:datumIngangFamilierechtelijkeBetrekking'),
            'datumIngangFamilierechtelijkeBetrekkingRaw': 'BG:datumIngangFamilierechtelijkeBetrekking',
            # Add raw value for filter
            'datumEindeFamilierechtelijkeBetrekking': 'BG:datumEindeFamilierechtelijkeBetrekking',
        }

    def filter(self, mapped_object: dict, **kwargs):
        naam = mapped_object.get('naam', {})
        today = datetime.datetime.now().strftime('%Y%m%d')

        if mapped_object.get('aanduidingStrijdigheidNietigheid') == 'true':
            return None
        elif mapped_object.get('datumIngangFamilierechtelijkeBetrekkingRaw') and \
                mapped_object['datumIngangFamilierechtelijkeBetrekkingRaw'] > \
                today[:len(mapped_object['datumIngangFamilierechtelijkeBetrekkingRaw'])]:
            # datumIngangFamilierechtelijkeBetrekkingRaw should not be after today
            # Compares only the same number of characters as the given string, to match precision
            return None
        elif mapped_object.get('datumEindeFamilierechtelijkeBetrekking') and \
                mapped_object['datumEindeFamilierechtelijkeBetrekking'] < \
                today[:len(mapped_object['datumEindeFamilierechtelijkeBetrekking'])]:
            # datumEindeFamilierechtelijkeBetrekking should not be before today
            # Compares only the same number of characters as the given string, to match precision
            return None
        elif not naam.get('geslachtsnaam') and not naam.get('voornamen') and not mapped_object.get('geboorte'):
            # https://github.com/BRP-API/Haal-Centraal-BRP-bevragen/blob/master/features/ouders.feature
            # Strictly one of the attributes above need to be present according to haalcentraal specs
            # A client may not have authorisation in MKS for above attributes, so they appear empty
            # In that case, also check for burgerservicenummer so we return the ouder if present
            if not mapped_object.get("burgerservicenummer"):
                return None

        # Delete keys that were only included for filtering.
        mapped_object.pop('aanduidingStrijdigheidNietigheid', None)
        mapped_object.pop('datumIngangFamilierechtelijkeBetrekkingRaw', None)
        mapped_object.pop('datumEindeFamilierechtelijkeBetrekking', None)

        return super().filter(mapped_object, **kwargs)

    def get_links(self, mapped_object: dict) -> dict:
        links = super().get_links(mapped_object)

        if mapped_object.get('burgerservicenummer'):
            links['ingeschrevenPersoon'] = {
                'href': get_auth_url('brp_ingeschrevenpersonen_bsn', bsn=mapped_object['burgerservicenummer'])
            }
        return links


class NPSNPSOUDMapping(NPSFamilieRelatedMapping):

    @property
    def answer_code(self) -> str:
        return "npsLa01"

    @property
    def entity_type(self):  # pragma: no cover
        return 'NPSNPSOUD'

    @property
    def include_related(self):
        return [
            *super().include_related,
            'geslachtsaanduiding',
        ]

    @property
    def mapping(self):
        return {
            **super().mapping,
            'ouderAanduiding': 'BG:ouderAanduiding',
        }


StufObjectMapping.register(NPSNPSOUDMapping)


class NPSNPSKNDMapping(NPSFamilieRelatedMapping):

    @property
    def answer_code(self) -> str:
        return "npsLa01"

    @property
    def entity_type(self):  # pragma: no cover
        return 'NPSNPSKND'

    @property
    def include_related(self):
        return [
            *super().include_related,
            'leeftijd',
        ]


StufObjectMapping.register(NPSNPSKNDMapping)


class VerblijfplaatsHistorieMapping(NPSMapping):

    @property
    def answer_code(self) -> str:
        return "npsLa07"

    @property
    def related(self) -> dict:
        return {}

    def get_links(self, mapped_object: dict) -> dict:
        return {}

    @property
    def mapping_verblijfplaats(self) -> dict:
        return super().mapping_verblijfplaats | {
            "datumIngangGeldigheid": (
                MKSConverter.get_first_date_from_various,
                "StUF:tijdvakGeldigheid StUF:beginGeldigheid",  # first location
                "BG:verblijfsadres BG:begindatumVerblijf",  # fallback datumAanvangAdreshouding only actual
                "BG:inp.verblijftIn StUF:tijdvakRelatie StUF:beginRelatie",
                "BG:inp.datumInschrijving"
            ),
            "datumTot": (MKSConverter.as_datum_broken_down, "StUF:tijdvakGeldigheid StUF:eindGeldigheid")
        }

    @property
    def mapping(self) -> dict:
        return {
            # necessary for filter overleden persoon, remove after filter
            # NB: user needs authentication for this field
            "overlijden": {"indicatieOverleden": (MKSConverter.true_if_exists, "BG:overlijdensdatum")},
            "verblijfplaats": self.mapping_verblijfplaats,
            "historieMaterieel": ["BG:historieMaterieel", self.mapping_verblijfplaats]
        }

    def filter(self, mapped_object: dict, **kwargs) -> dict | None:
        if historic := mapped_object.get("historieMaterieel"):
            mapped_object["historieMaterieel"] = [self._filter_verblijfplaats(vbo) for vbo in historic]

        # verblijfplaats is filtered in super().filter
        if result := super().filter(mapped_object, **kwargs):
            result.pop("overlijden", None)

            # add links to adres/adresobjectid after filtering woon/brief adres
            for obj in result["verblijfplaats"], *result["historieMaterieel"]:
                self._add_links(obj)

        return result

    @staticmethod
    def _get_href_from_objectid(object_id: str) -> str:
        try:
            return {"01": BAG_VBO_ENDPOINT, "02": BAG_LPS_ENDPOINT, "03": BAG_SPS_ENDPOINT}[object_id[4:6]]
        except (KeyError, IndexError):
            pass

    def _add_links(self, verblijfplaats: dict):
        links = {}

        if nr_id := verblijfplaats.get("nummeraanduidingIdentificatie"):
            links["adres"] = {"href": f"{BAG_NAG_ENDPOINT}/{nr_id}"}

        if adrsobj_id := verblijfplaats.get("adresseerbaarObjectIdentificatie"):
            if href := self._get_href_from_objectid(adrsobj_id):
                links["adresseerbaarObject"] = {"href": f"{href}/{adrsobj_id}"}

        if links:
            verblijfplaats["_links"] = links


StufObjectMapping.register(VerblijfplaatsHistorieMapping)
