# -*- coding: utf-8 -*-

from link.graph.algorithms.base import Algorithm


class Link(Algorithm):
    def __init__(self, graphmgr, node, *args, **kwargs):
        super(Link, self).__init__(graphmgr, *args, **kwargs)

        self.node = node

    def map(self, mapper, pair):
        f = self.graphmgr.relationships_store.get_feature('model')
        Relationship = f('relationship')
        f = self.graphmgr.nodes_store.get_feature('model')
        Node = f('node')

        properties = {
            p.propname: p.value
            for p in self.node.properties
        }

        obj = Relationship(
            type_set=[
                t.name
                for t in self.node.types
            ],
            **properties
        )

        obj.save()

        if self.node.alias is not None:
            mapper.emit(self.node.alias, obj)

        pair[0].targets_set = set(
            '{0}:{1}'.format(
                obj[Relationship._DATA_ID],
                pair[1][Node._DATA_ID]
            )
        )
        pair[0].n_rels_counter = 1
        pair[0].neighbors_counter = 1
        pair[0].n_targets_counter = 1
        pair[0].save()

        pair[1].n_rels_counter = 1
        pair[1].neighbors_counter = 1
        pair[1].save()

    def reduce(self, reducer, alias, objects):
        return alias, objects
