# -*- coding: utf-8 -*-
import unittest
import os
from page import PageAnalyst

class TestPageAnalyst(unittest.TestCase):

    def setUp(self):
        pass

    def _loadTestData(self, filename):
        filepath = os.path.join(os.path.dirname(__file__), 'data', filename)
        with open(filepath, 'r') as f:
            content = f.read()
        return unicode(content, 'utf-8','ignore')

    def testGetTitle(self):
        content = self._loadTestData('base.html')
        page = {'title': 'title'}
        PageAnalyst().analyse(content, page)
        self.assertEquals(page['title'], 'title1')


if __name__ == '__main__':
    unittest.main()

