# csv-validator [![Build Status](https://travis-ci.org/csinchok/csv-validator.svg?branch=master)](https://travis-ci.org/csinchok/csv-validator) [![PyPI version](https://badge.fury.io/py/csv_validator.svg)](https://badge.fury.io/py/csv_validator)

A simple wrapper for the `csv` module. There are many like it, but this one is mine.

To install:

`> pip install csv-validator`

A quick sample for the impatient:

```python
from csv_validator import DictReader
from csv_validator import fields

class SampleReader(DictReader):
    foo = fields.IntegerField(blank=False)
    bar = fields.DateField()
    baz = fields.Field(regex='[A-Z0-9]+')

# A valid document
f = io.StringIO('1,02/01/2016,FOO')
reader = SampleReader(f)
next(reader)
# {'foo': 1, 'bar': datetime.date(2016, 2, 1), 'baz': 'FOO'}

# Invalid documents will throw csv_validator.exceptions.ValidationError
f = io.StringIO(',02/01/2016,FOO')
reader = SampleReader(f)
next(reader)
# ValidationError('Field may not be blank')

f = io.StringIO('1,02-01-2016,FOO')
reader = SampleReader(f)
next(reader)
# ValidationError('Invalid date format')
```