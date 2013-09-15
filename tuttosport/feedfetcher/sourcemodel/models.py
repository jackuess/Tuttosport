from cStringIO import StringIO
import datetime
from email.utils import mktime_tz, parsedate_tz
import functools
import re
import types
from urlparse import urlparse

try:
    from lxml import etree
except ImportError:
    etree = None
try:
    import requests
except ImportError:
    requests = None


def iterrole(arg=None, name=None):
    def decorated(f):
        @functools.wraps(f)
        def wrapped(*args, **kwargs):
            if query is None:
                return f(*args, **kwargs)

            self = args[0]
            value = self._get_col(query)[0]
            return f(self, value, *args[1:], **kwargs)

        wrapped.is_iterrole = True
        name_ = name
        if name_ is None:
            name_ = f.__name__
        wrapped.name = name_
        return wrapped
    
    query = None
    name_ = name
    if type(arg) is types.FunctionType:
        return decorated(arg)
    query = arg
    return decorated


class MetaSourceModel(type):
    def __new__(cls, name, bases, dct):
        dct['_iterroles'] = dict((value.name, value)
                                  for key, value in dct.iteritems()
                                  if getattr(value, 'is_iterrole', False))
        return type.__new__(cls, name, bases, dct)


class SourceModel(object):
    __metaclass__ = MetaSourceModel

    def __init__(self, source=None):
        self._source = source

    @property
    def source(self):
        return self._source

    @property
    def _current_row(self):
        return self._rows[self._current_row_n]

    def __iter__(self):
        self._rows = self._create_rows(self.query)
        self._current_row_n = 0
        return self

    def next(self):
        if self._current_row_n + 1 > len(self._rows):
            raise StopIteration

        row_ = {}
        for name, func in self._iterroles.iteritems():
            row_[name] = func(self)

        self._current_row_n += 1
        return row_


class XmlModel(SourceModel):
    def __init__(self, source=None, source_url=None):
        if etree is None:
            raise RuntimeError('XmlModel requires lxml (http://lxml.de/) '
                'package installed.')

        super(XmlModel, self).__init__(source)
        self._set_source_from_url(source_url)
        self._parse()

    def _set_source_from_url(self, source_url):
        if source_url is not None:
            if requests is None:
                raise RuntimeError('Setting source_url requires requests '
                    '(http://docs.python-requests.org/) package installed')
            self._source = requests.get(source_url).content

    def _parse(self):
        self._tree = etree.parse(StringIO(self.source))

    def _create_rows(self, query):
        return self._tree.xpath(query)

    def _get_col(self, query):
        if query is None:
            return ['']
        return self._current_row.xpath(query)


def xpath_property(query):
    def decorated(f):
        @property
        @functools.wraps(f)
        def wrapped(*args, **kwargs):
            self = args[0]
            value = self._tree.xpath(query)[0]
            return f(self, value, *args[1:], **kwargs)

        return wrapped
    
    return decorated



class RssModel(XmlModel):
    query = '//item'

    @xpath_property('//channel/title/text()')
    def title(self, value):
        return value

    @iterrole('link/text()')
    def link(self, value):
        return value

    @iterrole
    def domain(self):
        domain = urlparse(self.link()).netloc
        domain = re.sub(r'^www\.', '', domain)
        return domain
    
    @iterrole('title/text()', name='title')
    def itemtitle(self, value):
        return value

    @iterrole('description/text()')
    def text(self, value):
        return value

    @iterrole('pubDate/text()')
    def pub_date(self, value):
        timestamp = mktime_tz(parsedate_tz(value))
        return datetime.datetime.utcfromtimestamp(timestamp)
