import logging
import re

from commonutil import lxmlutil
import lxml.html

def parseByElement(publishedFormat, contentelement):
    published = None
    publishedelement = None
    # publishedelement, published = _getPublishedInside(publishedFormat, contentelement)
    if not published:
        publishedelement, published = _getPublishedBefore(publishedFormat, contentelement)
    return publishedelement, published

def parseByText(publishedFormat, content):
    return _getPublished(publishedFormat, content)

def _getPublishedInside(publishedFormat, contentelement):
    published = None
    publishedelement = None
    text = contentelement.text
    if text:
        published = _getPublished(publishedFormat, text)
    if published:
        publishedelement = contentelement
        return publishedelement, published
    for child in contentelement.iterdescendants():
        if lxmlutil.isVisibleElement(child):
            text = child.text
            if text:
                published = _getPublished(publishedFormat, text)
            if published:
                publishedelement = child
                break
        text = child.tail
        if text:
            published = _getPublished(publishedFormat, text)
        if published:
            publishedelement = child
            break
    return publishedelement, published

def _getPublishedBefore(publishedFormat, contentelement):
    published = None
    publishedelement = None
    previous = contentelement
    while True:
        previous = lxmlutil.getFullPrevious(previous)
        if previous is None:
            break
        if lxmlutil.isVisibleElement(previous):
            text = previous.text_content()
            if text:
                published = _getPublished(publishedFormat, text)
        if published:
            # get the deepest element which has published data.
            publishedelement, published = _getPublishedInside(publishedFormat, previous)
            break
        if not published:
            text = previous.tail
            if text:
                published = _getPublished(publishedFormat, text)
            if published:
                publishedelement = previous
                break
    return publishedelement, published

def _getPublished(publishedFormat, content):
    publishedPatterns = publishedFormat.get('patterns')
    for publishedPattern in publishedPatterns:
        pattern = publishedPattern.get('pattern')
        format = publishedPattern.get('format')
        if not pattern or not format:
            continue

        m = re.search(pattern, content)
        if m:
            data = m.groupdict()

            month = data.get('month')
            if month and len(month) < 2:
                data['month'] = '0' + month

            hour = data.get('hour')
            if hour and len(hour) < 2:
                data['hour'] = '0' + hour

            minute = data.get('minute')
            if minute and len(minute) < 2:
                data['minute'] = '0' + minute

            second = data.get('second')
            if second:
                if len(second) < 2:
                    data['second'] = '0' + second
            else:
                data['second'] = '00'
            return format % data

    return None

