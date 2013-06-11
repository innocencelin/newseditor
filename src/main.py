import webapp2
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'library'))

import templateutil.filters

import editor.handlers
import editor.handlersapi


config = {}
config['webapp2_extras.jinja2'] = {
    'template_path': os.path.join(os.path.dirname(__file__), 'html', 'templates'),
    'filters': {
        'utc14duration': templateutil.filters.utc14duration,
        'd14format': templateutil.filters.d14format,
        'tojson': templateutil.filters.tojson,
    },
    'environment_args': {
        'extensions': ['jinja2.ext.loopcontrols', 'jinja2.ext.with_'],
    },
}

app = webapp2.WSGIApplication([
('/', editor.handlers.HomePage),
('/page/', editor.handlers.HomePage),
('/image/', editor.handlers.ImageProxy),
('/admin/test/', editor.handlers.TestPage),
('/api/edit/', editor.handlersapi.EditRequest),
('/edit/batch/', editor.handlersapi.BatchEditRequest),
],
debug=os.environ['SERVER_SOFTWARE'].startswith('Dev'), config=config)

