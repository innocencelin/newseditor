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

def _getMainElement(contentelement):
    result = []
    for item in contentelement.iterdescendants():
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
        result.append(lxmlutil.getCleanText(item))
    return result

def _getParagraphsTagBR(element):
    return [lxmlutil.getCleanText(element)]

def parse(contentelement):
    mainElement = _getMainElement(contentelement)
    tag = _getMaxChildTag(mainElement)
    if tag == 'p':
        paragraphs = _getParagraphsTagP(mainElement)
    elif tag == 'br':
        paragraphs = _getParagraphsTagBR(mainElement)
    else:
        paragraphs = [lxmlutil.getCleanText(mainElement)]
    return mainElement, paragraphs

