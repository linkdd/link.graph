# -*- coding: utf-8 -*-

from link.feature import getfeature
from link.crdt.map import Map

from copy import deepcopy
from uuid import uuid4


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

    def create_element(self, store, statement, aliased_sets):
        data_id_key = getfeature(store, 'fulltext').DATA_ID
        data_id_val = None

        newelt = Map()

        for elttype in statement.types:
            newelt['type_set'].add(elttype)

        for assign in statement.properties:
            if assign.__class__.__name__ == 'AssignAddNode':
                newelt[assign.propname].add(assign.val)

            elif assign.__class__.__name__ == 'AssignSetNode':
                if assign.propname == data_id_key:
                    data_id_val = assign.val

                else:
                    newelt[assign.propname].assign(assign.val)

        if data_id_val is None:
            data_id_val = str(uuid4())

        store[data_id_val] = newelt

        if statement.alias is not None:
            if statement.alias not in aliased_sets:
                if store is self.graphmgr.nodes_storage:
                    settype = 'nodes'

                elif store is self.graphmgr.relationships_storage:
                    settype = 'relationships'

                aliased_sets[statement.alias] = {
                    'type': settype,
                    'dataset': []
                }

            doc = deepcopy(newelt.current)
            doc[data_id_key] = data_id_val

            aliased_sets[statement.alias]['dataset'].append(doc)

        return newelt, data_id_val

    def do_NodeTypeNode(self, statement, aliased_sets):
        store = self.graphmgr.nodes_storage
        self.create_element(store, statement, aliased_sets)

    def do_RelationTypeNode(self, statement, aliased_sets):
        rstore = getfeature(self.graphmgr.relationships_storage, 'fulltext')
        nstore = getfeature(self.graphmgr.nodes_storage, 'fulltext')

        sources, targets = self.get_links(statement.links, aliased_sets)

        for source in sources:
            newrel, data_id = self.create_element(
                rstore,
                statement,
                aliased_sets
            )

            source_id = source[nstore.DATA_ID]
            source = Map(value=source)

            for target in targets:
                source['targets_set'].add(
                    '{0}:{1}'.format(
                        newrel[rstore.DATA_ID],
                        target[nstore.DATA_ID]
                    )
                )

            n = len(targets)
            source['n_targets_counter'].increment(n)
            source['n_rels_counter'].increment(n)
            source['neighbors_counter'].increment(n)

            self.graphmgr.nodes_storage[source_id] = source

            for target in targets:
                target_id = target[nstore.DATA_ID]
                target = Map(value=target)

                target['n_rels_counter'].increment(n)

                as_target = nstore.search(
                    'targets_set:"*:{0}"'.format(target_id)
                )

                target['neighbors_counter'].decrement(
                    abs(len(as_target) + target['n_targets_counter'].current)
                )

                self.graphmgr.nodes_storage[target_id] = target

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

    def compute_result(self, data_id, ids, result):
        computed = []

        for i, crdt in enumerate(result):
            doc = crdt.current
            doc[data_id] = ids[i]
            computed.append(doc)

        return computed

    def do_UpdateSetPropertyNode(self, statement, aliased_sets):
        result = {}

        alias = statement.alias
        key = '{0}_register'.format(statement.propname)

        if aliased_sets[alias]['type'] == 'nodes':
            store = self.graphmgr.nodes_storage

        elif aliased_sets[alias]['type'] == 'relationships':
            store = self.graphmgr.relationships_storage

        data_id = getfeature(store, 'fulltext').DATA_ID

        ids = [
            elt[data_id]
            for elt in aliased_sets[alias]['dataset']
        ]

        result[alias] = store[ids]

        for elt in result[alias]:
            elt[key].assign(statement.value)

        store[ids] = result[alias]
        result[alias] = self.compute_result(data_id, ids, result[alias])

        return result

    def do_UpdateAddPropertyNode(self, statement, aliased_sets):
        result = {}

        alias = statement.alias
        key = '{0}_set'.format(statement.propname)

        if aliased_sets[alias]['type'] == 'nodes':
            store = self.graphmgr.nodes_storage

        elif aliased_sets[alias]['type'] == 'relationships':
            store = self.graphmgr.relationships_storage

        data_id = getfeature(store, 'fulltext').DATA_ID

        ids = [
            elt[data_id]
            for elt in aliased_sets[alias]['dataset']
        ]

        result[alias] = store[ids]

        for elt in result[alias]:
            elt[key].add(statement.value)

        store[ids] = result[alias]
        result[alias] = self.compute_result(data_id, ids, result[alias])

        return result

    def do_UpdateUnsetPropertyNode(self, statement, aliased_sets):
        result = {}

        alias = statement.alias
        key = '{0}_register'.format(statement.propname)

        if aliased_sets[alias]['type'] == 'nodes':
            store = self.graphmgr.nodes_storage

        elif aliased_sets[alias]['type'] == 'relationships':
            store = self.graphmgr.relationships_storage

        data_id = getfeature(store, 'fulltext').DATA_ID

        ids = [
            elt[data_id]
            for elt in aliased_sets[alias]['dataset']
        ]

        result[alias] = store[ids]

        for elt in result[alias]:
            del elt[key]

        store[ids] = result[alias]
        result[alias] = self.compute_result(data_id, ids, result[alias])

        return result

    def do_UpdateDelPropertyNode(self, statement, aliased_sets):
        result = {}

        alias = statement.alias
        key = '{0}_set'.format(statement.propname)

        if aliased_sets[alias]['type'] == 'nodes':
            store = self.graphmgr.nodes_storage

        elif aliased_sets[alias]['type'] == 'relationships':
            store = self.graphmgr.relationships_storage

        data_id = getfeature(store, 'fulltext').DATA_ID

        ids = [
            elt[data_id]
            for elt in aliased_sets[alias]['dataset']
        ]

        result[alias] = store[ids]

        for elt in result[alias]:
            elt[key].discard(statement.value)

        store[ids] = result[alias]
        result[alias] = self.compute_result(data_id, ids, result[alias])

        return result

    def do_UpdateStatementNode(self, statement, aliased_sets):
        result = {}

        for update in statement.updates:
            methodname = 'do_{0}'.format(update.__class__.__name__)
            method = getattr(self, methodname, None)

            if method is not None:
                local_result = method(update, aliased_sets)
                result.update(local_result)

        return result

    def do_DeleteStatementNode(self, statement, aliased_sets):
        def map_remove_relation_id(mapper, rel_id):
            store = self.graphmgr.nodes_storage

            for node in store.search(
                'targets_set:"{0}:*"'.format(rel_id)
            ):
                mapper.emit('rel', {
                    'node_id': node,
                    'relation': rel_id
                })

        def reduce_remove_relation_id(mapper, key, items):
            store = self.graphmgr.nodes_storage

            for item in items:
                removes = [
                    target
                    for target in item['node']['targets_set']
                    if target.startswith('{0}:'.format(item['relation']))
                ]

                node_id = item['node'][store.DATA_ID]
                node = store[node_id]

                for remove in removes:
                    node['targets_set'].discard(remove)

                store[node_id] = node

        def map_deletable_elements(mapper, node):
            nodes_storage = self.graphmgr.nodes_storage
            store = getfeature(nodes_storage, 'fulltext')

            node_id = node[store.DATA_ID]

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
                store = self.graphmgr.nodes_storage

                del store[tuple(values)]

            elif key == 'deletable-elements-rels':
                store = self.graphmgr.relationships_storage

                ids = tuple(set(values))
                del store[ids]

                self.graphmgr.mapreduce(
                    'delete-rels:{0}'.format(reducer.identifier),
                    map_remove_relation_id,
                    reduce_remove_relation_id,
                    ids
                )

        for alias in statement.aliases:
            aliased_set = aliased_sets[alias]

            if aliased_set['type'] == 'nodes':
                self.graphmgr.mapreduce(
                    'delete-nodes',
                    map_deletable_elements,
                    reduce_deletable_elements,
                    aliased_set['dataset']
                )

            elif aliased_set['type'] == 'relationships':
                store = self.graphmgr.relationships_storage

                self.graphmgr.mapreduce(
                    'delete-rels',
                    map_remove_relation_id,
                    reduce_remove_relation_id,
                    [
                        rel[store.DATA_ID]
                        for rel in aliased_set['dataset']
                    ]
                )

            else:
                continue
