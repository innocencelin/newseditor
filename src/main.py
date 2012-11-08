import webapp2
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'library'))

import configmanager.handlers

import webservice.handlers

class MainPage(webapp2.RequestHandler):
    def get(self):
        self.response.headers['Content-Type'] = 'text/plain'
        self.response.out.write('Hello, webapp World!')


app = webapp2.WSGIApplication([
('/', MainPage),
('/configitem', configmanager.handlers.MainPage),
('/admin/editor/test/', webservice.handlers.TestPage),
],
                              debug=True)

