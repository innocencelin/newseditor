"""
The main purpose is to identify the content element.
It is the core feature, and other modules depend on its result.
"""
import logging
import re

import pyquery

from commonutil import lxmlutil
from pagecommon import isTextParagraph

def parse(contentFormat, docelement):
    if not contentFormat:
        return None, None
    sentenceFormat = contentFormat.get('sentence')
    maxcontainer = parseTextArea(sentenceFormat, docelement)
    if maxcontainer is not None:
        paragraphs = getParagraphs(contentFormat, maxcontainer)
        return maxcontainer, paragraphs
    return None, None

def isBrSeparated(element):
    for child in element.iterchildren():
        if child.tag == 'br':
            return True
    return False

def parseTextArea(sentenceFormat, docelement):
    parentsum = {}
    for item in docelement.iterdescendants():
        parent = item.getparent()
        if lxmlutil.isVisibleElement(item):
            text = item.text
            if text:
                text = text.strip()
            if text and isTextParagraph(sentenceFormat, text):
                if parent in parentsum:
                    parentsum[parent] += 1
                else:
                    parentsum[parent] = 1
        text = item.tail
        if text:
            text = text.strip()
        if text and isTextParagraph(sentenceFormat, text):
            if parent in parentsum:
                parentsum[parent] += 1
            else:
                parentsum[parent] = 1

    if not parentsum:
        return None

    maxsize = 0
    maxparents = []
    for parent, size in parentsum.iteritems():
        if size > maxsize:
            maxsize = size
            maxparents = [parent]
        else:
            maxparents.append(parent)

    if len(maxparents) == 1:
        maxparent = maxparents[0]
    else:
        # maybe all the items have same parent, the parent is needed.
        parentsum = {}
        for parent in maxparents:
            parent = parent.getparent()
            if parent is None:
                continue
            if parent in parentsum:
                parentsum[parent] += 1
            else:
                parentsum[parent] = 1
        maxsize = 0
        maxparentparent = None
        for parent, size in parentsum.iteritems():
            if size > maxsize:
                maxsize = size
                maxparentparent = parent
        if maxsize > 1:
            maxparent = maxparentparent
        else:
            # no same parent found, select the longest parent.
            maxparent = None
            maxsize = 0
            for parent in maxparents:
                text = parent.text_content()
                if text:
                    text = text.strip()
                if len(text) > maxsize:
                    maxsize = len(text)
                    maxparent = parent
    # <p> can be splited by some tags("a", "font", etc.) into multi htmlelement.
    # and <p> should not be seen as text container, it is the text itself.
    # <p> can be seen as container if it contains <br/>
    tags = ['p']
    if maxparent is not None and maxparent.tag in tags:
        if isBrSeparated(maxparent):
            return maxparent
        if len(pyquery.PyQuery(maxparent)('a')) > 0:
            return maxparent.getparent()
    return maxparent

"""
When br is used to separate paragraphs, it is hard to identify paragraphs.
Eg: <div>paragragh 1<br/>paragragh <b>2</b><br/>paragragh 3.
"""
def getBrParagraphs(maxparent):
    paragraphs = []
    text = maxparent.text
    if text:
        text = text.strip()
    for child in maxparent.iterchildren():
        if child.tag == 'br':
            if text:
                paragraphs.append(text)
            childtext = child.tail
            if childtext:
                childtext = childtext.strip()
            if childtext:
                text = childtext
            else:
                text = ''
        else:
            if lxmlutil.isVisibleElement(child):
                childtext = child.text
                if childtext:
                    childtext = childtext.strip()
                if childtext:
                    text += childtext
            childtext = child.tail
            if childtext:
                childtext = childtext.strip()
            if childtext:
                text += childtext
    if text:
        paragraphs.append(text)
    return paragraphs

def getParagraphs(contentFormat, maxparent):
    if isBrSeparated(maxparent):
        return getBrParagraphs(maxparent)
    paragraphs = []
    text = lxmlutil.getCleanText(maxparent)
    items = text.split('\n')
    for item in items:
        item = item.strip()
        if item:
            paragraphs.append(item)
    return paragraphs

