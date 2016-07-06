# -*- coding: utf-8 -*-

from link.graph.algorithms.base import Algorithm
from link.graph.algorithms.backward import Backward
from link.graph.algorithms.forward import Forward
from link.graph.algorithms.filter import Filter


class Joint(Algorithm):
    def __init__(
        self,
        graphmgr,
        elements=None,
        nodes=None,
        relationships=None,
        graphs=None,
        *args, **kwargs
    ):
        super(Joint, self).__init__(graphmgr, *args, **kwargs)

        self['elements'] = elements
        self['nodes'] = nodes
        self['relationships'] = relationships
        self['graphs'] = graphs

    def walk(self, nodes, begin, end, algo):
        result = nodes

        for i in range(end):
            if i < begin:
                result = self.graphmgr.call_algorithm(result, algo)

            else:
                result += self.graphmgr.call_algorithm(result, algo)

        return result

    def map(self, mapper, node):
        if self['elements'] is not None:
            self.map_elements(mapper, node)

        elif self['nodes'] is not None:
            self.map_nodes(mapper, node)

        elif self['relationships'] is not None:
            self.map_relationships(mapper, node)

        elif self['graphs'] is not None:
            self.map_graphs(mapper, node)

    def map_elements(self, mapper, node):
        pass

    def map_nodes(self, mapper, node):
        joint = self['nodes']

        if joint.fw != '-':
            nodes = self.walk(
                [node],
                joint.card.begin,
                joint.card.end,
                Forward(self.graphmgr)
            )

        if joint.bw != '-':
            nodes = self.walk(
                [node],
                joint.card.begin,
                joint.card.end,
                Backward(self.graphmgr)
            )

        filter_algo = Filter(self.graphmgr, joint.aelts)

        for node in self.graphmgr.call_algorithm(nodes, filter_algo):
            mapper.emit('joint_nodes', node)

    def map_relationships(self, mapper, node):
        pass

    def map_graphs(self, mapper, node):
        pass

    def reduce(self, reducer, key, nodes):
        return nodes
