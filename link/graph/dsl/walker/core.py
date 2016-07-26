# -*- coding: utf-8 -*-

from link.graph.dsl.walker.walkthrough import Walkthrough
from link.graph.dsl.walker.crud import CRUDOperations

from link.graph.dsl.semantics import GraphDSLSemantics
from grako.model import DepthFirstWalker


class GraphDSLNodeWalker(DepthFirstWalker):
    def __init__(self, graphmgr, *args, **kwargs):
        super(GraphDSLNodeWalker, self).__init__(*args, **kwargs)

        self.graphmgr = graphmgr
        self.semantics = GraphDSLSemantics()
        self.op_walk = Walkthrough(graphmgr)
        self.op_crud = CRUDOperations(graphmgr)

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
        node.op = node.op.value
        node.propname = node.propname.name
        node.value = node.value.value

    def walk_AssignSetNode(self, node, children_retval):
        node.propname = node.propname.name
        node.value = node.value.value

    def walk_AssignAddNode(self, node, children_retval):
        node.propname = node.propname.name
        node.value = node.value.value

    def walk_UpdateSetPropertyNode(self, node, children_retval):
        node.alias = node.alias.name
        node.propname = node.propname.name
        node.value = node.value.value

    def walk_UpdateAddPropertyNode(self, node, children_retval):
        node.alias = node.alias.name
        node.propname = node.propname.name
        node.value = node.value.value

    def walk_UpdateUnsetPropertyNode(self, node, children_retval):
        node.alias = node.alias.name
        node.propname = node.propname.name

    def walk_UpdateDelPropertyNode(self, node, children_retval):
        node.alias = node.alias.name
        node.propname = node.propname.name
        node.value = node.value.value

    def walk_WalkFilterNode(self, node, children_retval):
        if node.alias is not None:
            node.alias = node.alias.name

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

    def walk_NodeTypeNode(self, node, children_retval):
        if node.alias is not None:
            node.alias = node.alias.name

        node.types = [t.name for t in node.types.values_]
        node.properties = node.properties.assignations

    def walk_RelationTypeNode(self, node, children_retval):
        if node.alias is not None:
            node.alias = node.alias.name

        node.types = [t.name for t in node.types.values_]
        node.properties = node.properties.assignations

    def walk_TermRequestFilterNode(self, node, children_retval):
        node.op = node.op.value
        node.propname = node.propname.name
        node.value = node.value.value

    def walk_RequestFilterNode(self, node, children_retval):
        node.search = node.search.value

    def walk_AliasedFilterNode(self, node, children_retval):
        node.alias = node.alias.name

        if node.filter is not None:
            node.filter = node.filter.search

    def walk_CreateStatementNode(self, node, children_retval):
        node.typed.properties = [
            prop.value
            for prop in node.typed.properties
        ]

    def walk_ReadStatementNode(self, node, children_retval):
        filters = {}

        for nodefilter in node.filters:
            l = filters.setdefault(nodefilter.alias, [])

            if nodefilter.filter is not None:
                l.append(nodefilter.filter)

        node.filters = filters

    def walk_UpdateStatementNode(self, node, children_retval):
        node.updates = [
            update.value
            for update in node.updates
        ]

    def walk_DeleteStatementNode(self, node, children_retval):
        filters = {}

        for nodefilter in node.filters:
            l = filters.setdefault(nodefilter.alias, [])

            if nodefilter.filter is not None:
                l.append(nodefilter.filter)

        node.filters = filters

    def walk_WalkthroughBlock(self, node, children_retval):
        node.statements = list(reversed(node.statements))

    def walk_RequestNode(self, node, children_retval):
        if node.walkthrough is not None:
            node.walkthrough = node.walkthrough.statements

        else:
            node.walkthrough = []

        node.crud = node.crud.statements

        return node

        aliased_sets = self.op_walk(node.walkthrough)
        return self.op_crud(node.crud, aliased_sets)
