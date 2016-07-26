# -*- coding: utf-8 -*-

from link.graph.algorithms.base import Algorithm


class Update(Algorithm):
    def __init__(self, graphmgr, aliased_sets, *args, **kwargs):
        super(Update, self).__init__(graphmgr, *args, **kwargs)

        self.aliased_sets = aliased_sets

    def map(self, mapper, assign):
        if assign.alias in self.aliased_sets:
            algo = _Update(self.graphmgr, assign)
            dataset = self.aliased_sets[assign.alias]

            alias, objects = self.graphmgr.call_algorithm(dataset, algo)

            for obj in objects:
                mapper.emit(alias, obj)

    def reduce(self, reducer, alias, objects):
        return alias, objects


class _Update(Algorithm):
    def __init__(self, graphmgr, assign, *args, **kwargs):
        super(_Update, self).__init__(graphmgr, *args, **kwargs)

        self.assign = assign

    def map(self, mapper, obj):
        name = self.assign.__class__.__name__

        if name == 'UpdateSetPropertyNode':
            self.map_set(mapper, obj)

        elif name == 'UpdateAddPropertyNode':
            self.map_addtoset(mapper, obj)

        elif name == 'UpdateUnsetPropertyNode':
            self.map_unset(mapper, obj)

        elif name == 'UpdateDelPropertyNode':
            self.map_delfromset(mapper, obj)

        obj.save()

        mapper.emit(self.assign.alias, obj)

    def map_set(self, mapper, obj):
        obj[self.assign.propname] = self.assign.value

    def map_addtoset(self, mapper, obj):
        obj[self.assign.propname] = set([self.assign.value])

    def map_unset(self, mapper, obj):
        if self.assign.propname in obj:
            del obj[self.assign.propname]

    def map_delfromset(self, mapper, obj):
        obj[self.assign.propname] = set(['-{0}'.format(self.assign.value)])

    def reduce(self, reducer, alias, objects):
        return alias, objects
