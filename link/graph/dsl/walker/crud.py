# -*- coding: utf-8 -*-


class CRUDOperations(object):
    def __init__(self, graphmgr, *args, **kwargs):
        super(CRUDOperations, self).__init__(*args, **kwargs)

        self.graphmgr = graphmgr

    def __call__(self, statements, aliased_sets):
        result = []

        return result
