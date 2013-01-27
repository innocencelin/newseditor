# coding=utf-8

import logging

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

def getSentences(sentenceFormat, text):
    sentenceContains = sentenceFormat.get('contain')
    MIN_SENTENCE = 4
    for contain in sentenceContains:
        if contain not in text:
            continue
        sentences = text.split(contain)
        sentences = [sentence + contain for sentence in sentences
                        if sentence and len(sentence) >= MIN_SENTENCE]
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

    sentenceFormat = editorFormat.get('sentence', {})
    contentelement, paragraphs = contentparser.parse(sentenceFormat, docelement)
    if paragraphs:
        page['paragraphs'] = {}
        page['sentences'] = {}
        page['paragraphs']['first'] = paragraphs[0]
        page['sentences']['first'] = getSentences(sentenceFormat, paragraphs[0])[0]
        if len(paragraphs) > 1:
            page['paragraphs']['last'] = paragraphs[-1]
            page['sentences']['last'] = getSentences(sentenceFormat, paragraphs[-1])[-1]

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

