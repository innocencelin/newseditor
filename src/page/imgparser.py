import logging
import urllib2
import urlparse

from google.appengine.api.images import Image

import pyquery

from commonutil import numberutil

_MIN_WIDTH = 100
_MIN_HEIGHT = 100

def _fetchImageSize(imgurl):
    try:
        response = urllib2.urlopen(imgurl)
        data = response.read()
        image = Image(data)
        return image.width, image.height
    except Exception:
        logging.info('Failed to fetch iamge: %s.' % (imgurl,))
    return None, None

def parse(url, mainelement):
    items = pyquery.PyQuery(mainelement)('img')
    for item in items:
        img = {}
        imgurl = item.get('src')
        if imgurl:
            imgurl = urlparse.urljoin(url, imgurl)
            img['url'] = imgurl
        imgwidth = item.get('width')
        if imgwidth:
            imgwidth = numberutil.parseInt(imgwidth)
        imgheight = item.get('height')
        if imgheight:
            imgheight = numberutil.parseInt(imgheight)
        if not imgwidth or not imgheight:
            imgwidth, imgheight = _fetchImageSize(imgurl)
        if not imgwidth or not imgheight:
            continue
        if imgwidth < _MIN_WIDTH or imgheight < _MIN_HEIGHT:
            continue
        img['width'] = imgwidth
        img['height'] = imgheight
        return img

    return None

