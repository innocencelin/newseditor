import logging
import re

import lxml
import pyquery

import globalconfig

_PATTERN_MATCH_BODY = re.compile(r'<body[^>]*>(.+)</body>', re.IGNORECASE|re.DOTALL)
_PATTERN_TITLE_IN_HEAD = re.compile(r'<head[^>]*>.*<title[^>]*>(.*)</title>.*</head>', re.IGNORECASE|re.DOTALL)

def getTitleParts(separators, title):
    result = []
    useparator = separators[0]
    for separator in separators[1:]:
        title = title.replace(separator, useparator)
    parts = title.split(useparator)
    for part in parts:
        part = part.strip()
        plen = len(part)
        result.append({'l': len(part), 'v': part})
    result.sort(key=lambda k: k['l'], reverse=True)
    return result[:2]

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
    minlen = 0
    minvalue = None
    slen = len(sentence)
    for m in re.finditer(pattern, bodyContent, re.IGNORECASE|re.DOTALL):
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
    return minvalue

def getTitleFromHead(content):
    m = _PATTERN_TITLE_IN_HEAD.search(content)
    if m:
        return m.group(1)
    return None

class PageAnalyst(object):

    def analyse(self, content, page, separators=''):
        oldTitle = page.get('title')
        title = getTitleFromHead(content)
        if title:
            if oldTitle and oldTitle in title:
                return page
            if not separators:
                separators = globalconfig.getTitleSeparators()
            found = False
            if oldTitle:
                halfLen = len(oldTitle) / 2
            else:
                halfLen = 0
            bodyContent = getBodyContent(content)
            titleParts = getTitleParts(separators, title)
            for titlePart in titleParts:
                bodyTitle = getTitileFromBody(bodyContent, titlePart['v'])
                if bodyTitle and len(bodyTitle) > halfLen:
                    page['title'] = bodyTitle
                    found = True
                    break
            if not found:
                page['title'] = getTitle(oldTitle, titleParts[0]['v'])
        else:
            logging.error('Failed to parse title from head: %s.' % (page, ))
        return page

