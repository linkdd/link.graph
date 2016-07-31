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

    def walk_AliasNode(self, node, children_retval):
        node.name = node.name.name

    def walk_TypeNode(self, node, children_retval):
        node.name = node.name.name

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

    def walk_TermFilterNode(self, node, children_retval):
        node.op = node.op.value
        node.propname = node.propname.name
        node.value = node.value.value

        node.query = self.semantics.parse_TermFilterNode(node)

        del node.op
        del node.propname
        del node.value

    def walk_AndFilterNode(self, node, children_retval):
        node.query = self.semantics.parse_AndFilterNode(node)

        del node.left
        del node.right

    def walk_OrFilterNode(self, node, children_retval):
        node.query = self.semantics.parse_OrFilterNode(node)

        del node.left
        del node.right

    def walk_InnerFilterNode(self, node, children_retval):
        node.query = node.search.value.query
        del node.search

    def walk_TypedFilterNode(self, node, children_retval):
        node.types = [t.name for t in node.types.values_]

        if node.filter.filter is not None:
            node.filter = node.filter.filter.query

        else:
            node.filter = None

        node.query = self.semantics.parse_TypedFilterNode(node)

        del node.types
        del node.filter

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

    def walk_FromNode(self, node, children_retval):
        node.set_ = node.set_.name

        if node.alias is not None:
            node.alias = node.alias.name

        node.filter = node.filter.query

    def walk_WalkModeNode(self, node, children_retval):
        if node.type is not None:
            node.type = node.type.value

        if node.direction is not None:
            node.direction = node.direction.value

        if node.begin is not None:
            node.begin = node.begin.value

        if node.end is not None:
            node.end = node.end.value

    def walk_ThroughNode(self, node, children_retval):
        node.set_ = node.set_.name

        if node.alias is not None:
            node.alias = node.alias.name

        if node.filter is not None:
            node.filter = node.filter.query

    def walk_ToNode(self, node, children_retval):
        node.alias = node.alias.name

        if node.filter is not None:
            node.filter = node.filter.query

    def walk_CreateStatementNode(self, node, children_retval):
        node.typed.properties = [
            prop.value
            for prop in node.typed.properties
        ]

    def walk_ReadStatementNode(self, node, children_retval):
        node.aliases = [a.name for a in node.aliases]

    def walk_UpdateStatementNode(self, node, children_retval):
        node.updates = [
            update.value
            for update in node.updates
        ]

    def walk_DeleteStatementNode(self, node, children_retval):
        node.aliases = [a.name for a in node.aliases]

    def walk_CRUDBlock(self, node, children_retval):
        node.statements = [n.statement for n in node.statements]

    def walk_RequestNode(self, node, children_retval):
        node.crud = node.crud.statements
        return node

        aliased_sets = self.op_walk(node.walkthrough)
        return self.op_crud(node.crud, aliased_sets)
