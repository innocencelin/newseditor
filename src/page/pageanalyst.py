
from urlparse import urlparse

import lxml
import pyquery

def _formatTitle(title):
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

class PageAnalyst(object):

    def analyse(self, content, oldPage):
        filename = urlparse(oldPage['url']).path.split('/')[-1]
        detailed = '.' in filename

        htmlelement = lxml.html.fromstring(content)
        docquery = pyquery.PyQuery(htmlelement)

        title = None
        items = docquery('head title')
        if len(items) > 0:
            title = items[0].text_content()
        page = {
            'url': oldPage['url']
        }
        oldTitle = oldPage.get('title')
        if title:
            title = _formatTitle(title)
        if detailed:
            page['title'] = getTitle(oldTitle, title)
        else:
            if oldTitle:
                page['title'] = '%s: %s' % (oldTitle, title)
            else:
                page['title'] = title
        return page

