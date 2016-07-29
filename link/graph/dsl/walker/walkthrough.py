# -*- coding: utf-8 -*-

from link.graph.algorithms.filter import WalkFilter
from link.graph.algorithms.follow import Follow
from link.feature import getfeature


class Walkthrough(object):
    def __init__(self, graphmgr, *args, **kwargs):
        super(Walkthrough, self).__init__(*args, **kwargs)

        self.graphmgr = graphmgr

    def _get_storage(self, filter_node):
        if filter_node.__class__.__name__ == 'NodeFilterNode':
            store = self.graphmgr.nodes_store

        elif filter_node.__class__.__name__ == 'RelationFilterNode':
            store = self.graphmgr.relationships_store

        return getfeature(store, 'fulltext')

    def _get_alias_type(self, filter_node):
        if filter_node.__class__.__name__ == 'NodeFilterNode':
            return 'node'

        elif filter_node.__class__.__name__ == 'RelationFilterNode':
            return 'relationship'

        return 'unknown'

    def alias_and_follow_statement(self, statement, context, aliased_sets):
        if statement.filter.alias is not None:
            aliased_sets[statement.filter.alias] = {
                'type': self._get_alias_type(statement.filter.typed),
                'dataset': context
            }

        if statement.follow is not None:
            algo = Follow(self.graphmgr, statement.follow)
            context = self.graphmgr.call_algorithm(context, algo)

        return context

    def do_first_statement(self, statement, aliased_sets):
        store = self._get_storage(statement.filter.typed)
        context = store.search(statement.filter.typed.query)

        return self.alias_and_follow_statement(
            statement,
            context,
            aliased_sets
        )

    def do_statement(self, statement, context, aliased_sets):
        algo = WalkFilter(self.graphmgr, statement.filter.typed.query)
        context = self.graphmgr.call_algorithm(context, algo)

        return self.alias_and_follow_statement(
            statement,
            context,
            aliased_sets
        )

    def __call__(self, statements):
        context = None
        aliased_sets = {}

        if len(statements) > 0:
            context = self.do_first_statement(statements[0], aliased_sets)

            for statement in statements[1:]:
                context = self.do_statement(statement, context, aliased_sets)

        return aliased_sets
