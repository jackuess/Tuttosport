from urllib import quote

import cherrypy
from genshi.template import Context, TemplateLoader

class GenshiHandler():
    def __init__(self, template, next_handler, method):
        self.template = template
        self.next_handler = next_handler
        self.method = method
        
    def __call__(self):
        context = Context(url=cherrypy.url, quote=quote)
        context.push(self.next_handler())
        stream = self.template.generate(context)
        return stream.render(self.method)

class GenshiLoader(cherrypy.Tool):
    def __init__(self, auto_reload=False):
        self.loader = TemplateLoader(auto_reload=auto_reload)
        super(GenshiLoader, self).__init__(point="before_handler",
                                           callable=self.callable)

    def callable(self, filename, method='xhtml', template_dir=None):
        if not template_dir.endswith('/'):
            template_dir += '/'
        template = self.loader.load(filename, relative_to=template_dir)
        cherrypy.request.handler = GenshiHandler(
            template, cherrypy.request.handler, method)
    