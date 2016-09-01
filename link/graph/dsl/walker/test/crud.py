# -*- coding: utf-8 -*-

from b3j0f.utils.ut import UTCase
from mock import MagicMock, patch
from unittest import main

from link.graph.dsl.walker.crud import CRUDOperations
from link.crdt.map import Map
from six import string_types


class TestCRUD(UTCase):
    def _getfeature(self, middleware, featurename):
        expected = []

        if middleware is self.graphmgr.nodes_storage:
            expected = self.expected_nodes

        elif middleware is self.graphmgr.relationships_storage:
            expected = self.expected_rels

        feature = MagicMock()

        if featurename == 'fulltext':
            feature.DATA_ID = '_id'
            feature.search.side_effect = lambda name: expected[name]

        return feature

    def _mapreduce(self, identifier, mapfunc, reducefunc, dataset):
        mapped = {}

        def mapper_emit(key, item):
            key = (identifier, key)

            if key not in mapped:
                mapped[key] = []

            mapped[key].append(item)

        mapper = MagicMock()
        mapper.emit.side_effect = mapper_emit

        for item in dataset:
            mapfunc(mapper, item)

        result = []

        for identifier, key in mapped:
            reducer = MagicMock()
            reducer.identifier = identifier
            result.append(
                reducefunc(reducer, key, mapped[(identifier, key)])
            )

        return result

    def _get_nodes(self, ids):
        if not isinstance(ids, string_types):
            return [
                self.nodes[_id]
                for _id in ids
            ]

        else:
            return self.nodes[ids]

    def _get_rels(self, ids):
        if not isinstance(ids, string_types):
            return [
                self.relationships[_id]
                for _id in ids
            ]

        else:
            return self.relationships[ids]

    def _set_nodes(self, ids, values):
        if not isinstance(ids, string_types):
            for i, _id in enumerate(ids):
                self.nodes[_id] = values[i]

        else:
            self.nodes[ids] = values

    def _set_rels(self, ids, values):
        if not isinstance(ids, string_types):
            for i, _id in enumerate(ids):
                self.relationships[_id] = values[i]

        else:
            self.relationships[ids] = values

    def _del_nodes(self, ids):
        if not isinstance(ids, string_types):
            for _id in ids:
                del self.nodes[_id]

        else:
            del self.nodes[ids]

    def _del_rels(self, ids):
        if not isinstance(ids, string_types):
            for _id in ids:
                del self.relationships[_id]

        else:
            del self.relationships[ids]

    def _contain_node(self, _id):
        return _id in self.nodes

    def _contain_rel(self, _id):
        return _id in self.relationships

    def setUp(self):
        self.graphmgr = MagicMock()
        self.graphmgr.mapreduce.side_effect = self._mapreduce

        self.nodes = {}
        nodes_storage = MagicMock()
        nodes_storage.__getitem__.side_effect = self._get_nodes
        nodes_storage.__setitem__.side_effect = self._set_nodes
        nodes_storage.__delitem__.side_effect = self._del_nodes
        nodes_storage.__contains__.side_effect = self._contain_node

        self.relationships = {}
        relationships_storage = MagicMock()
        relationships_storage.__getitem__.side_effect = self._get_rels
        relationships_storage.__setitem__.side_effect = self._set_rels
        relationships_storage.__delitem__.side_effect = self._del_rels
        relationships_storage.__contains__.side_effect = self._contain_rel

        self.graphmgr.nodes_storage = nodes_storage
        self.graphmgr.relationships_storage = relationships_storage

        self.crud = CRUDOperations(self.graphmgr)

        patcher = patch('link.graph.dsl.walker.crud.getfeature')
        self.getfeature = patcher.start()
        self.getfeature.side_effect = self._getfeature
        self.addCleanup(patcher.stop)

        self.expected_nodes = {}
        self.expected_rels = {}

    def tearDown(self):
        self.expected_nodes = {}
        self.expected_rels = {}


