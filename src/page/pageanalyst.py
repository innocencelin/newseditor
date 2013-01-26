# coding=utf-8

import logging

import lxml

import globalconfig
from . import contentparser
from . import publishedparser
from . import mainparser
from . import imgparser
from . import titleparser

def analyse(originalPage, content, editorFormat=None, fortest=False):
    if not editorFormat:
        editorFormat = globalconfig.getEditorFormat()
    if not editorFormat:
        logging.error('Failed to load editor format.')
        return

    url = originalPage.get('url')
    page = {}
    pagePositions = {}
    docelement = lxml.html.fromstring(content)


    sentenceFormat = editorFormat.get('sentence', {})
    paragraphs = contentparser.parse(docelement, pagePositions, sentenceFormat)
    if paragraphs:
        page['first'] = paragraphs[0]
        if len(paragraphs) > 1:
            page['last'] = paragraphs[-1]

    publishedFormat = editorFormat.get('published', {})
    if publishedFormat:
        published = publishedparser.parse(publishedFormat, pagePositions, content)
        if published:
            page['published'] = published

    mainparser.parse(pagePositions)

    img = imgparser.parse(url, pagePositions)
    if img:
        page['img'] = img

    titleFormat = editorFormat.get('title', {})
    title = titleparser.parse(titleFormat,pagePositions, url, content, fortest)
    if title:
        page['title'] = title
    page['url'] = url
    return page

