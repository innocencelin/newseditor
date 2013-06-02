import logging

from commonutil import lxmlutil

def _getChildTextLength(element):
    result = 0
    for item in element.getchildren():
        if lxmlutil.isVisibleElement(item):
            if item.text:
                result += len(item.text.strip())
        if item.tail:
            result += len(item.tail.strip())
    return result

def _getMainElement(contentElement):
    items = []
    lxmlutil.findAllVisibleMatched(items, contentElement)
    result = []
    for item in items:
        result.append((_getChildTextLength(item), item))
    return max(result, key=lambda item: item[0])[1]

def _getMaxChildTag(element):
    result = {}
    for item in element.getchildren():
        text = ''
        if lxmlutil.isVisibleElement(item) and item.text:
            text = item.text.strip()
        if not text and item.tail:
            text = item.tail.strip()
        if item.tag in result:
            result[item.tag] += len(text)
        else:
            result[item.tag] = len(text)
    return max(result.iterkeys(), key=(lambda key: result[key]))

def _getParagraphsByTag(element, tag):
    result = []
    for item in element.getchildren():
        if item.tag != tag:
            continue
        content = lxmlutil.getCleanText(item)
        if not content:
            content = item.tail
            if content:
                content = content.strip()
        if content:
            result.append(content)
    return result

def _isTextParagraph(paragraphFormat, text):
    sentenceEnds = paragraphFormat.get('end')
    sentenceContains = paragraphFormat.get('contain')
    lastCharacter = text[-1]
    if lastCharacter in sentenceEnds:
        return True
    for contain in sentenceContains:
        if contain in text:
            return True
    return False

def _formatParagraphs(paragraphFormat, paragraphs):
    result = []
    started = False # filter the starting non sentence paragraph
    for paragraph in paragraphs:
        lines = paragraph.split('\n')
        for line in lines:
            line = line.strip()
            if not line:
                continue
            if _isTextParagraph(paragraphFormat, line):
                started = True
            if started:
                result.append(line)
    return result

def parse(paragraphFormat, contentElement):
    mainElement = _getMainElement(contentElement)
    tag = _getMaxChildTag(mainElement)
    paragraphs = _getParagraphsByTag(mainElement, tag)
    if paragraphFormat and paragraphs:
        paragraphs = _formatParagraphs(paragraphFormat, paragraphs)
    return mainElement, paragraphs

