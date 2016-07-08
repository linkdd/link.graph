# -*- coding: utf-8 -*-

from link.graph.dsl.semantics import GraphDSLSemantics
from link.graph.algorithms import Filter, Follow

from grako.model import DepthFirstWalker


class GraphDSLNodeWalker(DepthFirstWalker):
    def __init__(self, graphmgr, *args, **kwargs):
        super(GraphDSLNodeWalker, self).__init__(*args, **kwargs)

        self.graphmgr = graphmgr
        self.semantics = GraphDSLSemantics()

    def walk_StringNode(self, node, children_retval):
        node.value = self.semantics.parse_StringNode(node)

    def walk_NaturalNode(self, node, children_retval):
        node.value = self.semantics.parse_NaturalNode(node)

    def walk_IntegerNode(self, node, children_retval):
        node.value = self.semantics.parse_IntegerNode(node)
        del node.sign
        del node.int

    def walk_DecimalNode(self, node, children_retval):
        node.value = self.semantics.parse_DecimalNode(node)
        del node.sign
        del node.int
        del node.dec

    def walk_BooleanNode(self, node, children_retval):
        node.value = self.semantics.parse_BooleanNode(node)

    def walk_ValueNode(self, node, children_retval):
        node.value = self.semantics.parse_ValueNode(node)

    def walk_CardinalityNode(self, node, children_retval):
        node.begin = node.begin.value
        node.end = node.end.value

    def walk_AliasNode(self, node, children_retval):
        node.name = node.name.name

    def walk_TypeNode(self, node, children_retval):
        node.name = node.name.name

    def walk_ConditionNode(self, node, children_retval):
        node.propname = node.propname.name
        node.op = node.op.value
        node.value = node.value.value

    def walk_AssignNode(self, node, children_retval):
        node.propname = node.propname.name
        node.value = node.value.value

    def walk_NodeFilterNode(self, node, children_retval):
        node.properties = node.properties.conditions
        node.types = node.types.values_

        node.query = self.semantics.parse_query(node)

        del node.properties
        del node.types

    def walk_RelationFilterNode(self, node, children_retval):
        node.properties = node.properties.conditions
        node.types = node.types.values_

        node.query = self.semantics.parse_query(node)

        del node.properties
        del node.types

    def walk_FollowNode(self, node, children_retval):
        node.type = node.type.value
        node.direction = node.direction.value

    def walk_WalkthroughBlock(self, node, children_retval):
        node.statements = list(reversed(node.statements))

    def walk_RequestNode(self, node, children_retval):
        if node.walkthrough is not None:
            node.walkthrough = node.walkthrough.statements

        else:
            node.walkthrough = []

        node.crud = node.crud.statements

        context, aliased_sets = self.do_walkthrough(node.walkthrough)
        result = self.do_crud(node.crud, context, aliased_sets)

        return result

    def _get_storage(self, filter_node):
        if filter_node.__class__.__name__ == 'NodeFilterNode':
            store = self.graphmgr.nodes_store

        elif filter_node.__class__.__name__ == 'RelationFilterNode':
            store = self.graphmgr.relationships_store

        return store.get_feature('fulltext')

    def do_walkthrough(self, statements):
        context = None
        aliased_sets = {}

        if len(statements) > 0:
            initial_req = statements[0].filter
            store = self._get_storage(initial_req)

            context = store.search(initial_req.query)

            if initial_req.alias is not None:
                aliased_sets[initial_req.alias] = context

            if initial_req.follow is not None:
                algo = Follow(self.graphmgr, initial_req.follow)
                context = self.graphmgr.call_algorithm(context, algo)

            for statement in statements[1:]:
                algo = Filter(self.graphmgr, statement.filter.query)
                context = self.graphmgr.call_algorithm(context, algo)

                if statement.filter.alias is not None:
                    aliased_sets[statement.filter.alias] = context

                if statement.follow is not None:
                    algo = Follow(self.graphmgr, statement.follow)
                    context = self.graphmgr.call_algorithm(context, algo)

        return context, aliased_sets

    def do_crud(self, statements, context, aliased_sets):
        return None
