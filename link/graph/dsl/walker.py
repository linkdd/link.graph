# -*- coding: utf-8 -*-

from grako.model import NodeWalker


class GraphDSLNodeWalker(NodeWalker):
    def __init__(self, graphmgr, *args, **kwargs):
        super(GraphDSLNodeWalker, self).__init__(*args, **kwargs)

        self.graphmgr = graphmgr

    def walk_RequestNode(self, node):
        pass
