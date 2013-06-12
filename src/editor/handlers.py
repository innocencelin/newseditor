import base64
import json
import os
import urllib
import urllib2
import urlparse

from google.appengine.api import memcache

from commonutil import jsonutil, stringutil
from contentfetcher import ContentFetcher

from templateutil.handlers import BasicHandler

from page import pageanalyst
from . import globalconfig


class MyHandler(BasicHandler):

    def prepareBaseValues(self):
        self.site = globalconfig.getSiteConfig()
        self.i18n = globalconfig.getI18N()

class ImageProxy(BasicHandler):

    def get(self):
        url = self.request.get('url')
        if not url:
            return
        path = urlparse.urlparse(url).path
        ext = os.path.splitext(path)[1]
        if ext:
            contentType = 'image/%s' % (str(ext)[1:], )
        else:
            contentType = 'image/jpeg'
        self.response.headers['Content-Type'] = contentType
        key = stringutil.calculateHash([url])
        content = memcache.get(key)
        if not content:
            res = urllib2.urlopen(url)
            content = res.read()
            res.close()
            if content:
                memcache.set(key, content)
        self.response.out.write(content)

class HomePage(MyHandler):

    def get(self):
        url = self.request.get('url')
        page = None
        if url:
            try:
                url = base64.b64decode(url)
                url2 = ''
                length = len(url)
                for i in range(0, length, 2):
                    if i + 1 < length:
                        url2 += url[i+1] + url[i]
                if length % 2 != 0:
                    url2 += url[-1]
                url = url2
            except TypeError:
                pass
            key = stringutil.calculateHash([url])
            page = memcache.get(key)
            contentGot = bool(page)
            if not page:
                tried = 2 # the max try count is 3
                fetcher = ContentFetcher(url, tried=tried)
                fetchResult = fetcher.fetch()
                content = fetchResult.get('content')
                if content:
                    editorFormat = globalconfig.getEditorFormat()
                    page = pageanalyst.analyse(url, content, editorFormat=editorFormat)
                    if page:
                        page['url'] = url
                    if page and (page.get('content') or page.get('images')):
                        memcache.set(key, page)
                        contentGot = True
        if not contentGot:
            page = {'url': url}
            self.redirect(url, permanent=True)
            return
        if 'images' in page:
            for image in page['images']:
                image['url'] = '/image/?url=' + urllib.quote(image['url'].encode('utf-8'))
        templateValues = {
            'page': page,
        }
        self.render(templateValues, 'home.html')

class TestPage(MyHandler):
    def get(self):
        url = self.request.get('url')
        templateValues = {
            'fortest': True,
            'url': url,
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

