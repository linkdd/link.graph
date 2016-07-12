# -*- coding: utf-8 -*-

from link.graph.algorithms import Update, Link


class CRUDOperations(object):
    def __init__(self, graphmgr, *args, **kwargs):
        super(CRUDOperations, self).__init__(*args, **kwargs)

        self.graphmgr = graphmgr

    def _get_storage(self, filter_node):
        if filter_node.__class__.__name__ == 'NodeFilterNode':
            store = self.graphmgr.nodes_store

        elif filter_node.__class__.__name__ == 'RelationFilterNode':
            store = self.graphmgr.relationships_store

        return store.get_feature('fulltext')

    def __call__(self, statements, aliased_sets):
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
