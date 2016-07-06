# -*- coding: utf-8 -*-

from link.graph.algorithms.base import Algorithm


class Backward(Algorithm):
    def map(self, mapper, node):
        f = self.graphmgr.nodes_store.get_feature('fulltext')
        parents = f.search('targets_set:"*:{0}"'.format(node[f.DATA_ID]))

        for parent in parents:
            mapper.emit('backward', parent)

    def reduce(self, reducer, key, nodes):
        return nodes
