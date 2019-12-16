#!/usr/bin/env python
# -*-coding:utf-8 -*-

from utils.Parser import Parser
import urllib.request as ur
from bean.RootNode import RootNode
import jieba


class Spider:

    def __init__(self, node):
        self.node = node

    def go(self):
        parse = Parser()
        try:
            # 跟节点
            self.request(self.node)
            parse.themeParse(self.node)
            for theme in self.node.contextList:
                self.request(theme)
                parse.commentParse(theme)

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
    pageNum = 50
    for i in range(pageNum):
        rootNode = RootNode(code, i)
        spider = Spider(rootNode)
        spider.go()


