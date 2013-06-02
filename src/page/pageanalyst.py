# coding=utf-8
import lxml

from commonutil import lxmlutil
from . import titleparser
from . import contentparser
from . import paragraphparser
from . import digestparser
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
    if elementResult is not None and titleElement is not None:
        elementResult['element'] = {}
        elementResult['text'] = {}

        elementResult['element']['title'] = (titleElement.tag, titleElement.sourceline)
        elementResult['text']['title'] = lxmlutil.getCleanText(titleElement)

        elementResult['element']['content'] = (contentElement.tag, contentElement.sourceline)
        elementResult['text']['content'] = lxmlutil.getCleanText(contentElement)

    paragraphFormat = editorFormat.get('paragraph', {})
    mainElement, paragraphs = paragraphparser.parse(paragraphFormat, contentElement)
    if paragraphs:
        page['paragraphs'] = paragraphs
        page['content'] = digestparser.parse(paragraphFormat, paragraphs)
    if elementResult is not None and mainElement is not None:
        elementResult['element']['main'] = (mainElement.tag, mainElement.sourceline)
        elementResult['text']['main'] = lxmlutil.getCleanText(mainElement)

    if mainElement is not None:
        publishedFormat = editorFormat.get('published', {})
        publishedElement, published = publishedparser.parse(publishedFormat, titleElement, mainElement)
        if published:
            page['published'] = published
        if elementResult is not None and publishedElement is not None:
            elementResult['element']['published'] = (publishedElement.tag, publishedElement.sourceline)
            if publishedElement is not None:
                elementResult['text']['published'] = lxmlutil.getCleanText(publishedElement)

        images = imgparser.parse(url, contentElement, titleElement, mainElement)
        if images:
            page['images'] = images

    return page

