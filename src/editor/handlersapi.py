import json
import logging

from google.appengine.api import taskqueue

import webapp2

from commonutil import networkutil
from contentfetcher import ContentFetcher
from page import pageanalyst
from . import globalconfig

_URL_TIMEOUT = 30
_CALLBACK_TRYCOUNT = 3

class EditRequest(webapp2.RequestHandler):
    def post(self):
        data = json.loads(self.request.body)
        uuid = data.get('uuid')
        if networkutil.isUuidHandled(uuid):
            message = 'BatchEditRequest: %s is already handled.' % (uuid, )
            logging.warn(message)
            self.response.out.write(message)
            return
        networkutil.updateUuids(uuid)

        rawdata = self.request.body
        taskqueue.add(queue_name="default", payload=rawdata, url='/edit/batch/')
        self.response.headers['Content-Type'] = 'text/plain'
        self.response.out.write('Request is accepted.')

class BatchEditRequest(webapp2.RequestHandler):
    def post(self):
        data = json.loads(self.request.body)

        items = data['items']

        header = data.get('header')
        for item in items:
            url = item.get('url')
            if not url:
                continue
            fetcher = ContentFetcher(url, header=header,
                                        tried=2)
            fetchResult = fetcher.fetch()
            usedUrl = fetchResult.get('url')
            content = fetchResult.get('content')
            if not content:
                logging.error('Failed to get content from %s.' % (url, ))
                continue
            item['url'] = usedUrl
            try:
                editorFormat = globalconfig.getEditorFormat()
                page = pageanalyst.analyse(usedUrl, content,
                            editorFormat=editorFormat, monitorTitle=item.get('title'))
                if not item.get('title') and page.get('title'):
                    item['title'] = page['title']
                if not item.get('content') and page.get('content'):
                    item['content'] = page['content']
                if not item.get('img') and page.get('images'):
                    item['img'] = page['images'][0]
            except Exception:
                logging.exception('Error happens when analyse %s.' % (usedUrl, ))

        responseData = {
                'origin': data['origin'],
                'items': items,
        }

        self.response.headers['Content-Type'] = 'text/plain'
        callbackurl = data['callbackurl']
        success = networkutil.postData(callbackurl, responseData,
                    trycount=_CALLBACK_TRYCOUNT, timeout=_URL_TIMEOUT)

        if success:
            message = 'Push items back for %s to %s.' % (data['origin'], callbackurl)
        else:
            message = 'Failed to push items back for %s to %s.' % (data['origin'], callbackurl)
        logging.info(message)
        self.response.out.write(message)

