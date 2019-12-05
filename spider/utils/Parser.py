#!/usr/bin/env python
# -*-coding:utf-8 -*-

from lxml import etree
from lxml.html import fromstring, tostring
from bean.CommentNode import CommentNode

class Parser:

    def commentParse(self, html):
        dom = etree.HTML(html)
        dom.xpath('/html[1]/body[1]/div[6]/div[2]/div[4]/div[9]/span[1]')
        html_tree = dom.xpath('//div[contains(@class, "articleh normal_post")]/span[contains(@class, "l")]')
        contextList = []
        for i in range(0, len(html_tree) - 4, 5):
            readNum = html_tree[i].text
            conmentNum = html_tree[i + 1].text
            titleStr = tostring(html_tree[i + 2])
            authorStr = tostring(html_tree[i + 3])
            time = html_tree[i + 4].text
            titleDom = etree.HTML(titleStr).xpath('//a[contains(@href, "news")]')[0]
            authorDom = etree.HTML(authorStr).xpath('//a')[0]
            titleHref = titleDom.attrib['href']
            title = titleDom.text
            commentNode = CommentNode(i, time, title, titleHref)
            strFormat = "{:^1}  |  {:^8} |  {:^8} |  {:^19}"
            print(strFormat.format(commentNode.nodeId, commentNode.time, commentNode.content, commentNode.href))
            contextList.append(commentNode)
        return contextList
