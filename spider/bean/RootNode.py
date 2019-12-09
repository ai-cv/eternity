from Node import Node

class RootNode(Node):
    """
    @:param nodelId 评论节点唯一识别符
    @:param time 评论时间
    @:param content 内容
    """

    def __init__(self, code):
        self.code = code
        self.href = "http://guba.eastmoney.com/list," + code + ".html"
        self.themeList = []