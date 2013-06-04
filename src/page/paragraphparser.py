import logging

from commonutil import lxmlutil

"""
tag li can not be seen as paragraph.
paragraph can only contains inline tags.
"""
def _getParagraphLengthByLink(element):
    if element.tag == 'li':
        return 0
    result = 0
    if element.text:
        result += len(element.text.strip())
    for item in element.getchildren():
        # treat br specially, it is used as paragraph separator by some site
        if item.tag == 'br':
            continue
        if item.tag not in lxmlutil.INLINE_TAGS:
            continue
        text = lxmlutil.getCleanText(item)
        if text:
            result += len(text)
        if item.tail:
            result += len(item.tail.strip())
    return result

"""
<p> often contains <a>, then p.text is only a small part of p.
"""
def _getChildTextLength(element):
    result = 0
    for item in element.getchildren():
        if lxmlutil.isVisibleElement(item):
            result += _getParagraphLengthByLink(item)
        if item.tail:
            result += len(item.tail.strip())
    return result

def _getMainElement(contentElement, titleElement):
    _MIN_MAIN_LENGTH = 100
    items = []
    lxmlutil.findAllVisibleMatched(items, contentElement)
    result = []
    for item in items:
        weight = _getChildTextLength(item)
        result.append([weight, item])
    result2 = [item for item in result if item[0] >= _MIN_MAIN_LENGTH]
    for item in result2:
        # an element with more children is prefered.
        # an elment closer to title element is prefered.
        # 11 is used to avoid divide by 0 and a more balance.
        # eg, (m/2, n/22), (m/12, n/32); the later n has more chance.
        item[0] = item[0] * len(item[1].getchildren()
                    ) * 1.0 / (abs(item[1].sourceline - titleElement.sourceline) + 11)
    if result2:
        return max(result2, key=lambda item: item[0])[1]
    return max(result, key=lambda item: item[0])[1]

def _getMaxChildTag(element):
    result = {}
    for item in element.getchildren():
        textlen = 0
        if lxmlutil.isVisibleElement(item):
            textlen += _getParagraphLengthByLink(item)
        if item.tail:
            textlen += len(item.tail.strip())
        if item.tag in result:
            result[item.tag] += textlen
        else:
            result[item.tag] = textlen
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
    for paragraph in paragraphs:
        lines = paragraph.split('\n')
        for line in lines:
            line = line.strip()
            if not line:
                continue
            result.append(line)
    start = 0
    for paragraph in result:
        if _isTextParagraph(paragraphFormat, paragraph):
            break
        start += 1
    end = 0
    for paragraph in reversed(result):
        if _isTextParagraph(paragraphFormat, paragraph):
            break
        end += 1
    if end > 0:
        return result[start:-end]
    return result[start:]

def parse(paragraphFormat, contentElement, titleElement):
    mainElement = _getMainElement(contentElement, titleElement)
    tag = _getMaxChildTag(mainElement)
    paragraphs = _getParagraphsByTag(mainElement, tag)
    if paragraphFormat and paragraphs:
        paragraphs = _formatParagraphs(paragraphFormat, paragraphs)
    return mainElement, paragraphs

