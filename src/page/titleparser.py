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
        mainTitles.sort(key=lambda k: len(k), reverse=True)
        return mainTitles[0]
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
    for child in bodyElement.iterdescendants():
        if lxmlutil.isVisibleElement(child) and \
            child.text and mainTitle in child.text:
                result.append(child)
    return result

def parse(titleFormat, url, docelement, monitorTitle, fortest):
    headTitle = _getTitleFromHead(docelement)
    mainTitle = None
    if monitorTitle and monitorTitle in headTitle:
        mainTitle = monitorTitle
    else:
        mainTitle = _getMainTitle(titleFormat, url, headTitle, not fortest)
    if not mainTitle:
        return None, []
    titleElements = _getTitleElements(docelement, mainTitle)
    return mainTitle, titleElements

