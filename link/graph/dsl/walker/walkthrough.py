# -*- coding: utf-8 -*-


class Walkthrough(object):
    def __init__(self, graphmgr, *args, **kwargs):
        super(Walkthrough, self).__init__(*args, **kwargs)

        self.graphmgr = graphmgr

    def __call__(self, node):
        aliased_sets = {}

        return aliased_sets
