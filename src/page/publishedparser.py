import logging
import re

from commonutil import lxmlutil

def parse(publishedFormat, titleElement, mainElement):
    if titleElement.sourceline >= mainElement.sourceline:
        return None, None
    published = None
    publishedElement = None
    element = lxmlutil.getFullNext(titleElement)
    while element.sourceline < mainElement.sourceline:
        publishedElement, published = _getPublishedInside(publishedFormat, element)
        if publishedElement is not None:
            break
        element = lxmlutil.getFullNext(element)
    return publishedElement, published

def _getPublishedInside(publishedFormat, element):
    published = None
    publishedElement = None

    if lxmlutil.isVisibleElement(element) and element.text:
        published = _getPublished(publishedFormat, element.text)
    if not published and element.tail:
        published = _getPublished(publishedFormat, element.tail)
    if published:
        publishedElement = element
        return publishedElement, published

    if not lxmlutil.isVisibleElement(element):
        return None, None

    for child in element.iterdescendants():
        if lxmlutil.isVisibleElement(child) and child.text:
            published = _getPublished(publishedFormat, child.text)
        if not published and child.tail:
            published = _getPublished(publishedFormat, child.tail)
        if published:
            publishedElement = child
            break
    return publishedElement, published

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

            day = data.get('day')
            if day and len(day) < 2:
                data['day'] = '0' + day

            hour = data.get('hour')
            if hour:
                if len(hour) < 2:
                    data['hour'] = '0' + hour
            else:
                data['hour'] = '00'

            minute = data.get('minute')
            if minute:
                if len(minute) < 2:
                    data['minute'] = '0' + minute
            else:
                data['minute'] = '00'

            second = data.get('second')
            if second:
                if len(second) < 2:
                    data['second'] = '0' + second
            else:
                data['second'] = '00'

            return format % data

    return None

