import datetime
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
            context.exception,
            ValidationError({'foo': 'Field may not be blank'})
        )

    def test_regex(self):
        f = io.StringIO('1,02/01/2016,foo')
        reader = SampleReader(f)
        with self.assertRaises(ValidationError) as context:
            reader.__next__()
        self.assertEqual(
            context.exception,
            ValidationError({'baz': 'Doesn\'t match "[A-Z0-9_]{3,9}"'})
        )

    def test_integer(self):
        f = io.StringIO('X,02/01/2016,FOO')
        reader = SampleReader(f)

        with self.assertRaises(ValidationError) as context:
            reader.__next__()
        self.assertEqual(
            context.exception,
            ValidationError({'foo': 'Must be an int'})
        )

    def test_date(self):
        f = io.StringIO('1,02-01-2016,FOO')
        reader = SampleReader(f)

        with self.assertRaises(ValidationError) as context:
            reader.__next__()
        self.assertEqual(
            context.exception,
            ValidationError({'bar': 'Invalid date format'})
        )

    def test_strict_validation(self):
        f = io.StringIO('\n'.join([
            '1,02/01/2016,foo',
            'X,02/01/2016,FOO',
            '1,02-01-2016,FOO',
            ',02-01-2016,foo',
            '66,02/01/1987,BAZ'
        ]))

        reader = SampleReader(f)

        with self.assertRaises(ValidationError) as context:
            next(reader)
        
        self.assertEqual(
            context.exception,
            ValidationError({'baz': 'Doesn\'t match "[A-Z0-9_]{3,9}"'})
        )

    def test_capture_errors(self):
        f = io.StringIO('\n'.join([
            '1,02/01/2016,foo',
            'X,02/01/2016,FOO',
            '1,02-01-2016,FOO',
            ',02-01-2016,foo',
            '66,02/01/1987,BAZ'
        ]))

        reader = SampleReader(f)
        rows = [d for d in reader.iter_lines(skip_errors=True)]

        self.assertEqual(len(rows), 1)
        self.assertEqual(
            rows,
            [(4, {'foo': 66, 'bar': datetime.date(1987, 2, 1), 'baz': 'BAZ'})]
        )

        self.assertEqual(
            reader.errors[0],
            {
                'baz': 'Doesn\'t match "[A-Z0-9_]{3,9}"'
            }
        )

        self.assertEqual(
            reader.errors[1],
            {
                'foo': 'Must be an int'
            }
        )

        self.assertEqual(
            reader.errors[2],
            {
                'bar': 'Invalid date format'
            }
        )

        self.assertEqual(len(reader.errors[3]), 3)
