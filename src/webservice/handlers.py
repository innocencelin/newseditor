import json
import os

from google.appengine.ext.webapp import template

import webapp2

from contentfetcher import ContentFetcher
from page import PageAnalyst

class TestPage(webapp2.RequestHandler):

    def _render(self, templateValues):
        self.response.headers['Content-Type'] = 'text/html'
        path = os.path.join(os.path.dirname(__file__), 'templates', 'index.html')
        self.response.out.write(template.render(path, templateValues))

    def get(self):
        templateValues = {
            'fortest': True,
        }
        self._render(templateValues)

    def post(self):
        url = self.request.get('url')
        title = self.request.get('title')
        fortest = bool(self.request.get('fortest'))
        httpheader = self.request.get('httpheader')
        header = None
        if httpheader:
            header = json.loads(httpheader)
        tried = 2 # the max try count is 3
        fetcher = ContentFetcher(url,
                            header=header,
                            tried=tried
                         )
        fetchResult = fetcher.fetch()
        content = fetchResult.get('content')
        page = None
        if content:
            page = {'url': fetchResult.get('url'), 'title': title}
            analyst = PageAnalyst()
            analyst.analyse(content, page, fortest=fortest)
        if header:
            httpheader = jsonutil.getReadableString(header)
        templateValues = {
            'url': url,
            'title': title,
            'fortest': fortest,
            'httpheader': httpheader,
            'encoding': fetchResult.get('encoding'),
            'encodingSrc': fetchResult.get('encoding.src'),
            'oldContent': fetchResult.get('content.old'),
            'content': fetchResult.get('content'),
            'page': page,
        }
        self._render(templateValues)

