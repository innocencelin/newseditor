# coding=utf-8

import logging
import re

import lxml

from commonutil import lxmlutil
from . import titleparser
from . import contentparser
from . import paragraphparser
from . import publishedparser
from . import imgparser

def analyse(url, content, editorFormat, monitorTitle=None, fortest=False, elementResult={}):
    page = {}
    docelement = lxml.html.fromstring(content)

    titleFormat = editorFormat.get('title', {})
    title, titleeEements = titleparser.parse(titleFormat, url, docelement, monitorTitle, fortest)
    if not titleeEements:
        return page
    page['title'] = title
    if elementResult is not None:
        elementResult['titles'] = titleeEements

    page['url'] = url
    titleElement, contentElement = contentparser.parse(titleeEements)
    if elementResult is not None:
        elementResult['element'] = {}
        elementResult['text'] = {}

        elementResult['element']['title'] = titleElement
        elementResult['text']['title'] = lxmlutil.getCleanText(titleElement)

        elementResult['element']['content'] = contentElement
        elementResult['text']['content'] = lxmlutil.getCleanText(contentElement)

    mainElement, paragraphs = paragraphparser.parse(contentElement)
    page['paragraphs'] = paragraphs
    if elementResult is not None:
        elementResult['element']['main'] = mainElement
        elementResult['text']['main'] = lxmlutil.getCleanText(mainElement)

    if mainElement is not None:
        publishedFormat = editorFormat.get('published', {})
        publishedElement, published = publishedparser.parse(publishedFormat, titleElement, mainElement)
        if published:
            page['published'] = published
        if elementResult is not None:
            elementResult['element']['published'] = publishedElement
            if publishedElement is not None:
                elementResult['text']['published'] = lxmlutil.getCleanText(publishedElement)

    _ = """
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
        if contentElement is not None and len(paragraphs) >= MIN_PARAGRAPH_COUNT:
            publishedelement, published = publishedparser.parse(publishedFormat, contentElement)
        if published:
            page['published'] = published

    mainelement = None
    if contentElement is not None and publishedelement is not None:
        mainelement = getMainElement(contentElement, publishedelement)

    img = None
    if mainelement is not None:
        img = imgparser.parse(url, mainelement)
    elif contentElement is not None:
        img = imgparser.parse(url, contentElement)
    if img:
        page['img'] = img
"""
    return page

