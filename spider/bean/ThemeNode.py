from Node import Node


class ThemeNode(Node):
    """
    父节点，主要是主页发表的主题
    @:param nodelId 评论节点唯一识别符
    @:param time 评论时间
    @:param href 链接
    @:param theme 主题
    @:param commentList 主题下评论列表
    @:param readNum
    @:param commentNum
    """
    prefix = "http://guba.eastmoney.com"

    def __init__(self, nodeId, time, href, readNum, commentNum):
        super().__init__(nodeId, time, "")
        self.href = self.prefix + href
        self.theme = ""
        self.commentList = []
        self.readNum = readNum
        self.commentNum = commentNum
