import logging
import re

from commonutil import lxmlutil
import lxml.html

def parse(publishedFormat, pagePositions, content):
    contentelement = pagePositions.get('contentelement')
    if contentelement is not None:
        published = _getPublishedInside(publishedFormat, contentelement, pagePositions)
        if not published:
            published = _getPublishedBefore(publishedFormat, contentelement, pagePositions)
    else:
        published = _getPublished(publishedFormat, content)
    return published

def _getPublishedInside(publishedFormat, contentelement, pagePositions):
    published = None
    text = contentelement.text
    if text:
        published = _getPublished(publishedFormat, text)
    if published:
        pagePositions['publishedelement'] = contentelement
        return
    for child in contentelement.iterdescendants():
        text = child.text
        if text:
            published = _getPublished(publishedFormat, text)
        if published:
            pagePositions['publishedelement'] = child
            break
        text = child.tail
        if text:
            published = _getPublished(publishedFormat, text)
        if published:
            pagePositions['publishedelement'] = child
            break
    return published

def _getPublishedBefore(publishedFormat, contentelement, pagePositions):
    published = None
    previous = contentelement
    while True:
        previous = lxmlutil.getFullPrevious(previous)
        if previous is None:
            break
        if isinstance(previous, lxml.html.HtmlComment):
            continue
        if isinstance(previous, lxml.html.HtmlElement) and \
                previous.tag == 'script':
            continue
        text = previous.text_content()
        published = _getPublished(publishedFormat, text)
        if published:
            # get the deepest element which has published data.
            _getPublishedInside(publishedFormat, previous, pagePositions)
            break
    return published

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

