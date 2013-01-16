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
            if second and len(second) < 2:
                data['second'] = '0' + second

            return format % data

    return None

class PageAnalyst(object):

    def analyse(self, content, page, separators='', fortest=False):
        published = _getPublished(content)
        if published:
            page['published'] = published
        oldTitle = page.get('title')
        url = page.get('url')
        title = getTitleFromHead(content)
        if not title:
            logging.error('Failed to parse title from head: %s.' % (page, ))
            return page

        if oldTitle and oldTitle in title:
            return page

        if not separators:
            separators = globalconfig.getTitleSeparators()
        mainTitles = getMainTitles(url, separators, title, not fortest)
        bodyContent = getBodyContent(content)
        if not bodyContent:
            logging.error('Failed to get body content: %s.' % (page, ))
            if mainTitles:
                page['title'] = mainTitles[0]
            return page

        if oldTitle:
            bodyTitle = getTitleFromBody(bodyContent, oldTitle)
            if bodyTitle:
                return page

        if mainTitles:
            for mainTitle in mainTitles:
                bodyTitle = getTitleFromBody(bodyContent, mainTitle)
                if bodyTitle and len(bodyTitle) <= len(title):
                    page['title'] = bodyTitle
                    return
            if not oldTitle:
                page['title'] = mainTitles[0]
        else:
            # TODO: how to get a title like element without any tip?
            logging.error('There is no main title in head: %s.' % (page, ))
        return page

