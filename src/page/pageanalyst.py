import logging
import re

import lxml
import pyquery

import globalconfig

_PATTERN_MATCH_BODY = re.compile(r'<body[^>]*>(.+)</body>', re.IGNORECASE|re.DOTALL)
_PATTERN_TITLE_IN_HEAD = re.compile(r'<head>.*<title>(.*)</title>.*</head>', re.IGNORECASE|re.DOTALL)

def getMaxSentence(separators, title):
    maxvalue = title
    for separator in separators:
        parts = maxvalue.split(separator)
        maxlen = -1
        maxvalue = None
        for part in parts:
            part = part.strip()
            plen = len(part)
            if plen > maxlen:
                maxlen = plen
                maxvalue = part
    return maxvalue

def getTitle(oldTitle, newTitle):
    if not oldTitle:
        return newTitle
    if not newTitle:
        return oldTitle
    if len(oldTitle) >= len(newTitle):
        return oldTitle
    return newTitle

def getTitleFromDoc(content):
    docelement = lxml.html.fromstring(content)
    docquery = pyquery.PyQuery(docelement)
    title = None
    items = docquery('head title')
    if len(items) > 0:
        title = items[0].text_content()
    return title

def getBodyContent(content):
    m = _PATTERN_MATCH_BODY.search(content)
    if m:
        return m.group(1)
    return content

def getTitileFromBody(bodyContent, sentence):
    pattern = '>([^<>]*%s[^<>]*)<' % (re.escape(sentence), )
    m = re.search(pattern, bodyContent, re.IGNORECASE|re.DOTALL)
    if m:
        return m.group(1)
    return None

def getTitleFromHead(content):
    m = _PATTERN_TITLE_IN_HEAD.search(content)
    if m:
        return m.group(1)
    return None

class PageAnalyst(object):

    def analyse(self, content, page, separators=[]):
        title = getTitleFromHead(content)
        if title:
            if not separators:
                separators = globalconfig.getTitleSeparators()
            maxSentence = getMaxSentence(separators, title)
            bodyContent = getBodyContent(content)
            bodyTitle = getTitileFromBody(bodyContent, maxSentence)
            if bodyTitle and len(bodyTitle) < len(title):
                title = bodyTitle
            else:
                title = maxSentence
            oldTitle = page.get('title')
            page['title'] = getTitle(oldTitle, title)
        return page

