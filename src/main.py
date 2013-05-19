import webapp2
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'library'))

import webservice.handlers
import webservice.handlersapi

class MainPage(webapp2.RequestHandler):
    def get(self):
        self.response.headers['Content-Type'] = 'text/plain'
        self.response.out.write('Hello, webapp World!')


app = webapp2.WSGIApplication([
('/', MainPage),
('/admin/test/', webservice.handlers.TestPage),
('/api/edit/', webservice.handlersapi.EditRequest),
('/edit/batch/', webservice.handlersapi.BatchEditRequest),
],
                              debug=True)

