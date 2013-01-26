import pyquery

from commonutil import lxmlutil

def parse(docelement, pagePositions, sentenceFormat):
    pMax, pParagraphs = parseByTagP(docelement, sentenceFormat)
    bMax, bParagraphs = parseByTagBr(docelement, sentenceFormat)
    maxparent = None
    maxparagraphs = None
    if pMax is not None:
        if bMax is not None:
            if len(pParagraphs) >= len(bParagraphs):
                maxparent = pMax
                maxparagraphs = pParagraphs
            else:
                maxparent = bMax
                maxparagraphs = bParagraphs
        else:
            maxparent = pMax
            maxparagraphs = pParagraphs
    else:
        if bMax is not None:
            maxparent = bMax
            maxparagraphs = bParagraphs

    # the biggest parent is the content element.
    if maxparent is not None:
        pagePositions['contentelement'] = maxparent

    return maxparagraphs

def isTextParagraph(text, sentenceFormat):
    matched = False
    sentenceEnds = sentenceFormat.get('end')
    sentenceContains = sentenceFormat.get('contain')
    lastCharacter = text[-1]
    if not sentenceFormat or lastCharacter in sentenceFormat:
        matched = True
    if not matched and sentenceContains:
        for sentenceContain in sentenceContains:
            if sentenceContain in text:
                matched = True
                break
    return matched

def getParagraphs(maxparent, sentenceFormat):
    paragraphs = []
    text = maxparent.text
    if text:
        text = text.strip()
    if text and isTextParagraph(text, sentenceFormat):
        paragraphs.append(text)
    tagOccurence = {}
    for child in maxparent.iterchildren():
        tag = child.tag
        if not tag:
            continue
        if tag in tagOccurence:
            tagOccurence[tag] += 1
        else:
            tagOccurence[tag] = 1
    maxtag = None
    maxsize = 0
    for key, value in tagOccurence.iteritems():
        if value > maxsize:
            maxsize = value
            maxtag = key
    if not maxtag:
        return paragraphs
    for child in maxparent.iterchildren():
        if child.tag != maxtag:
            continue
        text = child.text_content()
        if not text:
            text = child.tail
        if text:
            text = text.strip()
        if text and isTextParagraph(text, sentenceFormat):
            paragraphs.append(text)
    return paragraphs

def parseByTagP(docelement, sentenceFormat):
    items = pyquery.PyQuery(docelement)('p')

    # summarize paragraph size of parents.
    result = {}
    for item in items:
        text = item.text_content()
        if not text:
            continue
        parent = item.getparent()
        if parent in result:
            result[parent] += len(text)
        else:
            result[parent] = len(text)

    # identify the biggest parent
    maxsize = 0
    maxparent = None
    for parent, size in result.items():
        if size > maxsize:
            maxsize = size
            maxparent = parent
    paragraphs = []
    if maxparent is not None:
        paragraphs = getParagraphs(maxparent, sentenceFormat)
    return maxparent, paragraphs

def parseByTagBr(docelement, sentenceFormat):
    items = pyquery.PyQuery(docelement)('br')
    # summarize paragraph size of parents.
    result = {}
    for item in items:
        parent = item.getparent()
        if parent in result:
            result[parent] += 1
        else:
            result[parent] = 1

    maxsize = 0
    maxparent = None
    for parent, size in result.items():
        if size > maxsize:
            maxsize = size
            maxparent = parent

    paragraphs = []
    if maxparent is not None:
        paragraphs = getParagraphs(maxparent, sentenceFormat)
    return maxparent, paragraphs

