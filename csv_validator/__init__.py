import csv
import collections

from .fields import Field
from .exceptions import ValidationError


class ValidationMetaclass(type):

    @classmethod
    def __prepare__(self, name, bases):
        return collections.OrderedDict()

    def __new__(cls, name, bases, dct):
        subclass = type.__new__(cls, name, bases, dct)

        subclass._fieldnames = []
        subclass._fields = {}
        for key, value in dct.items():
            if isinstance(value, Field):
                subclass._fields[key] = value
                if value.index is None:
                    subclass._fieldnames.append(key)
                else:
                    if not isinstance(value.index, int):
                        continue

                    extra_count = value.index - len(subclass._fieldnames) + 1
                    for i in range(extra_count):
                        index = len(subclass._fieldnames)
                        fieldname = 'not_captured_{}'.format(index)
                        subclass._fields[fieldname] = None
                        subclass._fieldnames.append(fieldname)

                    subclass._fieldnames[value.index] = key
        return subclass


class DictReader(csv.DictReader, metaclass=ValidationMetaclass):

    def __init__(self, *args, capture_errors=False, **kwargs):
        super().__init__(*args, **kwargs)

        self.capture_errors = capture_errors
        self.errors = {}

    @property
    def fieldnames(self):
        return self.__class__._fieldnames

    def __next__(self):
        row = next(self.reader)

        # Skip the first row if it's headers...
        if self.line_num == 0:
            if row == self.fieldnames:
                row = next(self.reader)
            elif self.fieldnames == []:
                for index, fieldname in enumerate(row):
                    for key, value in self._fields.items():
                        if value and value.index == fieldname:
                            self.__class__._fieldnames.append(key)
                            break
                    else:
                        fieldname = 'not_captured_{}'.format(index)
                        self.__class__._fields[fieldname] = None
                        self.__class__._fieldnames.append(fieldname)

                row = next(self.reader)

        # unlike the basic reader, we prefer not to return blanks,
        # because we will typically wind up with a dict full of None
        # values
        while row == []:
            row = next(self.reader)
        d = dict(zip(self.fieldnames, row))

        lf = len(self.fieldnames)
        lr = len(row)
        if lf < lr:
            d[self.restkey] = row[lf:]
        elif lf > lr:
            for key in self.fieldnames[lr:]:
                d[key] = self.restval

        for name, field in self._fields.items():
            if name.startswith('not_captured_'):
                if name in d:
                    del d[name]
                continue
            try:
                d[name] = field.to_python(d[name])
            except ValidationError as e:
                if not self.capture_errors:
                    raise e

                if self.line_num not in self.errors:
                    self.errors[self.line_num] = {'data': row, 'errors': {}}

                self.errors[self.line_num]['errors'][name] = str(e)

        self.line_num = self.reader.line_num

        return d
