# -*- coding: utf-8 -*-


class Algorithm(dict):
    def __init__(self, graphmgr, *args, **kwargs):
        super(Algorithm, self).__init__(*args, **kwargs)

        self['__class__'] = self.__class__.__name__
        self.graphmgr = graphmgr

    def map(self, mapper, inputdata):
        raise NotImplementedError()

    def reduce(self, reducer, key, values):
        raise NotImplementedError()
