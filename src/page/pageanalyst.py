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

def getSentences(text, sentenceFormat):
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

    sentenceFormat = editorFormat.get('sentence', {})
    contentelement, paragraphs = contentparser.parse(docelement, sentenceFormat)
    if paragraphs:
        page['paragraphs'] = {}
        page['sentences'] = {}
        page['paragraphs']['first'] = paragraphs[0]
        page['sentences']['first'] = getSentences(paragraphs[0], sentenceFormat)[0]
        if len(paragraphs) > 1:
            page['paragraphs']['last'] = paragraphs[-1]
            page['sentences']['last'] = getSentences(paragraphs[-1], sentenceFormat)[-1]

    publishedFormat = editorFormat.get('published', {})
    publishedelement = None
    if publishedFormat:
        if contentelement is not None:
            publishedelement, published = publishedparser.parseByElement(publishedFormat, contentelement)
        else:
            published = publishedparser.parseByText(publishedFormat, content)
        if published:
            page['published'] = published

    mainelement = None
    if contentelement is not None and publishedelement is not None:
        mainelement = getMainElement(contentelement, publishedelement)

    img = None
    if mainelement is not None:
        img = imgparser.parse(url, mainelement)
    elif contentelement:
        img = imgparser.parse(url, contentelement)
    if img:
        page['img'] = img

    titleelement = None
    title = None
    if mainelement is not None and publishedelement is not None:
        titleelement, title = titleparser.parseByElement(mainelement, publishedelement)
        if title:
            page['title'] = title
    if not title:
        titleFormat = editorFormat.get('title', {})
        title = titleparser.parseByText(titleFormat, url, content, fortest)
        if title:
            page['title'] = title
    return page

