import json
import os

from google.appengine.ext.webapp import template
import webapp2

from commonutil import jsonutil
from contentfetcher import ContentFetcher
from page import pageanalyst

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
        fetchResult = {}
        content = None
        page = None
        fortest = bool(self.request.get('fortest'))
        httpheader = self.request.get('httpheader')
        header = None
        if httpheader:
            header = json.loads(httpheader)
        if url:
            tried = 2 # the max try count is 3
            fetcher = ContentFetcher(url,
                                header=header,
                                tried=tried
                             )
            fetchResult = fetcher.fetch()
            content = fetchResult.get('content')
        if content:
            page = {'url': fetchResult.get('url')}
            if title:
                page['title'] = title
            page = pageanalyst.analyse(page, content, fortest=fortest)
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
            'page': jsonutil.getReadableString(page),
        }
        self._render(templateValues)

