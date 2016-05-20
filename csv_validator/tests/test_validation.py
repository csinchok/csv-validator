import datetime
import io
from unittest import TestCase

from .. import ValidatedDictReader
from .. import fields
from ..exceptions import ValidationError


class SampleReader(ValidatedDictReader):

    foo = fields.IntegerField(blank=False)
    bar = fields.DateField()
    baz = fields.Field(regex='[A-Z0-9_]{3,9}')


class ValidationTestCase(TestCase):

    def test_blank(self):
        f = io.StringIO(',02/01/2016,FOO')
        reader = SampleReader(f)

        with self.assertRaises(ValidationError) as context:
            reader.__next__()
        self.assertEqual(
            str(context.exception),
            'Field may not be blank'
        )

    def test_regex(self):
        f = io.StringIO('1,02/01/2016,foo')
        reader = SampleReader(f)
        with self.assertRaises(ValidationError) as context:
            reader.__next__()
        self.assertEqual(
            str(context.exception),
            'Doesn\'t match "[A-Z0-9_]{3,9}"'
        )

    def test_integer(self):
        f = io.StringIO('X,02/01/2016,FOO')
        reader = SampleReader(f)

        with self.assertRaises(ValidationError) as context:
            reader.__next__()
        self.assertEqual(
            str(context.exception),
            'Must be an int'
        )

    def test_date(self):
        f = io.StringIO('1,02-01-2016,FOO')
        reader = SampleReader(f)

        with self.assertRaises(ValidationError) as context:
            reader.__next__()
        self.assertEqual(
            str(context.exception),
            'Invalid date format'
        )