class TestNodeCRUD(TestCRUD):
    def test_create_node(self):
        stmt = MagicMock()
        stmt.__class__.__name__ = 'CreateStatementNode'
        stmt.typed.__class__.__name__ = 'NodeTypeNode'
        stmt.typed.types = ['n1', 'n2']

        assign0 = MagicMock()
        assign0.__class__.__name__ = 'AssignAddNode'
        assign0.propname = 'foo_set'
        assign0.val = 'bar'

        assign1 = MagicMock()
        assign1.__class__.__name__ = 'AssignSetNode'
        assign1.propname = 'bar_register'
        assign1.val = 'baz'

        stmt.typed.properties = [assign0, assign1]
        stmt.typed.alias = 'node0'

        aliased_sets = {}
        result = self.crud([stmt], aliased_sets)

        self.assertEqual(len(result), 0)
        self.assertIn('node0', aliased_sets)
        self.assertEqual(aliased_sets['node0']['type'], 'nodes')
        self.assertEqual(len(aliased_sets['node0']['dataset']), 1)

        result = aliased_sets['node0']['dataset'][0]

        self.assertEqual(result['type_set'], {'n1', 'n2'})
        self.assertEqual(result['foo_set'], {'bar'})
        self.assertEqual(result['bar_register'], 'baz')

        data_id = result['_id']
        self.assertIn(data_id, self.graphmgr.nodes_storage)

    def test_read_node(self):
        stmt = MagicMock()
        stmt.__class__.__name__ = 'ReadStatementNode'
        stmt.aliases = ['elt0', 'elt1']

        aliased_sets = {
            'elt0': {
                'type': 'nodes',
                'dataset': [
                    {'_id': 'foo'}
                ]
            },
            'elt1': {
                'type': 'relationships',
                'dataset': [
                    {'_id': 'bar'}
                ]
            }
        }

        result = self.crud([stmt], aliased_sets)

        self.assertEqual(len(result), 1)

        self.assertIn('elt0', result[0])
        self.assertIn({'_id': 'foo'}, result[0]['elt0'])

        self.assertIn('elt1', result[0])
        self.assertIn({'_id': 'bar'}, result[0]['elt1'])

    def test_update_node(self):
        stmt = MagicMock()
        stmt.__class__.__name__ = 'UpdateStatementNode'

        update0 = MagicMock()
        update0.__class__.__name__ = 'UpdateSetPropertyNode'
        update0.alias = 'elt0'
        update0.propname = 'foo'
        update0.value = 'bar'

        update1 = MagicMock()
        update1.__class__.__name__ = 'UpdateAddPropertyNode'
        update1.alias = 'elt0'
        update1.propname = 'bar'
        update1.value = 'biz'

        update2 = MagicMock()
        update2.__class__.__name__ = 'UpdateUnsetPropertyNode'
        update2.alias = 'elt0'
        update2.propname = 'baz'

        update3 = MagicMock()
        update3.__class__.__name__ = 'UpdateDelPropertyNode'
        update3.alias = 'elt0'
        update3.propname = 'bar'
        update3.value = 'baz'

        stmt.updates = [update0, update1, update2, update3]

        aliased_sets = {
            'elt0': {
                'type': 'nodes',
                'dataset': [
                    {'_id': 'foo'}
                ]
            }
        }

        m = Map(value={
            'foo_register': 'foo',
            'bar_set': {'baz'},
            'baz_register': 'foo'
        })
        self.nodes = {
            'foo': m
        }

        result = self.crud([stmt], aliased_sets)

        self.assertEqual(len(result), 1)
        self.assertIn('elt0', result[0])
        self.assertEqual(len(result[0]['elt0']), 1)

        expected = {
            '_id': 'foo',
            'foo_register': 'bar',
            'bar_set': {'biz'}
        }
        self.assertIn(expected, result[0]['elt0'])
        del expected['_id']
        self.assertEqual(self.nodes['foo'].current, expected)

    def test_delete_node(self):
        stmt = MagicMock()
        stmt.__class__.__name__ = 'DeleteStatementNode'
        stmt.aliases = ['elt0']

        aliased_sets = {
            'elt0': {
                'type': 'nodes',
                'dataset': [
                    {
                        '_id': 'buzz',
                        'targets_set': [
                            'andy:woody'
                        ]
                    }
                ]
            }
        }

        self.nodes['buzz'] = Map(value={
            'targets_set': {'andy:woody'}
        })
        self.nodes['woody'] = Map(value={
            'targets_set': {
                'squeeze:buzz',
                'lenny:mrpotato'
            }
        })

        self.relationships['andy'] = Map(value={'weight_counter': 50})
        self.relationships['squeeze'] = Map(value={'weight_counter': 50})

        self.expected_nodes = {
            'targets_set:"*:buzz"': [
                {
                    '_id': 'woody',
                    'targets_set': [
                        'squeeze:buzz',
                        'lenny:mrpotato'
                    ]
                }
            ],
            'targets_set:"andy:*"': [],
            'targets_set:"squeeze:*"': [
                {
                    '_id': 'woody',
                    'targets_set': [
                        'squeeze:buzz',
                        'lenny:mrpotato'
                    ]
                }
            ]
        }

        result = self.crud([stmt], aliased_sets)

        self.assertEqual(len(result), 0)
        self.assertNotIn('buzz', self.nodes)
        self.assertNotIn('andy', self.relationships)
        self.assertNotIn('squeeze', self.relationships)
        self.assertEqual(
            self.nodes['woody'].current,
            {
                'targets_set': {'lenny:mrpotato'}
            }
        )


class TestRelationCRUD(TestCRUD):
    def test_create_rel_with_alias(self):
        self.expected_nodes = {
            'targets_set:"*:woody"': []
        }

        stmt = MagicMock()
        stmt.__class__.__name__ = 'CreateStatementNode'
        stmt.typed.__class__.__name__ = 'RelationTypeNode'
        stmt.typed.types = ['r1', 'r2']

        stmt.typed.links.source.__class__.__name__ = 'AliasNode'
        stmt.typed.links.source.name = 'node0'

        stmt.typed.links.target.__class__.__name__ = 'AliasNode'
        stmt.typed.links.target.name = 'node1'

        assign0 = MagicMock()
        assign0.__class__.__name__ = 'AssignSetNode'
        assign0.propname = '_id'
        assign0.val = 'foo'

        stmt.typed.properties = [assign0]
        stmt.typed.alias = 'rel0'

        aliased_sets = {
            'node0': {
                'type': 'node',
                'dataset': [
                    {'_id': 'buzz'}
                ]
            },
            'node1': {
                'type': 'node',
                'dataset': [
                    {'_id': 'woody'}
                ]
            }
        }
        result = self.crud([stmt], aliased_sets)

        self.assertEqual(len(result), 0)
        self.assertIn('rel0', aliased_sets)
        self.assertEqual(aliased_sets['rel0']['type'], 'relationships')
        self.assertEqual(len(aliased_sets['rel0']['dataset']), 1)

        result = aliased_sets['rel0']['dataset'][0]

        self.assertEqual(result['_id'], 'foo')
        self.assertEqual(result['type_set'], {'r1', 'r2'})
        self.assertIn('foo', self.graphmgr.relationships_storage)


if __name__ == '__main__':
    main()
