import json
import logging

from google.appengine.api import taskqueue

import webapp2

from commonutil import networkutil
from contentfetcher import ContentFetcher
from page import pageanalyst

_URL_TIMEOUT = 30
_FETCH_TRYCOUNT = 3
_CALLBACK_TRYCOUNT = 3

class EditRequest(webapp2.RequestHandler):
    def post(self):
        rawdata = self.request.body
        taskqueue.add(queue_name="default", payload=rawdata, url='/edit/batch/')
        self.response.headers['Content-Type'] = 'text/plain'
        self.response.out.write('Request is accepted.')

class BatchEditRequest(webapp2.RequestHandler):
    def post(self):
        data = json.loads(self.request.body)

        uuid = data.get('uuid')
        if networkutil.isUuidHandled(uuid):
            message = 'BatchEditRequest: %s is already handled.' % (uuid, )
            logging.warn(message)
            self.response.out.write(message)
            return
        networkutil.updateUuids(uuid)

        items = data['items']

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


class SingleEditResponse(webapp2.RequestHandler):

    def post(self):
        self.response.headers['Content-Type'] = 'text/plain'
        data = json.loads(self.request.body)
        triedcount = data.get('triedcount', 0)
        header = data.get('header')
        page = data['page']
        editedPage = None
        url = page.get('url')

        if url:
            fetcher = ContentFetcher(url, header=header,
                                        tried=triedcount)
            fetchResult = fetcher.fetch()
            usedUrl = fetchResult.get('url')
            content = fetchResult.get('content')
            if not content:
                triedcount += 1
                leftcount = _FETCH_TRYCOUNT - triedcount
                message = 'Failed to fetch content form %s, lefted: %s.' % (
                            url, leftcount, )
                logging.error(message)
                self.response.out.write(message)
                if leftcount > 0:
                    data['triedcount'] = triedcount
                    taskqueue.add(queue_name="default", payload=json.dumps(data),
                                url='/edit/single/')
                    return
            if content:
                page['url'] = usedUrl
                try:
                    editedPage = pageanalyst.analyse(usedUrl, content)
                except Exception:
                    logging.exception('Error happens when analyse %s.' % (usedUrl, ))
        else:
            message = 'No url in data: %s.' % (data, )
            logging.error(message)
            self.response.out.write(message)

        callbackurl = data['callbackurl']
        # Make sure monitor and editor will not be None.
        responseData = {
                'origin': data['origin'],
                'items': [{
                            'monitor': page or {},
                            'editor': editedPage or {},
                            }],
        }

        success = networkutil.postData(callbackurl, responseData, tag=url,
                    trycount=_CALLBACK_TRYCOUNT, timeout=_URL_TIMEOUT)

        if success:
            message = 'Push items back for %s to %s.' % (url, callbackurl)
        else:
            message = 'Failed to push items back for %s to %s.' % (url, callbackurl)
        logging.info(message)
        self.response.out.write(message)

