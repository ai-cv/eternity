class ContentNode(Node):
    """
    父节点，主要是主页发表的主题
    @:param nodelId 评论节点唯一识别符
    @:param time 评论时间
    @:param content 内容
    @:param commentNum 评论数量
    @:param title 主题名字
    """
    def __init__(self, nodeId, time, content, commentNum, title):
        super(nodeId, time, content)
        self.commentNum = commentNum
        self.title = title

