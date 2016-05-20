import datetime
import io
from unittest import TestCase

from .. import ValidatedDictReader
from .. import fields

TEST_FILE_HEADERS = """foo,bar
1,02/01/2016
2,02/02/2016
3,02/03/2016
4,02/04/2016
"""

TEST_FILE_NO_HEADERS = """1,02/01/2016
2,02/02/2016
3,02/03/2016
4,02/04/2016
"""


TEST_FILE_EXTRA_COLUMNS = """1,02/01/2016,6
2,02/02/2016,7
3,02/03/2016,8
4,02/04/2016,9
"""

TEST_FILE_MISSING_COLUMNS = """1
2
3
4
"""

TEST_FILE_MISSING_DATA = """,02/01/2016
,02/02/2016
,02/03/2016
,02/04/2016
"""


class SampleReader(ValidatedDictReader):

    foo = fields.IntegerField()
    bar = fields.DateField()


class ValidationTestCase(TestCase):

    def test_with_headers(self):
        f = io.StringIO(TEST_FILE_HEADERS)
        reader = SampleReader(f)

        for i, row in enumerate(reader):
            self.assertEqual(row, {
                'foo': i + 1,
                'bar': datetime.date(2016, 2, i + 1)
            })

    def test_without_headers(self):
        f = io.StringIO(TEST_FILE_NO_HEADERS)
        reader = SampleReader(f)

        for i, row in enumerate(reader):
            self.assertEqual(row, {
                'foo': i + 1,
                'bar': datetime.date(2016, 2, i + 1)
            })

    def test_extra_columns(self):
        f = io.StringIO(TEST_FILE_EXTRA_COLUMNS)
        reader = SampleReader(f)

        for i, row in enumerate(reader):
            self.assertEqual(row, {
                'foo': i + 1,
                'bar': datetime.date(2016, 2, i + 1),
                None: [str(i + 6)]
            })

    def test_missing_columns(self):
        f = io.StringIO(TEST_FILE_MISSING_COLUMNS)
        reader = SampleReader(f)

        for i, row in enumerate(reader):
            self.assertEqual(row, {
                'foo': i + 1,
                'bar': None
            })

    def test_missing_data(self):
        f = io.StringIO(TEST_FILE_MISSING_DATA)
        reader = SampleReader(f)

        for i, row in enumerate(reader):
            self.assertEqual(row, {
                'foo': None,
                'bar': datetime.date(2016, 2, i + 1)
            })
