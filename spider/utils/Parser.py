#!/usr/bin/env python
# -*-coding:utf-8 -*-

from lxml import etree
from lxml.html import fromstring, tostring
from bean.ThemeNode import ThemeNode
from bean.ContentNode import ContentNode
import jieba
from dao.LocalFile import LocalFile
from nlp.Segment import Segment


class Parser:

    def __init__(self):
        # 分词和保存文件
        self.local_file = LocalFile()
        self.segment = Segment()

    def theme_parse(self, node):
        str_format = "{:^1}  |  {:^8} | {:^10} | {:^1} | {:^1}"
        dom = etree.HTML(node.html)
        dom.xpath('/html[1]/body[1]/div[6]/div[2]/div[4]/div[9]/span[1]')
        html_tree = dom.xpath('//div[contains(@class, "articleh normal_post")]/span[contains(@class, "l")]')
        context_list = []
        # 解析列表页主题
        for i in range(0, len(html_tree) - 4, 5):
            read_num = html_tree[i].text
            comment_num = html_tree[i + 1].text
            title_str = tostring(html_tree[i + 2])
            # author_str = tostring(html_tree[i + 3])
            time = html_tree[i + 4].text
            title_dom = etree.HTML(title_str).xpath('//a[contains(@href, "news")]')[0]
            # author_dom = etree.HTML(author_str).xpath('//a')[0]
            title_href = title_dom.attrib['href']
            # title = titleDom.text
            theme_node = ThemeNode("theme" + str(i), time, title_href, read_num, comment_num)
            print(str_format.format(theme_node.nodeId, theme_node.time, theme_node.href, theme_node.readNum, theme_node.commentNum))
            context_list.append(theme_node)
        node.contextList = context_list

    def comment_parse(self, theme_node):
        # str_format = "{:^1}  |  {:^8} | {:^10}"
        comment_list = []
        dom = etree.HTML(theme_node.html)
        theme_node.theme = "".join(dom.xpath('//*/div[contains(@class,"xeditor")]/text()')).strip()
        # 保存主题
        self.local_file.save(self.segment.cut(theme_node.theme))
        time_element = dom.xpath('//*/div[@class="zwlitime"]')
        content_element = dom.xpath('//*/div[@class="zwlitext  stockcodec"]/div[@class="short_text"]')
        for i in range(len(time_element)):
            text = content_element[i].text.strip()
            if len(text) < 3:
                continue
            content_node = ContentNode(theme_node.nodeId + "content" + str(i), content_element[i].text, content_element[i].text.strip())
            comment_list.append(content_node)
            # print(str_format.format(contentNode.nodeId, contentNode.time, contentNode.content))
            self.local_file.save(self.segment.cut(content_node.content))
        theme_node.commentList = comment_list
