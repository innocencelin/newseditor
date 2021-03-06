import logging

import pyquery

from commonutil import lxmlutil
from . import modelapi

def _getMainTitle(titleFormat, url, title, sideEffect):
    separators = titleFormat.get('separator')
    useparator = separators[0]
    for separator in separators[1:]:
        title = title.replace(separator, useparator)
    parts = title.split(useparator)
    mainTitles = []
    for part in parts:
        part = part.strip()
        if not modelapi.isConstantTitle(titleFormat, url, part, sideEffect):
            mainTitles.append(part)
    if mainTitles:
        return max(mainTitles, key=lambda k: len(k))
    elif parts:
        return max(parts, key=lambda k: len(k))
    return None

def _getTitleFromHead(docelement):
    items = pyquery.PyQuery(docelement)('head title')
    title = None
    if items:
        title = items[0].text_content()
    if title:
        title = title.strip()
    return title

def _getTitleElements(docelement, mainTitle):
    items = pyquery.PyQuery(docelement)('body')
    if not items:
        return []
    bodyElement = items[0]
    result = []
    textFunc = tailFunc = lambda text: text and mainTitle in text
    lxmlutil.findAllVisibleMatched(result, bodyElement, textFunc, tailFunc)
    return result

def parse(titleFormat, url, docelement, monitorTitle, fortest):
    headTitle = _getTitleFromHead(docelement)
    if not headTitle:
        return None, []
    mainTitle = None
    if monitorTitle and monitorTitle in headTitle:
        mainTitle = monitorTitle
    else:
        mainTitle = _getMainTitle(titleFormat, url, headTitle, not fortest)
    if not mainTitle:
        return None, []
    titleElements = _getTitleElements(docelement, mainTitle)
    return mainTitle, titleElements

