# -*- coding: utf-8 -*-

from link.feature import getfeature


class CRUDOperations(object):
    def __init__(self, graphmgr, *args, **kwargs):
        super(CRUDOperations, self).__init__(*args, **kwargs)

        self.graphmgr = graphmgr

    def __call__(self, statements, aliased_sets):
        result = []

        for statement in statements:
            methodname = 'do_{0}'.format(statement.__class__.__name__)
            method = getattr(self, methodname, None)

            if method is not None:
                stmtret = method(statement, aliased_sets)

                if stmtret is not None:
                    result.append(stmtret)

        return result

    def get_links(self, statement, aliased_sets):
        store = getfeature(self.graphmgr.nodes_storage, 'fulltext')

        sources = []
        targets = []

        if statement.source.__class__.__name__ == 'TypedFilterNode':
            sources = store.search(statement.source.query)

        elif statement.source.__class__.__name__ == 'AliasNode':
            sources = aliased_sets[statement.source.name]['dataset']

        if statement.target.__class__.__name__ == 'TypedFilterNode':
            targets = store.search(statement.target.query)

        elif statement.target.__class__.__name__ == 'AliasNode':
            targets = aliased_sets[statement.target.name]['dataset']

        return sources, targets

    def create_element(self, model, statement, aliased_sets):
        newelt = Model()
        newelt.type_set = set(statement.types)

        assigns = {}

        for assign in statement.properties:
            if assign.__class__.__name == 'AssignAddNode':
                assigns.setdefault(assign.propname, set()).add(assign.val)

            elif assign.__class__.__name__ == 'AssignSetNode':
                assigns[assign.propname] = assign.val

        for propname in assigns:
            val = assigns[propname]
            setattr(newelt, propname, val)

        newelt.save()

        if statement.alias is not None:
            if statement.alias not in aliased_sets:
                aliased_sets[statement.alias] = {
                    'type': 'node',
                    'dataset': []
                }

            aliased_sets[statement.alias]['dataset'].append(newelt)

        return newelt

    def do_NodeTypeNode(self, statement, aliased_sets):
        store = self.graphmgr.nodes_storage
        Model = getfeature(store, 'model')
        Node = Model('node')

        self.create_element(Node, statement, aliased_sets)

    def do_RelationTypeNode(self, statement, aliased_sets):
        rstore = getfeature(self.graphmgr.relationships_storage, 'fulltext')
        RModel = getfeature(self.graphmgr.relationships_storage, 'model')
        Relationship = RModel('relationship')

        nstore = getfeature(self.graphmgr.nodes_storage, 'fulltext')
        NModel = getfeature(self.graphmgr.nodes_storage, 'model')
        Node = NModel('node')

        sources, targets = self.get_links(statement.links, aliased_sets)

        for source in sources:
            newrel = self.create_element(
                Relationship,
                statement,
                aliased_sets
            )

            links = set(
                '{0}:{1}'.format(
                    newrel[Relationship._DATA_ID],
                    target[Node._DATA_ID]
                )
                for target in targets
            )

            source.targets_set = links
            source.n_targets_counter = len(links)
            source.n_rels_counter = len(links)
            source.neighbors_counter = len(targets)

            source.save()

            for target in targets:
                target.n_rels_counter = len(links)

                as_target = nstore.search(
                    'targets_set:"*:{0}"'.format(
                        target[Node._DATA_ID]
                    )
                )

                increment = target.neighbors_counter
                increment -= target.n_targets + len(as_target)
                increment = abs(increment)

                target.neighbors_counter = increment
                target.save()

    def do_CreateStatementNode(self, statement, aliased_sets):
        methodname = 'do_{0}'.format(statement.typed.__class__.__name__)
        method = getattr(self, methodname, None)

        if method is not None:
            return method(statement.typed, aliased_sets)

    def do_ReadStatementNode(self, statement, aliased_sets):
        result = {}

        for alias in statement.aliases:
            result[alias] = aliased_sets[alias]['dataset']

        return result

    def do_UpdateStatementNode(self, statement, aliased_sets):
        raise NotImplementedError()

    def do_DeleteStatementNode(self, statement, aliased_sets):
        for alias in statement.aliases:
            aliased_set = aliased_sets[alias]

            if aliased_set['type'] == 'nodes':
                def map_deletable_elements(mapper, node):
                    nodes_storage = self.graphmgr.nodes_storage
                    store = getfeature(nodes_storage, 'fulltext')
                    ModelFactory = getfeature(nodes_storage, 'model')
                    Model = ModelFactory('node')

                    node_id = node[Model._DATA_ID]

                    mapper.emit('deletable-elements-nodes', node_id)

                    for target in node['targets_set']:
                        mapper.emit(
                            'deletable-elements-rels',
                            target.split(':')[0]
                        )

                    for prev in store.search(
                        'targets_set:"*:{0}"'.format(node_id)
                    ):
                        for target in prev['targets_set']:
                            mapper.emit(
                                'deletable-elements-rels',
                                target.split(':')[0]
                            )

                def reduce_deletable_elements(reducer, key, values):
                    if key == 'deletable-elements-nodes':
                        nodes_storage = self.graphmgr.nodes_storage
                        store = getfeature(nodes_storage, 'fulltext')

                        del store[tuple(values)]

                    elif key == 'deletable-elements-rels':
                        store = self.graphmgr.relationships_storage

                        ids = tuple(set(values))
                        del store[ids]

                self.graphmgr.mapreduce(
                    map_deletable_elements,
                    reduce_deletable_elements,
                    aliased_set[alias]['dataset']
                )

            elif aliased_sets['type'] == 'relationships':
                store = self.graphmgr.relationships_storage
                ModelFactory = getfeature(store, 'model')
                Model = ModelFactory('relationship')

                # TODO: remove relationships from targets

            else:
                continue
