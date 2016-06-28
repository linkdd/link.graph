# -*- coding: utf-8 -*-


class Algorithm(object):
    def __init__(self, graphmgr, *args, **kwargs):
        super(Algorithm, self).__init__(*args, **kwargs)

        self.graphmgr

    def map(self, mapper, inputdata):
        raise NotImplementedError()

    def reduce(self, reducer, key, values):
        raise NotImplementedError()
