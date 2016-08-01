# -*- coding: utf-8 -*-

from link.fulltext import FulltextMatch
from link.feature import getfeature


def getmapfunc(key, match):
    def mapfunc(mapper, item):
        if match(item):
            mapper.emit(key, item)

    return mapfunc


def reducefunc(reducer, key, values):
    return values


class Walkthrough(object):
    def __init__(self, graphmgr, *args, **kwargs):
        super(Walkthrough, self).__init__(*args, **kwargs)

        self.graphmgr = graphmgr

    def __call__(self, statements):
        aliased_sets = {}

        last_alias = None

        for node in statements:
            for fromstmt in node.froms:
                if fromstmt.alias not in aliased_sets:
                    aliased_sets[fromstmt.alias] = {
                        'type': 'nodes',
                        'dataset': self.select_nodes(fromstmt, aliased_sets)
                    }

                last_alias = fromstmt.alias

            for path in node.path:
                nodes = aliased_sets[last_alias]

                for stmt in path.through:
                    if stmt.alias is not None and stmt.alias in aliased_sets:
                        rels = aliased_sets[stmt.alias]

                    else:
                        rels = self.select_relationships(
                            nodes,
                            stmt,
                            aliased_sets
                        )

                    if stmt.alias is not None:
                        aliased_sets[stmt.alias] = {
                            'type': 'relationships',
                            'dataset': rels
                        }

                    nodes = self.walk_nodes(nodes, rels, stmt.wmode)

                for to in path.to:
                    aliased_sets[to.alias] = {
                        'type': 'nodes',
                        'dataset': self.filter_nodes(nodes, to)
                    }

                    last_alias = to.alias

        return aliased_sets

    def select_nodes(self, nodes, fromstmt, aliased_sets):
        if fromstmt.set_ == 'NODES':
            store = getfeature(self.graphmgr.nodes_storage, 'fulltext')
            return store.search(fromstmt.filter)

        else:
            match = FulltextMatch(fromstmt.filter)

            return self.graphmgr.mapreduce(
                getmapfunc('walkthrough-select-nodes', match),
                reducefunc,
                aliased_sets[fromstmt.set_]
            )

    def select_relationships(self, nodes, throughnode, aliased_sets):
        if throughnode.set_ == 'RELS':
            store = getfeature(self.graphmgr.relationships_storage, 'fulltext')
            return store.search(throughnode.filter)

        else:
            match = FulltextMatch(throughnode.filter)

            return self.graphmgr.mapreduce(
                getmapfunc('walkthrough-select-relationships', match),
                reducefunc,
                aliased_sets[throughnode.set_]
            )

    def forward_breadth_nodes(self, nodes, rel_ids):
        store = getfeature(self.graphmgr.nodes_storage, 'fulltext')
        Model = getfeature(self.graphmgr.nodes_storage, 'model')
        Node = Model('node')

        node_ids = [
            target.split(':')[1]
            for node in nodes
            for target in node['targets_set']
            if target.split(':') in rel_ids
        ]

        query = '{0}:({1})'.format(
            Node._DATA_ID,
            ' OR '.join(node_ids)
        )

        return store.search(query)

    def backward_breadth_nodes(self, nodes, rel_ids):
        store = getfeature(self.graphmgr.nodes_storage, 'fulltext')
        Model = getfeature(self.graphmgr.nodes_storage, 'model')
        Node = Model('node')

        node_ids = [
            node[Node._DATA_ID]
            for node in nodes
        ]

        query = 'targets_set:({0})'.format(
            ' OR '.join([
                '"{0}:{1}"'.format(rel_id, node_id)
                for rel_id in rel_ids
                for node_id in node_ids
            ])
        )

        return store.search(query)

    def breadth_nodes(self, nodes, rel_ids, begin, end, func):
        result = []

        if end is not None:
            for i in range(end):
                nodes = func(nodes, rel_ids)

                if i >= begin:
                    result += nodes

        else:
            i = 0

            while nodes:
                nodes = func(nodes, rel_ids)

                if i >= begin:
                    result += nodes

                i += 1

        return result

    def walk_nodes(self, startnodes, rels, walkmode):
        Model = getfeature(self.graphmgr.relationships_storage, 'model')
        Relationship = Model('relationship')
        rel_ids = [r[Relationship._DATA_ID] for r in rels]

        result = []

        if walkmode.type == 'BEADTH':
            if walkmode.direction in ['FORWARD', 'BOTH']:
                result += self.breadth_nodes(
                    startnodes, rel_ids,
                    walkmode.begin, walkmode.end,
                    self.forward_breadth_nodes
                )

            if walkmode.direction in ['BACKWARD', 'BOTH']:
                result += self.breadth_nodes(
                    startnodes, rel_ids,
                    walkmode.begin, walkmode.end,
                    self.backward_breadth_nodes
                )

        elif walkmode.type == 'DEPTH':
            raise NotImplementedError()

        return result

    def filter_nodes(self, nodes, to):
        match = FulltextMatch(to.filter)

        return self.graphmgr.mapreduce(
            getmapfunc('walkthrough-filter-nodes', match),
            reducefunc,
            nodes
        )
