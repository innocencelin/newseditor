import json
import logging
import time
import urllib2

from google.appengine.api import taskqueue

import webapp2

from contentfetcher import ContentFetcher
from page import PageAnalyst

_URL_TIMEOUT = 30
_FETCH_TRYCOUNT = 3
_CALLBACK_TRYCOUNT = 3

def _fetchContent(url, header, triedcount):
    fetcher = ContentFetcher(url, header=header,
                                tried=triedcount)
    _, _, content = fetcher.fetch()
    return content

def _analysePage(oldPage, content):
    analyst = PageAnalyst()
    page = analyst.analyse(content, oldPage)
    return page

def _pushItemsBack(callbackurl, responseData):
    try:
        f = urllib2.urlopen(callbackurl, json.dumps(responseData),
                            timeout=_URL_TIMEOUT)
        f.read()
        f.close()
        return True
    except Exception:
        logging.exception('Failed to post data to "%s".' % (callbackurl, ))
    return False

class EditRequest(webapp2.RequestHandler):
    def post(self):
        rawdata = self.request.body
        taskqueue.add(queue_name="default", payload=rawdata, url='/edit/batch/')
        self.response.headers['Content-Type'] = 'text/plain'
        self.response.out.write('Request is accepted.')

class BatchEditRequest(webapp2.RequestHandler):
    def post(self):
        data = json.loads(self.request.body)
        items = data['items']
        for item in items:
            requestobj = {
                'callbackurl': data['callbackurl'],
                'origin': data['origin'],
                'header': data['header'],
                'page': item,
            }
            rawdata = json.dumps(requestobj)
            taskqueue.add(queue_name="default", payload=rawdata, url='/edit/single/')
        self.response.headers['Content-Type'] = 'text/plain'
        self.response.out.write('Put fetch task into queue.')


class SingleEditResponse(webapp2.RequestHandler):

    def post(self):
        self.response.headers['Content-Type'] = 'text/plain'
        data = json.loads(self.request.body)
        triedcount = data.get('triedcount', 0)
        header = data['header']
        oldPage = data['page']
        url = oldPage['url']
        content = _fetchContent(url, header, triedcount)
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

        page = _analysePage(oldPage, content)

        callbackurl = data['callbackurl']
        responseData = {
                'origin': data['origin'],
                'items': [page],
        }
        doCallback = False
        for i in range(_CALLBACK_TRYCOUNT):
            if _pushItemsBack(callbackurl, responseData):
                doCallback = True
                break
            leftcount = _CALLBACK_TRYCOUNT - 1 - i
            message = 'Failed to push %s back to %s, try count left: %s.' % (
                              url, callbackurl, leftcount)
            logging.info(message)
            self.response.out.write(message)
            if leftcount > 0:
                time.sleep(2)
        if not doCallback:
            return

        message = 'Push %s back to %s.' % (url, callbackurl)
        logging.info(message)
        self.response.out.write(message)

