
from urlparse import urlparse

import lxml
import pyquery

def _formatTitle(title):
    return title.split('_')[0]

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
        page = {}
        if oldPage.get('title'):
            page['title'] = oldPage['title']
        if title:
            formattedTitle = _formatTitle(title)
            if detailed:
                page['title'] = formattedTitle
            else:
                page['pagetitle'] = formattedTitle
        return page

