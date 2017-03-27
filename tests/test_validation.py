import io
from unittest import TestCase

from csv_validator import DictReader
from csv_validator import fields
from csv_validator.exceptions import ValidationError


class SampleReader(DictReader):

    foo = fields.IntegerField(required=True)
    bar = fields.DateField(required=True)
    baz = fields.Field(required=True, regex='[A-Z0-9_]{3,9}')


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

    def test_capture_errors(self):

        class CapturingReader(DictReader):
            foo = fields.IntegerField()
            bar = fields.DateField()
            baz = fields.Field(regex='[A-Z0-9_]{3,9}')


        f = io.StringIO('\n'.join([
            '1,02/01/2016,foo',
            'X,02/01/2016,FOO',
            '1,02-01-2016,FOO',
            ',02-01-2016,foo'
        ]))

        reader = CapturingReader(f)

        for row in reader:
            pass


        self.assertEqual(
            reader.errors[0]['errors'],
            {
                'baz': 'Doesn\'t match "[A-Z0-9_]{3,9}"'
            }
        )

        self.assertEqual(
            reader.errors[1]['errors'],
            {
                'foo': 'Must be an int'
            }
        )

        self.assertEqual(
            reader.errors[2]['errors'],
            {
                'bar': 'Invalid date format'
            }
        )

        self.assertEqual(len(reader.errors[3]['errors']), 2)
