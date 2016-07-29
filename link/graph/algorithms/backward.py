# -*- coding: utf-8 -*-

from link.graph.algorithms.base import Algorithm
from link.feature import getfeature


class NodeBreadthBackward(Algorithm):
    def __init__(self, graphmgr, filter_algo, *args, **kwargs):
        super(NodeBreadthBackward, self).__init__(graphmgr, *args, **kwargs)

        self.filter_algo = filter_algo

    def map(self, mapper, node):
        f = getfeature(self.graphmgr.nodes_store, 'fulltext')
        parents = f.search('targets_set:"*:{0}"'.format(node[f._DATA_ID]))

        for parent in parents:
            mapper.emit('backward-breadth', parent)

    def reduce(self, reducer, key, nodes):
        return self.graphmgr.call_algorithm(nodes, self.filter_algo)


class NodeDepthForward(Algorithm):
    def __init__(
        self,
        graphmgr,
        filter_algo,
        cardinality,
        iteration=0,
        *args, **kwargs
    ):
        super(NodeDepthForward, self).__init__(graphmgr, *args, **kwargs)

        self.filter_algo = filter_algo
        self.start = cardinality.begin
        self.stop = cardinality.end
        self.iteration = 0

    def map(self, mapper, node):
        f = getfeature(self.graphmgr.nodes_store, 'fulltext')
        parents = f.search('targets_set:"*:{0}"'.format(node[f._DATA_ID]))

        for parent in parents:
            mapper.emit('backward-depth', parent)

    def reduce(self, reducer, key, values):
        raise NotImplementedError()


class RelationBreadthBackward(Algorithm):
    pass


class RelationDepthBackward(Algorithm):
    pass
