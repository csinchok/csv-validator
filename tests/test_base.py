import datetime
import io
from unittest import TestCase

from csv_validator import DictReader
from csv_validator import fields

TEST_FILE_HEADERS = """foo,bar
1,02/01/2016
2,02/02/2016
3,02/03/2016
4,02/04/2016
"""

TEST_FILE_MAPPED_HEADERS = """Foosball,Barry
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


class SampleReader(DictReader):

    foo = fields.IntegerField()
    bar = fields.DateField()


class SampleReaderMapped(DictReader):
    foo = fields.IntegerField(index='Foosball')
    bar = fields.DateField(index='Barry')


class ValidationTestCase(TestCase):

    def test_with_headers(self):
        f = io.StringIO(TEST_FILE_HEADERS)
        reader = SampleReader(f)

        for i, row in enumerate(reader):
            self.assertEqual(row, {
                'foo': i + 1,
                'bar': datetime.date(2016, 2, i + 1)
            })

    def test_with_mapped_headers(self):
        f = io.StringIO(TEST_FILE_MAPPED_HEADERS)
        reader = SampleReaderMapped(f)

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


class SampleIndexedDictReader(DictReader):
    foo = fields.Field(index=1)
    bar = fields.Field(index=3)
    baz = fields.Field(index=10)


TEST_DATA_INDEXED = '''bullshit,foo,bs,bar,whatever,something,who,what,where,no,baz
bs,foo,bs,bar,when,arg,who,what,where,,baz
no,foo,bs,bar,whom?,something,blank,don't care,where,,baz
what,foo,bs,bar,python,ack,who,what,,,baz
'''


class IndexTestCase(TestCase):

    def test_fieldnames(self):
        f = io.StringIO()
        reader = SampleIndexedDictReader(f)

        self.assertEqual(
            reader.fieldnames,
            [
                'not_captured_0', 'foo', 'not_captured_2', 'bar', 'not_captured_4',
                'not_captured_5', 'not_captured_6', 'not_captured_7', 'not_captured_8',
                'not_captured_9', 'baz'
            ]
        )

    def test_reader(self):
        f = io.StringIO(TEST_DATA_INDEXED)
        reader = SampleIndexedDictReader(f)

        for row in reader:
            self.assertEqual(row, {
                'foo': 'foo',
                'bar': 'bar',
                'baz': 'baz'
            })
