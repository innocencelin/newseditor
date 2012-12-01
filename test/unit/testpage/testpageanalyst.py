# -*- coding: utf-8 -*-
import unittest
import os
from page import pageanalyst
from page import PageAnalyst

class TestPageAnalyst(unittest.TestCase):

    def setUp(self):
        pass

    def _loadTestData(self, filename):
        filepath = os.path.join(os.path.dirname(__file__), 'data', filename)
        with open(filepath, 'r') as f:
            content = f.read()
        return unicode(content, 'utf-8','ignore')

    def testBodyTitle(self):
        content = self._loadTestData('base.html')

        bodyContent = pageanalyst.getBodyContent(content)
        expected = 'body here\n<p>abc (title1) xyz</p>\n'
        self.assertEquals(bodyContent, expected)

        bodyTitle = pageanalyst.getTitileFromBody(bodyContent, 'title1')
        self.assertEquals(bodyTitle, 'abc (title1) xyz')


if __name__ == '__main__':
    unittest.main()

