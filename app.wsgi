import os.path

import cherrypy

from tuttosport.web.tools.genshitool import GenshiLoader

cherrypy.tools.genshi_template = GenshiLoader(auto_reload=True)

import tuttosport.web.app
application = tuttosport.web.app.App()

cherrypy.config.update({'tools.genshi_template.template_dir': os.path.abspath('tuttosport/web/templates')})

if __name__ == '__main__':
    cherrypy.tree.mount(application, "/static", config={'/': {'tools.staticdir.on': True,
                                                              'tools.staticdir.dir': os.path.abspath('tuttosport/web/static')}})
    cherrypy.quickstart(application)
