#!/usr/bin/env python
# -*-coding:utf-8 -*-

from utils.Parser import Parser
import urllib.request as ur
from bean.RootNode import RootNode


class Spider:

    def __init__(self, node):
        self.node = node

    def go(self):
        parse = Parser()
        try:
            self.request(self.node)
            parse.themeParse(self.node)
            for theme in self.node.contextList:
                commentHtml = self.request(theme)

        except ur.URLError as e:
            if hasattr(e, "code"):
                print(e.code)
            if hasattr(e, "reason"):
                print(e.reason)

    def request(self, node):
        request = ur.Request(node.href)
        response = ur.urlopen(request)
        node.html = response.read().decode('utf-8')


if __name__ == '__main__':
    code = "002243"
    rootNode = RootNode(code)
    spider = Spider(rootNode)
    spider.go()

