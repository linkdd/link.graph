# -*- coding: utf-8 -*-

from link.graph.dsl.semantics import GraphDSLSemantics
from grako.model import DepthFirstWalker


class GraphDSLNodeWalker(DepthFirstWalker):
    def __init__(self, graphmgr, *args, **kwargs):
        super(GraphDSLNodeWalker, self).__init__(*args, **kwargs)

        self.graphmgr = graphmgr
        self.context = None
        self.aliases = {}
        self.semantics = GraphDSLSemantics()

    def walk_StringNode(self, node, *args):
        node.value = self.semantics.parse_StringNode(node)

    def walk_IntegerNode(self, node, *args):
        node.value = self.semantics.parse_IntegerNode(node)

    def walk_DecimalNode(self, node, *args):
        node.value = self.semantics.parse_DecimalNode(node)

    def walk_BooleanNode(self, node, *args):
        node.value = self.semantics.parse_BooleanNode(node)

    def walk_ValueNode(self, node, *args):
        node.value = self.semantics.parse_ValueNode(node)

    def walk_WalkthroughBlockNode(self, node, *args):
        for walkstmt in node.walkstmt:
            print('---')
            nodes = self.semantics.parse_PathNode(walkstmt.path)

            for node in nodes:
                if node.__class__.__name__ == 'AliasedElementsNode':
                    if node.alias is not None:
                        self.aliases[node.alias.name] = node.elts

                    types = [
                        t.name
                        for t in node.elts.types
                    ]

                    type_query = 'type_set:({0})'.format(' OR '.join(types))

                    print('TYPES:', type_query)
                    print('PROPS:', node.elts.props)

                else:
                    print('JOINT:', node)
