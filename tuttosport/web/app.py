import math
import os.path

import cherrypy
from genshi import Markup

from tuttosport.feedfetcher.db import Db
import tuttosport.feedfetcher.settings as ff_settings


class App(object):
    def __init__(self):
        self.storage = Db(**ff_settings.database)

    def _fix_entry(self, entry):
        entry['text'] = entry['text'].replace(
            'http://vskbandy.se///www.youtube.com/', 'http://youtube.com/')
        entry['text'] = Markup(entry['text'])
        return entry

    def _get_entries(self):
        entries = self.storage.get_entries()
        count = entries.count()
        return count, map(self._fix_entry, entries)

    @cherrypy.expose
    @cherrypy.tools.genshi_template(filename='index.html')
    def index(self, offset='0'):
        try:
            offset = int(offset)
        except ValueError:
            offset = 0
        limit = 10

        count, entries = self._get_entries()
        pages_count = int(math.ceil(count/float(limit)))

        return {'entries': entries[offset:offset+limit], 'pages_count': pages_count,
                'limit': limit}

    @cherrypy.expose
    @cherrypy.tools.genshi_template(filename='rss.xml', method='xml')
    @cherrypy.tools.response_headers(headers=[('Content-Type', 'text/xml')])
    def rss_xml(self):
        _, entries = self._get_entries()
        return {'entries': entries[:10]}

    @cherrypy.expose
    @cherrypy.tools.genshi_template(filename='about.html')
    def about_html(self, offset='0'):
        return {}
