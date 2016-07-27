# -*- coding: utf-8 -*-

from link.graph.algorithms import Update, Link, CRUDFilter
from link.graph.dsl.walker.filter import CRUDFilterWalker
from link.feature import getfeature


class CRUDOperations(object):
    def __init__(self, graphmgr, *args, **kwargs):
        super(CRUDOperations, self).__init__(*args, **kwargs)

        self.graphmgr = graphmgr

    def _get_storage(self, filter_node):
        if filter_node.__class__.__name__ == 'NodeFilterNode':
            store = self.graphmgr.nodes_store

        elif filter_node.__class__.__name__ == 'RelationFilterNode':
            store = self.graphmgr.relationships_store

        return getfeature(store, 'fulltext')

    def __call__(self, statements, aliased_sets):
        result = []

        for statement in statements:
            methodname = 'do_{0}'.format(statement.__class__.__name__)
            method = getattr(self, methodname, None)
            local_result = None

            if method is not None:
                local_result = method(statement, aliased_sets)

            if local_result is not None:
                result.append(local_result)

        return result

    def do_ReadStatementNode(self, statement, aliased_sets):
        walker = CRUDFilterWalker()
        result = {}

        for alias in statement.filters:
            mfilter = {'$and': [
                walker.walk(subfilter)
                for subfilter in statement.filters[alias]
            ]}

            if len(mfilter['$and']) == 1:
                mfilter = mfilter['$and'][0]

            elif len(mfilter['$and']) == 0:
                mfilter = {}

            algo = CRUDFilter(self.graphmgr, mfilter)
            result[alias] = {
                'type': aliased_sets[alias]['type'],
                'dataset': self.graphmgr.call_algorithm(
                    aliased_sets[alias]['dataset'],
                    algo
                )
            }

        return result

    def do_CreateStatementNode(self, statement, aliased_sets):
        if statement.typed.__class__.__name__ == 'NodeTypeNode':
            self.do_create_node(statement.typed, aliased_sets)

        elif statement.typed.__class__.__name__ == 'RelationTypeNode':
            self.do_create_relations(statement.typed, aliased_sets)

    def do_create_node(self, node, aliased_sets):
        f = getfeature(self.graphmgr.nodes_store, 'model')
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
                aliased_sets[alias] = {
                    'type': 'node',
                    'dataset': []
                }

            aliased_sets[alias]['dataset'].append(obj)

    def do_create_relations(self, node, aliased_sets):
        f = getfeature(self.graphmgr.nodes_store, 'model')
        Model = f('node')

        target = node.links.target
        source = node.links.source

        if target.__class__.__name__ == 'AliasNode':
            target = aliased_sets[target.name]['dataset']

        elif target.__class__.__name__ == 'NodeFilterNode':
            store = self._get_storage(target)
            target = store.search(target.query)

        if source.__class__.__name__ == 'AliasNode':
            source = aliased_sets[source.name]['dataset']

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
            aliased_sets[alias] = {
                'type': 'relationship',
                'dataset': objects
            }

    def do_UpdateStatementNode(self, statement, aliased_sets):
        algo = Update(self.graphmgr, aliased_sets)
        result = self.graphmgr.call_algorithm(statement.assignations, algo)

        for alias, objects in result:
            aliased_sets[alias]['dataset'] = objects

    def do_DeleteStatementNode(self, statement, aliased_sets):
        result = self.do_ReadStatementNode(statement, aliased_sets)

        for alias in result:
            aliasedset = result[alias]

            if aliasedset['type'] == 'node':
                store = self.graphmgr.nodes_store

            elif aliasedset['type'] == 'relationship':
                store = self.graphmgr.relationships_store

            f = getfeature(, 'model')
            Model = f(aliasedset['type'])

            for obj in aliasedset['dataset']:
                if Model._DATA_ID in obj:
                    del store[obj[Model._DATA_ID]]
