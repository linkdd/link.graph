# -*- coding: utf-8 -*-

from link.graph.algorithms.base import Algorithm


class NodeBreadthForward(Algorithm):
    def __init__(self, graphmgr, filter_algo, *args, **kwargs):
        super(NodeBreadthForward, self).__init__(graphmgr, *args, **kwargs)

        self.filter_algo = filter_algo

    def map(self, mapper, node):
        targets = node.get('targets_set', [])

        if not isinstance(targets, list):
            targets = [targets]

        for target in targets:
            _, node_id = target.split(':')
            mapper.emit('forward-breadth', node_id)

    def reduce(self, reducer, key, node_ids):
        nodes = self.graphmgr.nodes_store[tuple(node_ids)]

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
        targets = node.get('targets_set', [])

        if not isinstance(targets, list):
            targets = [targets]

        for target in targets:
            _, node_id = target.split(':')
            mapper.emit('forward-depth', node_id)

    def reduce(self, reducer, key, values):
        raise NotImplementedError()


class RelationBreadthForward(Algorithm):
    pass


class RelationDepthForward(Algorithm):
    pass
