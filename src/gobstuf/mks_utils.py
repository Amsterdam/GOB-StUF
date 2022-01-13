"""
MKS utility methods

"""
import datetime
from calendar import isleap
from typing import Optional

from gobstuf.indications import Geslachtsaanduiding, AanduidingNaamgebruik, IncompleteDateIndicator, \
    SoortVerbintenis, AanduidingBijzonderNederlanderschap
from gobstuf.lib.communicatie import Persoon, Partner, Communicatie
from gobstuf.reference_data.code_resolver import CodeResolver, DataItemNotFoundException


def _today():
    return datetime.datetime.now().date()


class MKSConverter:
    """
    Utility class to convert MKS values to return in the REST response

    Input values are in StUF MKS format
    Output values are in REST API output format
    """
    _MKS_DATUM_FORMAT = "yyyymmdd"
    _MKS_DATUM_PARSE_FORMAT = "%Y%m%d"

    @classmethod
    def _is_mks_datum(cls, mks_datum):
        if not mks_datum or len(mks_datum) != len(cls._MKS_DATUM_FORMAT):
            # Minimal requirement is that the length is OK
            return False

        try:
            # Simply try to parse the date, if that succeeds then return True
            datetime.datetime.strptime(mks_datum, cls._MKS_DATUM_PARSE_FORMAT)
            return True
        except (ValueError, TypeError):
            return False

    @classmethod
    def _yyyy(cls, mks_datum):
        return mks_datum[0:4] if cls._is_mks_datum(mks_datum) else None

    @classmethod
    def _mm(cls, mks_datum):
        return mks_datum[4:6] if cls._is_mks_datum(mks_datum) else None

    @classmethod
    def _dd(cls, mks_datum):
        return mks_datum[6:8] if cls._is_mks_datum(mks_datum) else None

    @classmethod
    def as_datum_broken_down(cls, mks_datum, ind_onvolledige_datum=None):
        if cls._is_mks_datum(mks_datum):
            return {
                'datum': cls.as_datum(mks_datum, ind_onvolledige_datum),
                'jaar': cls.as_jaar(mks_datum, ind_onvolledige_datum),
                'maand': cls.as_maand(mks_datum, ind_onvolledige_datum),
                'dag': cls.as_dag(mks_datum, ind_onvolledige_datum)
            }

    @classmethod
    def as_datum(cls, mks_datum, ind_onvolledige_datum=None):
        if cls._is_mks_datum(mks_datum) and IncompleteDateIndicator(ind_onvolledige_datum).is_datum_complete():
            return f"{cls._yyyy(mks_datum)}-{cls._mm(mks_datum)}-{cls._dd(mks_datum)}"

    @classmethod
    def as_jaar(cls, mks_datum, ind_onvolledige_datum=None):
        if cls._is_mks_datum(mks_datum) and IncompleteDateIndicator(ind_onvolledige_datum).is_jaar_known():
            return int(cls._yyyy(mks_datum))

    @classmethod
    def as_maand(cls, mks_datum, ind_onvolledige_datum=None):
        if cls._is_mks_datum(mks_datum) and IncompleteDateIndicator(ind_onvolledige_datum).is_maand_known():
            return int(cls._mm(mks_datum))

    @classmethod
    def as_dag(cls, mks_datum, ind_onvolledige_datum=None):
        if cls._is_mks_datum(mks_datum) and IncompleteDateIndicator(ind_onvolledige_datum).is_dag_known():
            return int(cls._dd(mks_datum))

    @classmethod
    def to_date(cls, mks_datum: str) -> Optional[datetime.date]:
        """Make  python date object from a mks_datum string.

        :param mks_datum: Date formatted like yyyymmdd
        :return: a datetime object, if it can be formatted.
        """
        if cls._is_mks_datum(mks_datum):
            return datetime.datetime.strptime(mks_datum, cls._MKS_DATUM_PARSE_FORMAT).date()

    @classmethod
    def _get_age(cls, now, birthday):
        """
        Age calculation that takes leap years into account

        :param now:
        :param birthday:
        :return:
        """
        if birthday.month == 2 and birthday.day == 29 and not isleap(now.year):
            # Born on 29 february (leap year)
            # If the current year is not a leap year then use March 1 as birthdate for age calculation
            day = birthday.replace(year=now.year, month=birthday.month + 1, day=1)
        else:
            day = birthday.replace(year=now.year)

        if day > now:
            return now.year - birthday.year - 1
        else:
            return now.year - birthday.year

    @classmethod
    def as_leeftijd(cls, mks_geboortedatum,  ind_onvolledige_datum=None, overlijdensdatum=None):
        """
        birthday string as age

        Accepts birthday strings with unknown month. The age is unknown in the same month
        but otherwise simple known as if the birthday was on a arbitrary day in the month

        :param mks_geboortedatum:
        :param is_overleden:
        :return:
        """
        if not mks_geboortedatum or overlijdensdatum:
            return None

        incomplete_date_indicator = IncompleteDateIndicator(ind_onvolledige_datum)
        if not (incomplete_date_indicator.is_jaar_known() and incomplete_date_indicator.is_maand_known()):
            # jaar and maand are mandatory to calculate age
            return None

        if cls._is_mks_datum(mks_geboortedatum):
            # Interpret all dates as dates in the current timezone
            now = _today()
            birthday = datetime.datetime.strptime(mks_geboortedatum, cls._MKS_DATUM_PARSE_FORMAT).date()
            if incomplete_date_indicator.is_dag_known() or now.month != birthday.month:
                # The dag is mandatory. Unless the current month is unequal to the birthday month
                # In the latter case the age can be calculated without knowing the exact birthday dag
                return cls._get_age(now=now, birthday=birthday)

    @classmethod
    def as_geslachtsaanduiding(cls, mks_geslachtsaanduiding, no_value=None):
        return Geslachtsaanduiding(mks_geslachtsaanduiding, no_value).description

    @classmethod
    def as_soort_verbintenis(cls, mks_soort_verbintenis):
        return SoortVerbintenis(mks_soort_verbintenis).description

    @classmethod
    def as_aanduiding_naamgebruik(cls, mks_aanduiding_naamgebruik):
        return AanduidingNaamgebruik(mks_aanduiding_naamgebruik).description

    @classmethod
    def as_aanduiding_bijzonder_nederlanderschap(cls, mks_aanduiding_bijzonder_nederlanderschap, no_value=None):
        return AanduidingBijzonderNederlanderschap(mks_aanduiding_bijzonder_nederlanderschap, no_value).description

    @classmethod
    def as_code(cls, length):
        """
        Returns a function to convert a code to a zero padded string of length <length>
        :param length:
        :return:
        """
        def as_code(mks_code):
            if mks_code is not None:
                return mks_code.zfill(length)
        return as_code

    @classmethod
    def resolve_code(cls, resolver, mks_code):
        # Make sure we send a 4 digit code to the code resolver
        as_code = MKSConverter.as_code(4)
        code = as_code(mks_code)
        return resolver(code) if code else code

    @classmethod
    def get_gemeente_code(cls, omschrijving):
        return CodeResolver.get_gemeente_code(omschrijving)

    @classmethod
    def as_gemeente_code(cls, mks_code):
        """Returns zero-padded gemeente_code if gemeente_code is known. Returns None otherwise.
        (If gemeente_code is not known, get_gemeente_omschrijving returns the code as well)

        :param mks_code:
        :return:
        """
        try:
            cls.resolve_code(CodeResolver.get_gemeente, mks_code)
            return cls.as_code(4)(mks_code)
        except DataItemNotFoundException:
            return None

    @classmethod
    def get_gemeente_omschrijving(cls, mks_code):
        resolver = CodeResolver.get_gemeente
        try:
            return cls.resolve_code(resolver, mks_code)
        except DataItemNotFoundException:
            # Return code. Can happen in case of foreign places
            return mks_code

    @classmethod
    def get_land_omschrijving(cls, mks_code):
        resolver = CodeResolver.get_land
        return cls.resolve_code(resolver, mks_code)

    @classmethod
    def get_adellijke_titel_code(cls, mks_omschrijving):
        return CodeResolver.get_adellijke_titel_code(mks_omschrijving)

    @classmethod
    def true_if_exists(cls, property):
        """
        Return True if the property has a value, None if the property is empty

        :param property:
        :return:
        """
        if property is not None:
            return True

    @classmethod
    def true_if_equals(cls, value):
        """
        Returns a function to check if the property is equal to the given value
        :param property:
        :param value:
        :return:
        """
        def true_if_equals(property):
            return property == value

        return true_if_equals

    @classmethod
    def true_if_in(cls, value):
        """
        Returns a function to check if the property is in the given list
        :param property:
        :param value:
        :return:
        """
        def true_if_in(property):
            if property is not None and property in value:
                return True

        return true_if_in

    @classmethod
    def _get_communicatie(cls, communicatie_parameters):
        persoon = Persoon(communicatie_parameters['persoon'])
        partners = [Partner(partner) for partner in communicatie_parameters['partners']
                    if not partner['ontbindingHuwelijkPartnerschap']['datum']]
        partnerhistorie = [Partner(partner) for partner in communicatie_parameters['partners']
                           if partner['ontbindingHuwelijkPartnerschap']['datum']]
        return Communicatie(persoon, partners, partnerhistorie)

    @classmethod
    def get_aanhef(cls, communicatie_parameters):
        communicatie = cls._get_communicatie(communicatie_parameters)
        return communicatie.aanhef

    @classmethod
    def get_aanschrijfwijze(cls, communicatie_parameters):
        communicatie = cls._get_communicatie(communicatie_parameters)
        return communicatie.aanschrijfwijze

    @classmethod
    def _get_nationaliteit(cls, nationaliteit_parameters):
        nationaliteiten = []
        for nationaliteit in nationaliteit_parameters['nationaliteiten']:
            # Handle <BG:inp.heeftAlsNationaliteit ... StUF:noValue="nietGeautoriseerd"/>
            if nationaliteit["nationaliteit"]["code"] is None:
                continue

            if not nationaliteit['datumVerlies']:
                result = {
                    'aanduidingBijzonderNederlanderschap':
                        nationaliteit_parameters['aanduidingBijzonderNederlanderschap'],
                    'datumIngangGeldigheid': nationaliteit['datumIngangGeldigheid'],
                    'nationaliteit': nationaliteit['nationaliteit']
                }
                nationaliteiten.append(result)

        return nationaliteiten

    @classmethod
    def get_nationaliteit(cls, nationaliteit_parameters: dict) -> Optional[list[dict]]:
        """Returns nationalities, if the user has permission to see them.

        :param nationaliteit_parameters: A dict with parameters coming from xml.
        :return:
        """
        nationaliteiten = cls._get_nationaliteit(nationaliteit_parameters)
        if len(nationaliteiten) == 0:
            return None

        return nationaliteiten

    @classmethod
    def get_verblijf_buitenland(cls, verblijf_buitenland_parameters):
        if verblijf_buitenland_parameters['land']['code'] is None:
            return None

        if verblijf_buitenland_parameters['land']['code'] == '0000':
            return {
                'vertrokkenOnbekendWaarheen': True
            }

        return verblijf_buitenland_parameters
