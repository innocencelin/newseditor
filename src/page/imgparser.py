import logging
import urllib2
import urlparse

from google.appengine.api.images import Image

import pyquery

from commonutil import lxmlutil, numberutil

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

def _getNextText(element):
    while element is not None:
        if lxmlutil.isVisibleElement(element) and element.text:
            return element.text.strip()
        elif element.tail:
            return element.tail.strip()
        element = lxmlutil.getFullNext(element)
    return None

def _getImgTitle(element):
    alt = element.get('alt')
    if alt:
        return alt
    nextTitle = _getNextText(element)
    nextMaxLength = 30
    if nextTitle and len(nextTitle) <= nextMaxLength:
        return nextTitle
    return None

def _parseImg(url, imgElement):
    img = {}
    imgurl = imgElement.get('src')
    if not imgurl:
        return None
    imgurl = urlparse.urljoin(url, imgurl)
    img['url'] = imgurl
    imgwidth = imgElement.get('width')
    if imgwidth:
        imgwidth = numberutil.parseInt(imgwidth)
    imgheight = imgElement.get('height')
    if imgheight:
        imgheight = numberutil.parseInt(imgheight)
    if not imgwidth or not imgheight:
        imgwidth, imgheight = _fetchImageSize(imgurl)
    if not imgwidth or not imgheight:
        return None
    if imgwidth < _MIN_WIDTH or imgheight < _MIN_HEIGHT:
        return None
    imgTitle = _getImgTitle(imgElement)
    if imgTitle:
        img['title'] = imgTitle
    img['width'] = imgwidth
    img['height'] = imgheight
    return img

def parse(url, contentElement, titleElement, mainElement):
    startLine = titleElement.sourceline
    mainNext = lxmlutil.getFullNext(mainElement)
    if mainNext is None:
        endLine = -1
    else:
        endLine = mainNext.sourceline
    items = pyquery.PyQuery(contentElement)('img')
    result = []
    for item in items:
        if item.sourceline < startLine:
            continue
        if endLine > 0 and item.sourceline > endLine:
            break
        img = _parseImg(url, item)
        if img:
            result.append(img)

    return result

