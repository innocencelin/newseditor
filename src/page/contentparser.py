import logging
import pyquery

from commonutil import lxmlutil

def parse(sentenceFormat, docelement):
    maxcontainer = parseTextArea(sentenceFormat, docelement)
    if maxcontainer is not None:
        paragraphs = getParagraphs(sentenceFormat, maxcontainer)
        return maxcontainer, paragraphs
    return None, None

def isTextParagraph(sentenceFormat, text):
    if not sentenceFormat:
        return True
    sentenceEnds = sentenceFormat.get('end')
    sentenceContains = sentenceFormat.get('contain')
    lastCharacter = text[-1]
    if lastCharacter in sentenceEnds:
        return True
    for contain in sentenceContains:
        if contain in text:
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

    maxsize = 0
    maxparents = []
    for parent, size in parentsum.iteritems():
        if size > maxsize:
            maxsize = size
            maxparents = [parent]
        elif size == maxsize:
            maxparents.append(parent)

    if not maxparents:
        return None

    maxsize = 0
    maxparent = None
    for parent in maxparents:
        text = parent.text_content()
        if text:
            text = text.strip()
        if text and len(text) > maxsize:
            maxsize = len(text)
            maxparent = parent
    # <p> can be splited by some tags("a", etc.) into multi htmlelement.
    # and <p> should not be seen as text container, it is the text itself.
    tags = ['p']
    if maxparent is not None and maxparent.tag in tags:
        maxparent = maxparent.getparent()
    return maxparent


def isCopyrightParagraph(sentenceFormat, text):
    copyrightFormats = sentenceFormat.get('copyright')
    if not copyrightFormats:
        return False
    for copyrightFormat in copyrightFormats:
        result = True
        for word in copyrightFormat:
            if not word in text:
                result = False
                break
        if result:
            return True
    return False

def getParagraphs(sentenceFormat, maxparent):
    paragraphs = []
    counter = 0
    text = maxparent.text
    if text:
        text = text.strip()
    if text and isTextParagraph(sentenceFormat, text):
        paragraphs.append({
            'text': text,
            'index': counter,
        })
    for child in maxparent.iterchildren():
        counter += 1
        text = child.text_content()
        if text:
            text = text.strip()
        if text and isTextParagraph(sentenceFormat, text):
            paragraphs.append({
                'text': text,
                'index': counter,
                'tag': child.tag,
            })
        text = child.tail
        if text:
            text = text.strip()
        if text:
            counter += 1
            if isTextParagraph(sentenceFormat, text):
                paragraphs.append({
                    'text': text,
                    'index': counter,
                })

    if not paragraphs:
        return None
    # text paragraph must have the same tag,
    # such as <p>, <div>, <br>(tag is none)
    tagsummary = {
    }
    for paragraph in paragraphs:
        tag = paragraph.get('tag', 'None')
        if tag in tagsummary:
            tagsummary[tag] += 1
        else:
            tagsummary[tag] = 1
    maxtag = None
    maxcount = 0
    for tag, count in tagsummary.iteritems():
        if count > maxcount:
            maxcount = count
            maxtag = tag
    paragraphs = [paragraph for paragraph in paragraphs
                    if paragraph.get('tag', 'None') == maxtag]
    if not paragraphs:
        return None

    # text paragraph must be near to other text paragraph
    size = len(paragraphs)
    for i in range(size):
        if i == 0:
            if i < size - 1:
                paragraphs[i]['distance'] = paragraphs[i + 1]['index'] \
                                             - paragraphs[i]['index']
            else:
                paragraphs[i]['distance'] = 0
        elif i == size -1:
            paragraphs[i]['distance'] = paragraphs[i]['index'] \
                                             - paragraphs[i - 1]['index']
        else:
            distance1 = paragraphs[i]['index'] - paragraphs[i - 1]['index']
            distance2 = paragraphs[i + 1]['index'] - paragraphs[i]['index']
            paragraphs[i]['distance'] = min(distance1, distance2)
    distances = [paragraph['distance'] for paragraph in paragraphs]
    davg = sum(distances) / size
    avgtoleration = 1
    paragraphs = [paragraph['text'] for paragraph in paragraphs
                    if paragraph['distance'] <= davg + avgtoleration]
    if paragraphs and isCopyrightParagraph(sentenceFormat, paragraphs[-1]):
        paragraphs = paragraphs[:-1]
    return paragraphs

