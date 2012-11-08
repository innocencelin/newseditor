
from urlparse import urlparse

import lxml
import pyquery

def _formatTitle(title):
    parts = title.split('_')
    maxlen = -1
    maxvalue = None
    for part in parts:
        plen = len(part)
        if plen > maxlen:
            maxlen = plen
            maxvalue = part
    return maxvalue

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
            page['title'] = title if title else oldTitle
        else:
            if oldTitle:
                page['title'] = oldTitle
                page['pagetitle'] = title
            else:
                page['title'] = title
        return page

