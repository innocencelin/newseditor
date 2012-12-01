
import lxml
import pyquery

def formatTitle(title):
    separators = ['_', '|', '-',]
    maxvalue = title
    for separator in separators:
        parts = maxvalue.split(separator)
        maxlen = -1
        maxvalue = None
        for part in parts:
            plen = len(part)
            if plen > maxlen:
                maxlen = plen
                maxvalue = part
        if len(parts) > 1:
            break
    return maxvalue

def getTitle(oldTitle, newTitle):
    if not oldTitle:
        return newTitle
    if not newTitle:
        return oldTitle
    if len(oldTitle) >= len(newTitle):
        return oldTitle
    return newTitle

def getTitleFromDoc(docelement):
    docquery = pyquery.PyQuery(docelement)
    title = None
    items = docquery('head title')
    if len(items) > 0:
        title = items[0].text_content()
    return title

class PageAnalyst(object):

    def analyse(self, content, page):
        docelement = lxml.html.fromstring(content)
        title = getTitleFromDoc(docelement)
        if title:
            oldTitle = page.get('title')
            title = formatTitle(title)
            page['title'] = getTitle(oldTitle, title)
        return page

