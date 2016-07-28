# -*- coding: utf-8 -*-

from link.graph.algorithms.forward import NodeBreadthBackward
from link.graph.algorithms.forward import NodeBreadthForward
from link.graph.algorithms.filter import WalkFilter
from link.graph.algorithms.base import Algorithm


class Follow(Algorithm):
    def __init__(self, graphmgr, node, *args, **kwargs):
        super(Follow, self).__init__(graphmgr, *args, **kwargs)

        self['direction'] = node.direction
        self['type'] = node.type
        self['cardinality'] = node.cardinality
        self['filter'] = node.filter

    def map(self, mapper, node):
        if self['filter'].__class__.__name__ == 'NodeFilterNode':
            if self['type'] == 'BREADTH':
                mapper.emit('follow-node-breadth', node)

            elif self['type'] == 'DEPTH':
                mapper.emit('follow-node-depth', node)

        elif self['filter'].__class__.__name__ == 'RelationFilterNode':
            if self['type'] == 'BREADTH':
                mapper.emit('follow-relation-breadth', node)

            elif self['type'] == 'DEPTH':
                mapper.emit('follow-relation-depth', node)

    def reduce(self, reducer, key, values):
        methods = {
            'follow-node-breadth': self.reduce_node_breadth,
            'follow-node-depth': self.reduce_node_depth,
            'follow-relation-breadth': self.reduce_relaton_breadth,
            'follow-relation-depth': self.reduce_relaton_depth
        }

        return methods[key](values)

    def walk_nodes(self, dataset, algo):
        start, stop = self['cardinality'].begin, self['cardinality'].end
        result = []

        for i in range(stop):
            dataset = self.graphmgr.call_algorithm(dataset, algo)

            if i >= start:
                result += dataset

        return result

    def reduce_node_breadth(self, dataset):
        result = []

        filter_algo = WalkFilter(self.graphmgr, self['filter'].query)

        if self['direction'] in ['FORWARD', 'BOTH']:
            algo = NodeBreadthForward(self.graphmgr, filter_algo)
            result += self.walk_nodes(dataset, algo)

        if self['direction'] in ['BACKWARD', 'BOTH']:
            algo = NodeBreadthBackward(self.graphmgr, filter_algo)
            result += self.walk_nodes(dataset, algo)

        return result

    def reduce_node_depth(self, dataset):
        return []

    def reduce_relations_breadth(self, dataset):
        return []

    def reduce_relations_depth(self, dataset):
        return []
