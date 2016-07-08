# -*- coding: utf-8 -*-

from link.graph.algorithms.base import Algorithm
from link.fulltext.filter import FulltextMatch


class Filter(Algorithm):
    def __init__(self, graphmgr, step, *args, **kwargs):
        super(Filter, self).__init__(graphmgr, *args, **kwargs)

        self['query'] = step.query
        self['alias'] = step.alias

        self.query = FulltextMatch(step.query)

    def map(self, mapper, document):
        if self.query(document):
            mapper.emit('filtered', document)

    def reduce(self, reducer, key, values):
        return values, self['alias']
