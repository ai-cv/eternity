#!/usr/bin/env python
# -*-coding:utf-8 -*-

from lxml import etree
from lxml.html import fromstring, tostring
from bean.ThemeNode import ThemeNode
from bean.ContentNode import ContentNode


class Parser:
    def themeParse(self, node):
        strFormat = "{:^1}  |  {:^8} | {:^10} | {:^1} | {:^1}"
        dom = etree.HTML(node.html)
        dom.xpath('/html[1]/body[1]/div[6]/div[2]/div[4]/div[9]/span[1]')
        html_tree = dom.xpath('//div[contains(@class, "articleh normal_post")]/span[contains(@class, "l")]')
        contextList = []
        for i in range(0, len(html_tree) - 4, 5):
            readNum = html_tree[i].text
            commentNum = html_tree[i + 1].text
            titleStr = tostring(html_tree[i + 2])
            authorStr = tostring(html_tree[i + 3])
            time = html_tree[i + 4].text
            titleDom = etree.HTML(titleStr).xpath('//a[contains(@href, "news")]')[0]
            authorDom = etree.HTML(authorStr).xpath('//a')[0]
            titleHref = titleDom.attrib['href']
            title = titleDom.text
            themeNode = ThemeNode("theme" + str(i), time, titleHref, readNum, commentNum)
            print(strFormat.format(themeNode.nodeId, themeNode.time, themeNode.href, themeNode.readNum, themeNode.commentNum))
            contextList.append(themeNode)
        node.contextList = contextList

    def commentParse(self, themeNode):
        strFormat = "{:^1}  |  {:^8} | {:^10}"
        commentList = []
        dom = etree.HTML(themeNode.html)
        themeNode.theme = dom.xpath('//*[@id="zwconbody"]/div')[0].text
        timeElement = dom.xpath('//*/div[@class="zwlitime"]')
        contentElement = dom.xpath('//*/div[@class="zwlitext  stockcodec"]/div[@class="short_text"]')
        for i in range(len(timeElement)):
            contentNode = ContentNode(themeNode.nodeId + "content" + str(i), timeElement[i].text, contentElement[i].text.strip())
            commentList.append(contentNode)
            print(strFormat.format(contentNode.nodeId, contentNode.time, contentNode.content))
        themeNode.commentList = commentList
