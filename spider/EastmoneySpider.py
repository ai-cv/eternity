#!/usr/bin/env python
# -*-coding:utf-8 -*-

from lxml import etree
import urllib.request as ur
from lxml.html import fromstring, tostring
import CommentNode
ID = 0


class Spider:
    # url = 'http://guba.eastmoney.com/list,600030,5,f_' + str(j) + '.html'
    def go(self, url):
        try:
            request = ur.Request(url)
            response = ur.urlopen(request)
            html = response.read().decode('utf-8')
            dom = etree.HTML(html)
            dom.xpath('/html[1]/body[1]/div[6]/div[2]/div[4]/div[9]/span[1]')
            html_tree = dom.xpath('//div[contains(@class, "articleh normal_post")]/span[contains(@class, "l")]')
            for i in range(0, len(html_tree) - 4, 5):
                print(i)
                readNum = html_tree[i].text
                conmentNum = html_tree[i + 1].text
                titleStr = tostring(html_tree[i + 2])
                authorStr = tostring(html_tree[i + 3])
                time = html_tree[i + 4].text
                titleDom = etree.HTML(titleStr).xpath('//a[contains(@href, "news")]')[0]
                authorDom = etree.HTML(authorStr).xpath('//a')[0]
                titleHref = titleDom.attrib['href']
                title = titleDom.text
                conmentNode = CommentNode(ID,  time, title)
                print(readNum + " " + conmentNum  + " " + title  + " " + time)

        except ur.URLError as e:
            if hasattr(e, "code"):
                print(e.code)
            if hasattr(e, "reason"):
                print(e.reason)


if __name__ == '__main__':
    globals(ID)

