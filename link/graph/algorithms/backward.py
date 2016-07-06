# -*- coding: utf-8 -*-

from link.graph.algorithms.base import Algorithm


class NodeBackward(Algorithm):
    def __init__(self, graphmgr, filter_algo, *args, **kwargs):
        super(NodeBackward, self).__init__(graphmgr, *args, **kwargs)

        self.filter_algo = filter_algo

    def map(self, mapper, node):
        f = self.graphmgr.nodes_store.get_feature('fulltext')
        parents = f.search('targets_set:"*:{0}"'.format(node[f.DATA_ID]))

        for parent in parents:
            mapper.emit('backward', parent)

    def reduce(self, reducer, key, nodes):
        return self.graphmgr.call_algorithm(nodes, self.filter_algo)


class RelationBackward(Algorithm):
    pass
