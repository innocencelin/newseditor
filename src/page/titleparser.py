import logging
import re

import lxml.html

from commonutil import lxmlutil
from . import modelapi

_PATTERN_MATCH_BODY = re.compile(r'<body[^>]*>(.+)</body>', re.IGNORECASE|re.DOTALL)
_PATTERN_TITLE_IN_HEAD = re.compile(r'<head[^>]*>.*<title[^>]*>(.*)</title>.*</head>', re.IGNORECASE|re.DOTALL)

def parseByText(titleFormat, url, content, fortest):
    headTitle = getTitleFromHead(content)
    if not headTitle:
        logging.error('Failed to parse title from head: %s.' % (url, ))
        return

    if not titleFormat:
        return headTitle

    mainTitles = getMainTitles(titleFormat, url, headTitle, not fortest)

    if not mainTitles:
        return headTitle

    bodyContent = getBodyContent(content)
    if not bodyContent:
        logging.error('Failed to get body content: %s.' % (url, ))
        return mainTitles[0]

    for mainTitle in mainTitles:
        bodyTitle = getTitleFromBody(bodyContent, mainTitle)
        if bodyTitle and len(bodyTitle) <= len(headTitle):
            return bodyTitle
    return mainTitles[0]

def getMainTitles(titleFormat, url, title, sideEffect):
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
    mainTitles.sort(key=lambda k: len(k), reverse=True)
    return mainTitles[:2]

def getTitleFromDoc(content):
    docelement = lxml.html.fromstring(content)
    docquery = pyquery.PyQuery(docelement)
    title = None
    items = docquery('head title')
    if items:
        title = items[0].text_content()
    return title

def getTitleFromHead(content):
    m = _PATTERN_TITLE_IN_HEAD.search(content)
    if m:
        return m.group(1)
    return None

def getBodyContent(content):
    m = _PATTERN_MATCH_BODY.search(content)
    if m:
        return m.group(1)
    return None

def getTitleFromBody(bodyContent, sentence):
    pattern = '>([^<>]*%s[^<>]*)<' % (re.escape(sentence), )
    minlen = 0
    minvalue = None
    slen = len(sentence)
    maxTitlePosition = len(bodyContent) * 3 / 4
    for m in re.finditer(pattern, bodyContent, re.IGNORECASE|re.DOTALL):
        if m.start() > maxTitlePosition:
            break
        value = m.group(1).strip()
        if not minvalue:
            minvalue = value
            minlen = len(value)
        else:
            vlen = len(value)
            if vlen < minlen:
                minlen = vlen
                minvalue = value
        if minlen == slen:
            break
    if minvalue:
        pattern = '[^\\n]*%s[^\\n]*' % (re.escape(sentence), )
        m = re.search(pattern, minvalue, re.IGNORECASE|re.DOTALL)
        if m:
            minvalue = m.group(0).strip()
    return minvalue

def parseByElement(mainelement, publishedelement, content):
    maxtitle = None
    titleelement = None
    text = mainelement.text
    if text:
        text = text.strip()
    if text:
        maxlen = len(text)
        maxelement = mainelement
        maxtitle = text
    else:
        maxlen = 0
        maxelement = None
        maxtitle = None

    publishedBlockParent = lxmlutil.getBlockParent(publishedelement)
    for child in mainelement.iterdescendants():
        if child == publishedBlockParent:
            break
        if lxmlutil.isVisibleElement(child):
            text = child.text
            if text:
                text = text.strip()
            if text and len(text) > maxlen:
                maxlen = len(text)
                maxelement = child
                maxtitle = text

        text = child.tail
        if text:
            text = text.strip()
        if text and len(text) > maxlen:
            maxlen = len(text)
            maxelement = child
            maxtitle = text

    if maxelement is not None:
        titleelement = maxelement
    headTitle = getTitleFromHead(content)
    if maxtitle and headTitle and len(maxtitle) > len(headTitle):
        return None, None
    return titleelement, maxtitle

