# -*- coding: utf-8 -*-

from link.graph.algorithms.base import Algorithm


class Forward(Algorithm):
    def map(self, mapper, node):
        targets = node.get('targets_set', [])

        if not isinstance(targets, list):
            targets = [targets]

        for target in targets:
            _, node_id = target.split(':')
            mapper.emit('forward', node_id)

    def reduce(self, reducer, key, node_ids):
        return self.graphmgr.nodes_store[tuple(node_ids)]
