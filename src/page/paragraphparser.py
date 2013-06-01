import logging

from commonutil import lxmlutil

def _getChildTextLength(element):
    result = 0
    for item in element.getchildren():
        if lxmlutil.isVisibleElement(item):
            if item.text:
                result += len(item.text)
        if item.tail:
            result += len(item.tail)
    return result

def _getMainElement(contentElement):
    result = []
    for item in contentElement.iterdescendants():
        result.append((_getChildTextLength(item), item))
    return max(result, key=lambda item: item[0])[1]

def _getMaxChildTag(element):
    result = {}
    for item in element.getchildren():
        if item.tag in result:
            result[item.tag] += 1
        else:
            result[item.tag] = 1
    return max(result.iterkeys(), key=(lambda key: result[key]))

def _getParagraphsTagP(element):
    result = []
    for item in element.getchildren():
        if item.tag != 'p':
            continue
        content = lxmlutil.getCleanText(item)
        if content:
            result.append(content)
    return result

def _getParagraphsTagBR(element):
    return [lxmlutil.getCleanText(element)]

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

def _stripPreNonParagraph(paragraphFormat, paragraphs):
    result = []
    started = False
    for paragraph in paragraphs:
        if _isTextParagraph(paragraphFormat, paragraph):
            started = True
        if started:
            result.append(paragraph)
    return result

def parse(paragraphFormat, contentElement):
    mainElement = _getMainElement(contentElement)
    tag = _getMaxChildTag(mainElement)
    if tag == 'p':
        paragraphs = _getParagraphsTagP(mainElement)
    elif tag == 'br':
        paragraphs = _getParagraphsTagBR(mainElement)
    else:
        paragraphs = [lxmlutil.getCleanText(mainElement)]
    if paragraphFormat and paragraphs:
        paragraphs = _stripPreNonParagraph(paragraphFormat, paragraphs)
    return mainElement, paragraphs

