import copy
import itertools


def invert(f):
    def wrapped(*args, **kwargs):
        return not f(*args, **kwargs)
    return wrapped


def or_(f1, f2):
    def wrapped(*args, **kwargs):
        return (f1(*args, **kwargs) or f2(*args, **kwargs))
    return wrapped


def and_(f1, f2):
    def wrapped(*args, **kwargs):
        return (f1(*args, **kwargs) and f2(*args, **kwargs))
    return wrapped


class BaseFilter(object):
    def __init__(self, filter_):
        self._filter = filter_

    def __call__(self, item):
        return self.test(item)

    def __ror__(self, other):
        return itertools.ifilter(self.test, other)

    def __or__(self, other):
        cpy = copy.copy(self)
        cpy.test = or_(cpy.test, other.test)
        return cpy

    def __and__(self, other):
        cpy = copy.copy(self)
        self.test = and_(cpy.test, other.test)
        return cpy

    def not_(self):
        self.test = invert(self.test)
        return self

    def test(self, row):
        return True


class TextFilter(BaseFilter):
    def test(self, row):
        for col in row.itervalues():
            if self._filter.lower() in col.lower():
                return True
        return False


class ReFilter(BaseFilter):
    def test(self, row):
        for col in row.itervalues():
            if self._filter.search(unicode(col)) is not None:
                return True
        return False


class NewsFilter(TextFilter):
    def test(self, row):
        return self._filter in row['title']
