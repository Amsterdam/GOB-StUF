"""
Request argument checks are defined here

"""
import re


class ArgumentCheck():
    is_boolean = {
        'check': lambda v: v in ['true', 'false'],
        'msg': {
            'code': 'boolean',
            'reason': 'Waarde is geen geldige boolean.'
        }
    }

    is_postcode = {
        'check': lambda v: re.match(r'^[1-9]{1}[0-9]{3}[A-Z]{2}$', v) is not None,
        'msg': {
            "code": "pattern",
            "reason": "Waarde voldoet niet aan patroon ^[1-9]{1}[0-9]{3}[A-Z]{2}$."
        }
    }

    is_integer = {
        'check': lambda v: re.match(r'^\d+$', v) is not None,
        'msg': {
            "code": "integer",
            "reason": "Waarde is geen geldige integer."
        }
    }

    is_positive_integer = {
        'check': lambda v: re.match(r'^[1-9][0-9]*$', v) is not None,
        'msg': {
            "code": "minimum",
            "reason": "Waarde is lager dan minimum 1."
        }
    }

    @classmethod
    def validate(cls, checks, value):
        """
        Validate the given value against one or more checks
        The first failing check is returned, or None if all checks pass

        :param checks:
        :param value:
        :return:
        """
        if not isinstance(checks, list):
            # Accept a single check as value by converting it to a list
            checks = [checks]
        for check in checks:
            if not check['check'](value):
                return check
