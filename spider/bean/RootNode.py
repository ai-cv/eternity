from Node import Node


class RootNode(Node):
    """
    跟节点  一页是一个跟节点
    @:param nodelId 评论节点唯一识别符
    @:param time 评论时间
    @:param content 内容
    """

    def __init__(self, code, index):
        self.code = code
        self.href = "http://guba.eastmoney.com/list," + code + "_" + str(index) + ".html"
        self.themeList = []