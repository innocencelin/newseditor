# coding=utf-8

import logging
import re

import lxml

import globalconfig
from . import contentparser
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

def getSentences(contentFormat, text):
    sentenceContains = contentFormat['sentence'].get('contain')
    suffixStrip = None
    stripFormat = contentFormat.get('filter')
    if stripFormat:
        suffixStrips = stripFormat.get('suffix')
    MIN_SENTENCE = stripFormat.get('length', 10)
    for contain in sentenceContains:
        if contain not in text:
            continue
        sentences = text.split(contain)
        sentences = [sentence + contain for sentence in sentences
                        if sentence and len(sentence) >= MIN_SENTENCE]
        if sentences and suffixStrips:
            lastSentence = sentences[-1]
            for suffixStrip in suffixStrips:
                if re.search(suffixStrip, lastSentence, re.IGNORECASE|re.DOTALL):
                    del sentences[-1]
                    break
        return sentences
    return [text]

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
        page['paragraphs'] = {}
        page['sentences'] = {}
        page['paragraphs']['first'] = paragraphs[0]
        sentences = getSentences(contentFormat, paragraphs[0])
        if sentences:
            page['sentences']['first'] = sentences[0]
        if len(paragraphs) > 1:
            page['paragraphs']['last'] = paragraphs[-1]
            sentences = getSentences(contentFormat, paragraphs[-1])
            if sentences:
                page['sentences']['last'] = sentences[-1]

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

