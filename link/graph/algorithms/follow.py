# -*- coding: utf-8 -*-

from link.graph.algorithms.base import Algorithm
from link.graph.algorithms.backward import NodeBackward, RelationBackward
from link.graph.algorithms.forward import NodeForward, RelationForward
from link.graph.algorithms.filter import Filter


class Follow(Algorithm):
    def __init__(self, graphmgr, node, *args, **kwargs):
        super(Follow, self).__init__(graphmgr, *args, **kwargs)

        self['direction'] = node.direction
        self['type'] = node.type
        self['cardinality'] = node.cardinality
        self['filter'] = node.filter

    def map(self, mapper, node):
        if self['filter'].__class__.__name__ == 'NodeFilterNode':
            self.map_nodes(mapper, node)

        elif self['filter'].__class__.__name__ == 'RelationFilterNode':
            self.map_relations(mapper, node)

    def map_nodes(self, mapper, node):
        pass

    def map_relations(self, mapper, node):
        pass

    def reduce(self, reducer, key, values):
        return values
