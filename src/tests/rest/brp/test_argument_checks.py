from unittest import TestCase
from unittest.mock import patch, MagicMock

from gobstuf.rest.brp.argument_checks import ArgumentCheck

class TestArgumentCheck(TestCase):

    def test_validate(self):
        check = ArgumentCheck.is_boolean
        for v in ['true', 'false']:
            self.assertIsNone(ArgumentCheck.validate(check, v))
        for v in ['True', 'False', 'TRUE', 'FALSE', '', '1', '0', 't', 'f']:
            self.assertEqual(ArgumentCheck.validate(check, v), check)

        check = ArgumentCheck.is_postcode
        for v in ['1234AB', '9999XX']:
            self.assertIsNone(ArgumentCheck.validate(check, v))
        for v in ['1234ab', '123456', '1234 AB', '']:
            self.assertEqual(ArgumentCheck.validate(check, v), check)

        check = ArgumentCheck.is_integer
        for v in ['0', '1']:
            self.assertIsNone(ArgumentCheck.validate(check, v))
        for v in ['-1', '', '1.5', 'one']:
            self.assertEqual(ArgumentCheck.validate(check, v), check)

        check = ArgumentCheck.is_positive_integer
        for v in ['1', '100']:
            self.assertIsNone(ArgumentCheck.validate(check, v))
        for v in ['0', '-1', '', '1.5', 'one']:
            self.assertEqual(ArgumentCheck.validate(check, v), check)

        check = [ArgumentCheck.is_integer, ArgumentCheck.is_positive_integer]
        for v in ['1', '100']:
            self.assertIsNone(ArgumentCheck.validate(check, v))
        for v in ['-1', '', '1.5', 'one']:
            self.assertEqual(ArgumentCheck.validate(check, v), ArgumentCheck.is_integer)
        for v in ['0']:
            self.assertEqual(ArgumentCheck.validate(check, v), ArgumentCheck.is_positive_integer)
