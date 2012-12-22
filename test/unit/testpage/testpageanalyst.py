# -*- coding: utf-8 -*-
import unittest
import os
from page import pageanalyst
from page import PageAnalyst

class BaseTestCase(unittest.TestCase):

    def _loadTestData(self, filename):
        filepath = os.path.join(os.path.dirname(__file__), 'data', filename)
        with open(filepath, 'r') as f:
            content = f.read()
        return unicode(content, 'utf-8','ignore')



class TestBase(BaseTestCase):

    def testBodyTitle(self):
        content = self._loadTestData('base.html')

        bodyContent = pageanalyst.getBodyContent(content)
        expected = 'body here\n<p>abc (title1) xyz\nhaha</p>\n<p>Old Title In Body\nhaha</p>\n'
        self.assertEquals(bodyContent, expected)

        bodyTitle = pageanalyst.getTitileFromBody(bodyContent, 'title1')
        self.assertEquals(bodyTitle, 'abc (title1) xyz')

class TestTitle(BaseTestCase):

    def setUp(self):
        pass

    def testChinaSafety(self):
        content = self._loadTestData('chinasafety.html')
        # the comments before DOCTYPE make lxml and pyquery fail to match "head title"
        title1 = pageanalyst.getTitleFromDoc(content)
        self.assertIsNone(title1)

        title2 = pageanalyst.getTitleFromHead(content)
        expected = u'杨栋梁在部分重点煤炭企业主要负责人座谈会上强调：深入贯彻党的十八大精神 以科学发展观为指导 严格落实企业主体责任 强化安全生产基础建设_国家安全监管总局'
        self.assertEquals(title2, expected)

    def testTitle(self):
        content = self._loadTestData('base.html')

        p = PageAnalyst()
        page = {'title': 'oldTitle'}
        p.analyse(content, page, separators=u'-_|')
        expected = 'abc (title1) xyz'
        self.assertEquals(page['title'], expected)


class TestOldTitle(BaseTestCase):
    def atestOldTitleInHead(self):
        content = self._loadTestData('base.html')

        p = PageAnalyst()
        oldTitle = 'a-(title1)'
        page = {'title': oldTitle}
        p.analyse(content, page, separators=u'-_|')
        self.assertEquals(page['title'], oldTitle)

    def testOldTitleInBody(self):
        content = self._loadTestData('base.html')

        p = PageAnalyst()
        oldTitle = 'Old Title In Body'
        page = {'title': oldTitle}
        p.analyse(content, page, separators=u'-_|')
        self.assertEquals(page['title'], oldTitle)

class TestNoHead(BaseTestCase):

    def testNoHead(self):
        content = self._loadTestData('base-nohead.html')

        title = pageanalyst.getTitleFromHead(content)
        self.assertIsNone(title)

    def testNoHeadTitle(self):
        content = self._loadTestData('base-nohead.html')

        p = PageAnalyst()
        oldTitle = 'oldTitle'
        page = {'title': oldTitle}
        p.analyse(content, page, separators=u'-_|')
        self.assertEquals(page['title'], oldTitle)


class TestNoBody(BaseTestCase):

    def testNoBody(self):
        content = self._loadTestData('base-nobody.html')

        body = pageanalyst.getBodyContent(content)
        self.assertIsNone(body)

    def testNoBodyTitle(self):
        content = self._loadTestData('base-nobody.html')

        p = PageAnalyst()
        page = {'title': 'oldTitle'}
        p.analyse(content, page, separators=u'-_|')
        expected = '(title1)'
        self.assertEquals(page['title'], expected)

if __name__ == '__main__':
    unittest.main()
    # suite = unittest.TestLoader().loadTestsFromTestCase(TestOldTitle)
    # unittest.TextTestRunner().run(suite)

