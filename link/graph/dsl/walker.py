# -*- coding: utf-8 -*-

from link.graph.algorithms import Filter, Follow, Update, Link
from link.graph.dsl.semantics import GraphDSLSemantics

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
        node.alias = node.alias.name
        node.op = node.op.value
        node.propname = node.propname.name
        node.value = node.value.value

    def walk_RequestFilterNode(self, node, children_retval):
        node.search = node.search.value

    def walk_CreateStatementNode(self, node, children_retval):
        node.typed.properties = [
            prop.value
            for prop in node.typed.properties
        ]

    def walk_ReadStatementNode(self, node, children_retval):
        node.filter = node.filter.search
        node.aliases = [
            alias.name
            for alias in node.aliases
        ]

    def walk_UpdateStatementNode(self, node, children_retval):
        node.updates = [
            update.value
            for update in node.updates
        ]

    def walk_DeleteStatementNode(self, node, children_retval):
        node.filter = node.filter.search
        node.aliases = [
            alias.name
            for alias in node.aliases
        ]

    def walk_WalkthroughBlock(self, node, children_retval):
        node.statements = list(reversed(node.statements))

    def walk_RequestNode(self, node, children_retval):
        if node.walkthrough is not None:
            node.walkthrough = node.walkthrough.statements

        else:
            node.walkthrough = []

        node.crud = node.crud.statements

        return node

        aliased_sets = self.do_walkthrough(node.walkthrough)
        result = self.do_crud(node.crud, aliased_sets)

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
            store = self._get_storage(initial_req.typed)

            context = store.search(initial_req.typed.query)

            if initial_req.alias is not None:
                aliased_sets[initial_req.alias] = context

            if statements[0].follow is not None:
                algo = Follow(self.graphmgr, statements[0].follow)
                context = self.graphmgr.call_algorithm(context, algo)

            for statement in statements[1:]:
                algo = Filter(self.graphmgr, statement.filter.typed.query)
                context = self.graphmgr.call_algorithm(context, algo)

                if statement.filter.alias is not None:
                    aliased_sets[statement.filter.alias] = context

                if statement.follow is not None:
                    algo = Follow(self.graphmgr, statement.follow)
                    context = self.graphmgr.call_algorithm(context, algo)

        return aliased_sets

    def do_crud(self, statements, aliased_sets):
        result = []

        for statement in statements:
            methodname = 'do_{0}'.format(statement.__class__.__name__)
            method = getattr(self, methodname, None)

            if method is not None:
                result += method(statement, aliased_sets)

        return result

    def do_CreateStatementNode(self, statement, aliased_sets):
        if statement.typed.__class__.__name__ == 'NodeTypeNode':
            self.do_create_node(statement.typed, aliased_sets)

        elif statement.typed.__class__.__name__ == 'RelationTypeNode':
            self.do_create_relations(statement.typed, aliased_sets)

        return []

    def do_create_node(self, node, aliased_sets):
        f = self.graphmgr.nodes_store.get_feature('model')
        Model = f('node')

        properties = {
            p.propname: p.value
            for p in node.properties
        }

        obj = Model(
            type_set=[
                t.name
                for t in node.types
            ],
            **properties
        )

        obj.save()

        if node.alias is not None:
            alias = node.alias

            if alias not in aliased_sets:
                aliased_sets[alias] = []

            aliased_sets[alias].append(obj)

    def do_create_relations(self, node, aliased_sets):
        f = self.graphmgr.nodes_store.get_feature('model')
        Model = f('node')

        target = node.links.target
        source = node.links.source

        if target.__class__.__name__ == 'AliasNode':
            target = aliased_sets[target.name]

        elif target.__class__.__name__ == 'NodeFilterNode':
            store = self._get_storage(target)
            target = store.search(target.query)

        if source.__class__.__name__ == 'AliasNode':
            source = aliased_sets[source.name]

        elif source.__class__.__name__ == 'NodeFilterNode':
            store = self._get_storage(source)
            source = store.search(source.query)

        target = [Model(t) for t in target]
        source = [Model(s) for s in source]

        algo = Link(self.graphmgr, node)
        dataset = [
            [s, t]
            for s in source
            for t in target
        ]

        result = self.graphmgr.call_algorithm(dataset, algo)

        for alias, objects in result:
            aliased_sets[alias] = objects

    def do_UpdateStatementNode(self, statement, aliased_sets):
        algo = Update(self.graphmgr, aliased_sets)
        result = self.graphmgr.call_algorithm(statement.assignations, algo)

        for alias, objects in result:
            aliased_sets[alias] = objects

        return []
