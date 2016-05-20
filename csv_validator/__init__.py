import csv
import collections

from .fields import Field


class OrderedMetaclass(type):

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
                subclass._fieldnames.append(key)
        return subclass


class ValidatedDictReader(csv.DictReader, metaclass=OrderedMetaclass):

    @property
    def fieldnames(self):
        return self.__class__._fieldnames

    def __next__(self):
        row = next(self.reader)
        self.line_num = self.reader.line_num

        # Skip the first row if it's headers...
        if self.line_num == 1 and row == self.fieldnames:
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

        # lf = len(self.fieldnames)
        # lr = len(row)
        # if lf < lr:
        #     d[self.restkey] = row[lf:]
        # elif lf > lr:
        #     for key in self.fieldnames[lr:]:
        #         d[key] = self.restval
        # print(d)
        for name, field in self._fields.items():
            try:
                d[name] = field.to_python(d[name])
            except KeyError as e:
                print(data)
                raise e

        return d

    # def __init__(self, f, *args, **kwargs):
    #     fieldnames = []
    #     for key, value in self.__dict__.items():
    #         print(key, value)
    #         if isinstance(value, Field):
    #             value.name = key
    #             fieldnames.append(key)

    #     print(fieldnames)

    #     super().__init__(f, fieldnames=fieldnames, *args, **kwargs)
