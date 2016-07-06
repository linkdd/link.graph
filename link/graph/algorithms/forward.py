# -*- coding: utf-8 -*-

from link.graph.algorithms.base import Algorithm


class NodeForward(Algorithm):
    def __init__(self, graphmgr, filter_algo, *args, **kwargs):
        super(NodeForward, self).__init__(graphmgr, *args, **kwargs)

        self.filter_algo = filter_algo

    def map(self, mapper, node):
        targets = node.get('targets_set', [])

        if not isinstance(targets, list):
            targets = [targets]

        for target in targets:
            _, node_id = target.split(':')
            mapper.emit('forward', node_id)

    def reduce(self, reducer, key, node_ids):
        nodes = self.graphmgr.nodes_store[tuple(node_ids)]

        return self.graphmgr.call_algorithm(nodes, self.filter_algo)


class RelationForward(Algorithm):
    pass
