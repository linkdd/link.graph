# -*- coding: utf-8 -*-

from link.graph.dsl.semantics import GraphDSLSemantics
from link.graph.algorithms import NodeFilter, RelFilter, Joint

from grako.model import DepthFirstWalker


class GraphDSLNodeWalker(DepthFirstWalker):
    def __init__(self, graphmgr, *args, **kwargs):
        super(GraphDSLNodeWalker, self).__init__(*args, **kwargs)

        self.graphmgr = graphmgr
        self.context = None
        self.aliases = {}
        self.semantics = GraphDSLSemantics()

    def walk_StringNode(self, node, child_retval):
        node.value = self.semantics.parse_StringNode(node)

    def walk_NaturalNode(self, node, child_retval):
        node.value = self.semantics.parse_NaturalNode(node)

    def walk_IntegerNode(self, node, child_retval):
        node.value = self.semantics.parse_IntegerNode(node)
        del node.sign
        del node.int

    def walk_DecimalNode(self, node, child_retval):
        node.value = self.semantics.parse_DecimalNode(node)
        del node.sign
        del node.int
        del node.dec

    def walk_BooleanNode(self, node, child_retval):
        node.value = self.semantics.parse_BooleanNode(node)

    def walk_ValueNode(self, node, child_retval):
        node.value = self.semantics.parse_ValueNode(node)

    def walk_AliasedElementsNode(self, node, child_retval):
        node.elt_type = node.elts.elt_type
        node.query = self.semantics.parse_query(node)
        del node.elts

        if node.alias is not None:
            node.alias = node.alias.name
            self.aliases[node.alias] = node

    def walk_CardinalityNode(self, node, child_retval):
        node.begin = node.begin.value
        node.end = node.end.value

    def walk_PathNode(self, node, child_retval):
        return self.semantics.parse_PathNode(node)

    def walk_WalkthroughStatementNode(self, node, child_retval):
        node.path = child_retval[0]

    def walk_WalkthroughBlockNode(self, node, child_retval):
        walk_sequence = [
            (
                node.walkstmt[0].elt_type,
                node.walkstmt[0].query
            )
        ]

        for walknode in node.walkstmt[1:]:
            if walknode.__class__.__name__ == 'AliasedElementsNode':
                if walknode.elt_type == 'NODES':
                    walk_sequence.append(
                        NodeFilter(self.graphmgr, walknode.query)
                    )

                elif walknode.elt_type == 'RELS':
                    walk_sequence.append(
                        RelFilter(self.graphmgr, walknode.query)
                    )

            elif walknode.__class__.__name__ == 'JointNode':
                algo = Joint(
                    self.graphmgr,
                    elements=walknode.ejoint,
                    nodes=walknode.njoint,
                    relationships=walknode.rjoint,
                    graphs=walknode.gjoint
                )
                walk_sequence.append(algo)

        node.sequence = walk_sequence
        del node.walkstmt

    def walk_RequestNode(self, node, child_retval):
        # walk through graph
        initial = node.walkthrough.sequence[0]

        if initial[0] == 'NODES':
            f = self.graphmgr.nodes_store.get_feature('fulltext')

        elif initial[0] == 'RELS':
            f = self.graphmgr.relationships_store.get_feature('fulltext')

        self.context = f(initial[1])

        for step in node.walkthrough.sequence[1:]:
            self.context = self.graphmgr.call_algorithm(self.context, step)

        # TODO: filter elements
        # TODO: apply CRUD operations

        return self.context
