from Node import Node


class CommentNode(Node):
    """
    父节点，主要是主页发表的主题
    @:param nodelId 评论节点唯一识别符
    @:param time 评论时间
    @:param content 内容
    """
    def __init__(self, nodeId, time, content, href):
        super().__init__(nodeId, time, content)
        self.href = href
