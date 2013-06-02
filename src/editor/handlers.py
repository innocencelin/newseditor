import json
import os


from commonutil import jsonutil
from contentfetcher import ContentFetcher

from templateutil.handlers import BasicHandler

from page import pageanalyst
from . import globalconfig


class MyHandler(BasicHandler):

    def prepareBaseValues(self):
        self.site = globalconfig.getSiteConfig()
        self.i18n = globalconfig.getI18N()

class HomePage(MyHandler):

    def get(self):
        url = self.request.get('url')
        page = {'url': url}
        if url:
            tried = 2 # the max try count is 3
            fetcher = ContentFetcher(url, tried=tried)
            fetchResult = fetcher.fetch()
            content = fetchResult.get('content')
            if content:
                editorFormat = globalconfig.getEditorFormat()
                page = pageanalyst.analyse(url, content, editorFormat=editorFormat)
        templateValues = {
            'page': page,
        }
        self.render(templateValues, 'home.html')

class TestPage(MyHandler):
    def get(self):
        templateValues = {
            'fortest': True,
        }
        self.render(templateValues, 'test.html')

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
        elementResult = {}
        if content:
            editorFormat = globalconfig.getEditorFormat()
            page = pageanalyst.analyse(url, content, editorFormat=editorFormat,
                                monitorTitle=title, fortest=fortest, elementResult=elementResult)
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
            'pagestr': jsonutil.getReadableString(page),
            'page': page,
            'elementResult': elementResult,
        }
        self.render(templateValues, 'test.html')

