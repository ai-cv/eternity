class Node:
    """
    @:param nodelId 评论节点唯一识别符
    @:param time 评论时间
    @:param content 内容
    """
    def __init__(self, nodeId, time, content):
        self.nodeId = nodeId
        self.time = time
        self.content = content