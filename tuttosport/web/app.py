import math
import os.path

import cherrypy
from genshi import Markup

from tuttosport.feedfetcher.db import Db
import tuttosport.feedfetcher.settings as ff_settings



print cherrypy.config
class App(object):
    def __init__(self):
        self.storage = Db(**ff_settings.database)

    @cherrypy.expose
    @cherrypy.tools.genshi_template(filename='index.html')
    def index(self, offset='0'):
        def markup_text(entry):
            entry['text'] = entry['text'].replace(
                'http://vskbandy.se///www.youtube.com/', 'http://youtube.com/')
            entry['text'] = Markup(entry['text'])
            return entry

        try:
            offset = int(offset)
        except ValueError:
            offset = 0
        limit = 10

        entries = self.storage.get_entries()
        count = entries.count()
        pages_count = int(math.ceil(count/float(limit)))
        entries = map(markup_text, entries)

        return {'entries': entries[offset:offset+limit], 'pages_count': pages_count,
                'limit': limit}

    @cherrypy.expose
    @cherrypy.tools.genshi_template(filename='about.html')
    def about_html(self, offset='0'):
        return {}
