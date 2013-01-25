# coding=utf-8

import logging
import re

import lxml
import pyquery

import globalconfig

_PATTERN_MATCH_BODY = re.compile(r'<body[^>]*>(.+)</body>', re.IGNORECASE|re.DOTALL)
_PATTERN_TITLE_IN_HEAD = re.compile(r'<head[^>]*>.*<title[^>]*>(.*)</title>.*</head>', re.IGNORECASE|re.DOTALL)

def getMainTitles(url, separators, title, sideEffect):
    useparator = separators[0]
    for separator in separators[1:]:
        title = title.replace(separator, useparator)
    parts = title.split(useparator)
    mainTitles = []
    for part in parts:
        part = part.strip()
        if not globalconfig.isConstantTitle(url, part, sideEffect):
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
    if minvalue:
        pattern = '[^\\n]*%s[^\\n]*' % (re.escape(sentence), )
        m = re.search(pattern, minvalue, re.IGNORECASE|re.DOTALL)
        if m:
            minvalue = m.group(0).strip()
    return minvalue

def _getPublished(content):
    publishedFormats = globalconfig.getPublishedFormats()
    for publishedFormat in publishedFormats:
        pattern = publishedFormat.get('pattern')
        format = publishedFormat.get('format')
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

def _getTitle(url, content, separators, fortest):
    headTitle = getTitleFromHead(content)
    if not headTitle:
        logging.error('Failed to parse title from head: %s.' % (page, ))
        return

    if not separators:
        separators = globalconfig.getTitleSeparators()
    mainTitles = getMainTitles(url, separators, headTitle, not fortest)

    if not mainTitles:
        return headTitle

    bodyContent = getBodyContent(content)
    if not bodyContent:
        logging.error('Failed to get body content: %s.' % (page, ))
        return mainTitles[0]

    for mainTitle in mainTitles:
        bodyTitle = getTitleFromBody(bodyContent, mainTitle)
        if bodyTitle and len(bodyTitle) <= len(headTitle):
            return bodyTitle
    return mainTitles[0]


def _getMainScope(docelement):
    docquery = pyquery.PyQuery(docelement)
    title = None
    items = docquery('p')
    result = {}
    for item in items:
        text = item.text_content()
        if not text:
            continue
        parent = item.getparent()
        size = result.get(parent)
        if size:
            result[parent] += len(text)
        else:
            result[parent] = len(text)
    maxsize = 0
    maxparent = None
    for parent, size in result.items():
        if size > maxsize:
            maxsize = size
            maxparent = parent
    if maxparent:
        mainstart = maxparent.sourceline
        next = maxparent.getnext()
        if next:
            mainend = next.sourceline
        else:
            mainend = -1
        return mainstart, mainend
    return None, None

def _getParagraphs(content, sentenceFormat):
    if not sentenceFormat:
        sentenceFormat = globalconfig.getSentenceFormat()
    docelement = lxml.html.fromstring(content)
    mainstart, mainend = _getMainScope(docelement)
    if not mainstart:
        return None
    docquery = pyquery.PyQuery(docelement)
    title = None
    items = docquery('p')
    result = []
    sentenceEnds = sentenceFormat.get('end')
    sentenceContains = sentenceFormat.get('contain')
    for item in items:
        if item.sourceline < mainstart or (mainend > 0 and item.sourceline > mainend):
            continue
        text = item.text_content()
        if text:
            text = text.strip()
        if not text:
            continue
        lastCharacter = text[-1]
        if lastCharacter in sentenceFormat:
            result.append(text)
            continue
        for sentenceContain in sentenceContains:
            if sentenceContain in text:
                result.append(text)
                break
    return result

class PageAnalyst(object):

    def analyse(self, content, page, separators='', sentenceFormat=None, fortest=False):
        published = _getPublished(content)
        if published:
            page['published'] = published
        url = page.get('url')
        title = _getTitle(url, content, separators, fortest)
        if title:
            page['title2'] = title
        paragraphs = _getParagraphs(content, sentenceFormat)
        if paragraphs:
            page['first'] = paragraphs[0]
            if len(paragraphs) > 1:
                page['last'] = paragraphs[-1]
        return page

