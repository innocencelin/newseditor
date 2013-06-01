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

        images = imgparser.parse(url, contentElement, titleElement, mainElement)
        if images:
            page['images'] = images

    return page

