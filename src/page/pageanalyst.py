# coding=utf-8

import logging
import re

import lxml

import globalconfig
from . import contentparser
from . import digestparser
from . import publishedparser
from . import imgparser
from . import titleparser

def getMainElement(contentelement, publishedelement):
    mainelement = None
    parents = []
    parent = contentelement
    while parent is not None:
        parents.append(parent)
        parent = parent.getparent()
    parent = publishedelement
    while parent is not None:
        if parent in parents:
            mainelement = parent
            break
        parent = parent.getparent()
    return mainelement

def analyse(url, content, editorFormat=None, fortest=False):
    if not editorFormat:
        editorFormat = globalconfig.getEditorFormat()
    if not editorFormat:
        logging.error('Failed to load editor format.')
        return
    page = {}
    page['url'] = url
    docelement = lxml.html.fromstring(content)

    MIN_PARAGRAPH_COUNT = 2

    contentFormat = editorFormat.get('content', {})
    contentelement, paragraphs = contentparser.parse(contentFormat, docelement)
    if paragraphs:
        maxContentLength = 100
        # page['p'] = paragraphs
        result = digestparser.parse(contentFormat, paragraphs)
        if result and result.get('paragraphs'):
            page['content'] = result['paragraphs']['first'][:maxContentLength]

    publishedFormat = editorFormat.get('published', {})
    publishedelement = None
    if publishedFormat:
        published = None
        if contentelement is not None and len(paragraphs) >= MIN_PARAGRAPH_COUNT:
            publishedelement, published = publishedparser.parse(publishedFormat, contentelement)
        if published:
            page['published'] = published

    mainelement = None
    if contentelement is not None and publishedelement is not None:
        mainelement = getMainElement(contentelement, publishedelement)

    img = None
    if mainelement is not None:
        img = imgparser.parse(url, mainelement)
    elif contentelement is not None:
        img = imgparser.parse(url, contentelement)
    if img:
        page['img'] = img

    titleelement = None
    title = None
    if mainelement is not None and publishedelement is not None:
        titleelement, title = titleparser.parseByElement(mainelement, publishedelement, content)
        if title:
            page['title'] = title
    if not title:
        titleFormat = editorFormat.get('title', {})
        title = titleparser.parseByText(titleFormat, url, content, fortest)
        if title:
            page['title'] = title
    return page

