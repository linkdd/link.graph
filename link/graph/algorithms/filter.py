# -*- coding: utf-8 -*-

from link.utils.filter import Filter as MongoFilter
from link.graph.algorithms.base import Algorithm
from link.fulltext.filter import FulltextMatch


class WalkFilter(Algorithm):
    def __init__(self, graphmgr, query, *args, **kwargs):
        super(WalkFilter, self).__init__(graphmgr, *args, **kwargs)

        self['query'] = query

        self.query = FulltextMatch(query)

    def map(self, mapper, document):
        if self.query(document):
            mapper.emit('walk-filtered', document)

    def reduce(self, reducer, key, values):
        return values


class CRUDFilter(Algorithm):
    def __init__(self, graphmgr, mfilter, *args, **kwargs):
        super(CRUDFilter, self).__init__(graphmgr, *args, **kwargs)

        self.mfilter = MongoFilter(mfilter)

    def map(self, mapper, document):
        if self.mfilter.match(document):
            mapper.emit('crud-filtered', document)

    def reduce(self, reducer, key, values):
        return values
