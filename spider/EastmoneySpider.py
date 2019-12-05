#!/usr/bin/env python
# -*-coding:utf-8 -*-

from utils.Parser import Parser
from lxml import etree
import urllib.request as ur
from lxml.html import fromstring, tostring
import urllib.request as ur

class Spider:

    def go(self, url):
        parse = Parser()
        try:
            request = ur.Request(url)
            response = ur.urlopen(request)
            html = response.read().decode('utf-8')
            parse.commentParse(html)

        except ur.URLError as e:
            if hasattr(e, "code"):
                print(e.code)
            if hasattr(e, "reason"):
                print(e.reason)


if __name__ == '__main__':
    code = "002243"
    url = "http://guba.eastmoney.com/list," + code + ".html"
    spider = Spider()
    spider.go(url)

