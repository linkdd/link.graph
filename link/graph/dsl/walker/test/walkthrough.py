# -*- coding: utf-8 -*-

from b3j0f.utils.ut import UTCase
from mock import MagicMock, patch
from unittest import main

from link.graph.dsl.walker.walkthrough import Walkthrough


class TestWalkthrough(UTCase):
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

    def setUp(self):
        self.graphmgr = MagicMock()
        self.graphmgr.mapreduce.side_effect = self._mapreduce
        self.walk = Walkthrough(self.graphmgr)

        patcher = patch('link.graph.dsl.walker.walkthrough.getfeature')
        self.getfeature = patcher.start()
        self.getfeature.side_effect = self._getfeature
        self.addCleanup(patcher.stop)

    def tearDown(self):
        self.expected_nodes = {}
        self.expected_rels = {}

    def test_walk_depth_backward(self):
        self.expected_nodes = {
            'fromfilter': [
                {'_id': 'buzz'}
            ],
            'targets_set:("andy:buzz")': [
                {'_id': 'woody'},
                {'_id': 'rex'}
            ],
            'targets_set:("andy:woody")': [
                {'_id': 'sarge'}
            ],
            'targets_set:("andy:rex")': [
                {'_id': 'sid'}
            ],
            'targets_set:("andy:sarge")': [],
            'targets_set:("andy:sid")': []
        }
        self.expected_rels = {
            'throughfilter': [
                {'_id': 'andy'}
            ]
        }

        from_ = MagicMock()
        from_.set_ = 'NODES'
        from_.alias = 'elt0'
        from_.filter = 'fromfilter'

        statement = MagicMock()
        statement.froms = [from_]

        path = MagicMock()

        through = MagicMock()
        through.set_ = 'RELS'
        through.alias = 'rel0'
        through.wmode.type = 'DEPTH'
        through.wmode.begin = 1
        through.wmode.end = 2
        through.wmode.direction = 'BACKWARD'
        through.filter = 'throughfilter'
        path.through = [through]

        to = MagicMock()
        to.alias = 'elt1'
        to.filter = '_id:sarge'

        path.to = [to]

        statement.path = [path]

        result = self.walk([statement])

        self.assertIn('elt0', result)
        self.assertIn('elt1', result)
        self.assertIn('rel0', result)

        self.assertEqual(result['elt0']['type'], 'nodes')
        self.assertEqual(len(result['elt0']['dataset']), 1)
        self.assertIn({'_id': 'buzz'}, result['elt0']['dataset'])

        self.assertEqual(result['elt1']['type'], 'nodes')
        self.assertEqual(len(result['elt1']['dataset']), 1)
        self.assertIn({'_id': 'sarge'}, result['elt1']['dataset'])

        self.assertEqual(result['rel0']['type'], 'relationships')
        self.assertEqual(len(result['rel0']['dataset']), 1)
        self.assertIn({'_id': 'andy'}, result['rel0']['dataset'])

    def test_walk_breadth_backward(self):
        self.expected_nodes = {
            'fromfilter': [
                {'_id': 'buzz'}
            ],
            'targets_set:("andy:buzz")': [
                {'_id': 'woody'},
                {'_id': 'rex'}
            ],
            'targets_set:("andy:woody" OR "andy:rex")': [
                {'_id': 'sarge'},
                {'_id': 'sid'}
            ]
        }
        self.expected_rels = {
            'throughfilter': [
                {'_id': 'andy'}
            ]
        }

        from_ = MagicMock()
        from_.set_ = 'NODES'
        from_.alias = 'elt0'
        from_.filter = 'fromfilter'

        statement = MagicMock()
        statement.froms = [from_]

        path = MagicMock()

        through = MagicMock()
        through.set_ = 'RELS'
        through.alias = 'rel0'
        through.wmode.type = 'BREADTH'
        through.wmode.begin = 1
        through.wmode.end = 2
        through.wmode.direction = 'BACKWARD'
        through.filter = 'throughfilter'
        path.through = [through]

        to = MagicMock()
        to.alias = 'elt1'
        to.filter = '_id:sarge'

        path.to = [to]

        statement.path = [path]

        result = self.walk([statement])

        self.assertIn('elt0', result)
        self.assertIn('elt1', result)
        self.assertIn('rel0', result)

        self.assertEqual(result['elt0']['type'], 'nodes')
        self.assertEqual(len(result['elt0']['dataset']), 1)
        self.assertIn({'_id': 'buzz'}, result['elt0']['dataset'])

        self.assertEqual(result['elt1']['type'], 'nodes')
        self.assertEqual(len(result['elt1']['dataset']), 1)
        self.assertIn({'_id': 'sarge'}, result['elt1']['dataset'])

        self.assertEqual(result['rel0']['type'], 'relationships')
        self.assertEqual(len(result['rel0']['dataset']), 1)
        self.assertIn({'_id': 'andy'}, result['rel0']['dataset'])

    def test_walk_breadth_backward_noend(self):
        self.expected_nodes = {
            'fromfilter': [
                {'_id': 'buzz'}
            ],
            'targets_set:("andy:buzz")': [
                {'_id': 'woody'},
                {'_id': 'rex'}
            ],
            'targets_set:("andy:woody" OR "andy:rex")': [
                {'_id': 'sarge'},
                {'_id': 'sid'}
            ],
            'targets_set:("andy:sarge" OR "andy:sid")': []
        }
        self.expected_rels = {
            'throughfilter': [
                {'_id': 'andy'}
            ]
        }

        from_ = MagicMock()
        from_.set_ = 'NODES'
        from_.alias = 'elt0'
        from_.filter = 'fromfilter'

        statement = MagicMock()
        statement.froms = [from_]

        path = MagicMock()

        through = MagicMock()
        through.set_ = 'RELS'
        through.alias = 'rel0'
        through.wmode.type = 'BREADTH'
        through.wmode.begin = 1
        through.wmode.end = None
        through.wmode.direction = 'BACKWARD'
        through.filter = 'throughfilter'
        path.through = [through]

        to = MagicMock()
        to.alias = 'elt1'
        to.filter = '_id:sarge'

        path.to = [to]

        statement.path = [path]

        result = self.walk([statement])

        self.assertIn('elt0', result)
        self.assertIn('elt1', result)
        self.assertIn('rel0', result)

        self.assertEqual(result['elt0']['type'], 'nodes')
        self.assertEqual(len(result['elt0']['dataset']), 1)
        self.assertIn({'_id': 'buzz'}, result['elt0']['dataset'])

        self.assertEqual(result['elt1']['type'], 'nodes')
        self.assertEqual(len(result['elt1']['dataset']), 1)
        self.assertIn({'_id': 'sarge'}, result['elt1']['dataset'])

        self.assertEqual(result['rel0']['type'], 'relationships')
        self.assertEqual(len(result['rel0']['dataset']), 1)
        self.assertIn({'_id': 'andy'}, result['rel0']['dataset'])

    def test_walk_depth_forward(self):
        self.expected_nodes = {
            'fromfilter': [
                {
                    '_id': 'buzz',
                    'targets_set': [
                        'andy:woody',
                        'andy:rex'
                    ]
                }
            ],
            '_id:(woody OR rex)': [
                {
                    '_id': 'woody',
                    'targets_set': [
                        'andy:sarge'
                    ]
                },
                {
                    '_id': 'rex',
                    'targets_set': [
                        'andy:sid'
                    ]
                }
            ],
            '_id:(sarge)': [
                {
                    '_id': 'sarge',
                    'targets_set': []
                }
            ],
            '_id:(sid)': [
                {
                    '_id': 'sid',
                    'targets_set': []
                }
            ]
        }
        self.expected_rels = {
            'throughfilter': [
                {'_id': 'andy'}
            ]
        }

        from_ = MagicMock()
        from_.set_ = 'NODES'
        from_.alias = 'elt0'
        from_.filter = 'fromfilter'

        statement = MagicMock()
        statement.froms = [from_]

        path = MagicMock()

        through = MagicMock()
        through.set_ = 'RELS'
        through.alias = 'rel0'
        through.wmode.type = 'DEPTH'
        through.wmode.begin = 1
        through.wmode.end = 2
        through.wmode.direction = 'FORWARD'
        through.filter = 'throughfilter'
        path.through = [through]

        to = MagicMock()
        to.alias = 'elt1'
        to.filter = '_id:sarge'

        path.to = [to]

        statement.path = [path]

        result = self.walk([statement])

        self.assertIn('elt0', result)
        self.assertIn('elt1', result)
        self.assertIn('rel0', result)

        self.assertEqual(result['elt0']['type'], 'nodes')
        self.assertEqual(len(result['elt0']['dataset']), 1)
        self.assertIn(
            {
                '_id': 'buzz',
                'targets_set': ['andy:woody', 'andy:rex']
            },
            result['elt0']['dataset']
        )

        self.assertEqual(result['elt1']['type'], 'nodes')
        self.assertEqual(len(result['elt1']['dataset']), 1)
        self.assertIn(
            {
                '_id': 'sarge',
                'targets_set': []
            },
            result['elt1']['dataset']
        )

        self.assertEqual(result['rel0']['type'], 'relationships')
        self.assertEqual(len(result['rel0']['dataset']), 1)
        self.assertIn({'_id': 'andy'}, result['rel0']['dataset'])

    def test_walk_breadth_forward(self):
        self.expected_nodes = {
            'fromfilter': [
                {
                    '_id': 'buzz',
                    'targets_set': [
                        'andy:woody',
                        'andy:rex'
                    ]
                }
            ],
            '_id:(woody OR rex)': [
                {
                    '_id': 'woody',
                    'targets_set': [
                        'andy:sarge'
                    ]
                },
                {
                    '_id': 'rex',
                    'targets_set': [
                        'andy:sid'
                    ]
                }
            ],
            '_id:(sarge OR sid)': [
                {
                    '_id': 'sarge',
                    'targets_set': []
                },
                {
                    '_id': 'sid',
                    'targets_set': []
                }
            ]
        }
        self.expected_rels = {
            'throughfilter': [
                {'_id': 'andy'}
            ]
        }

        from_ = MagicMock()
        from_.set_ = 'NODES'
        from_.alias = 'elt0'
        from_.filter = 'fromfilter'

        statement = MagicMock()
        statement.froms = [from_]

        path = MagicMock()

        through = MagicMock()
        through.set_ = 'RELS'
        through.alias = 'rel0'
        through.wmode.type = 'BREADTH'
        through.wmode.begin = 1
        through.wmode.end = 2
        through.wmode.direction = 'FORWARD'
        through.filter = 'throughfilter'
        path.through = [through]

        to = MagicMock()
        to.alias = 'elt1'
        to.filter = '_id:sarge'

        path.to = [to]

        statement.path = [path]

        result = self.walk([statement])

        self.assertIn('elt0', result)
        self.assertIn('elt1', result)
        self.assertIn('rel0', result)

        self.assertEqual(result['elt0']['type'], 'nodes')
        self.assertEqual(len(result['elt0']['dataset']), 1)
        self.assertIn(
            {
                '_id': 'buzz',
                'targets_set': ['andy:woody', 'andy:rex']
            },
            result['elt0']['dataset']
        )

        self.assertEqual(result['elt1']['type'], 'nodes')
        self.assertEqual(len(result['elt1']['dataset']), 1)
        self.assertIn(
            {
                '_id': 'sarge',
                'targets_set': []
            },
            result['elt1']['dataset']
        )

        self.assertEqual(result['rel0']['type'], 'relationships')
        self.assertEqual(len(result['rel0']['dataset']), 1)
        self.assertIn({'_id': 'andy'}, result['rel0']['dataset'])

    def test_walk_breadth_forward_noend(self):
        self.expected_nodes = {
            'fromfilter': [
                {
                    '_id': 'buzz',
                    'targets_set': [
                        'andy:woody',
                        'andy:rex'
                    ]
                }
            ],
            '_id:(woody OR rex)': [
                {
                    '_id': 'woody',
                    'targets_set': [
                        'andy:sarge'
                    ]
                },
                {
                    '_id': 'rex',
                    'targets_set': [
                        'andy:sid'
                    ]
                }
            ],
            '_id:(sarge OR sid)': [
                {
                    '_id': 'sarge',
                    'targets_set': []
                },
                {
                    '_id': 'sid',
                    'targets_set': []
                }
            ]
        }
        self.expected_rels = {
            'throughfilter': [
                {'_id': 'andy'}
            ]
        }

        from_ = MagicMock()
        from_.set_ = 'NODES'
        from_.alias = 'elt0'
        from_.filter = 'fromfilter'

        statement = MagicMock()
        statement.froms = [from_]

        path = MagicMock()

        through = MagicMock()
        through.set_ = 'RELS'
        through.alias = 'rel0'
        through.wmode.type = 'BREADTH'
        through.wmode.begin = 1
        through.wmode.end = None
        through.wmode.direction = 'FORWARD'
        through.filter = 'throughfilter'
        path.through = [through]

        to = MagicMock()
        to.alias = 'elt1'
        to.filter = '_id:sarge'

        path.to = [to]

        statement.path = [path]

        result = self.walk([statement])

        self.assertIn('elt0', result)
        self.assertIn('elt1', result)
        self.assertIn('rel0', result)

        self.assertEqual(result['elt0']['type'], 'nodes')
        self.assertEqual(len(result['elt0']['dataset']), 1)
        self.assertIn(
            {
                '_id': 'buzz',
                'targets_set': ['andy:woody', 'andy:rex']
            },
            result['elt0']['dataset']
        )

        self.assertEqual(result['elt1']['type'], 'nodes')
        self.assertEqual(len(result['elt1']['dataset']), 1)
        self.assertIn(
            {
                '_id': 'sarge',
                'targets_set': []
            },
            result['elt1']['dataset']
        )

        self.assertEqual(result['rel0']['type'], 'relationships')
        self.assertEqual(len(result['rel0']['dataset']), 1)
        self.assertIn({'_id': 'andy'}, result['rel0']['dataset'])

    def test_complex_walkthrough(self):
        self.expected_nodes = {
            'fromfilter': [
                {
                    '_id': 'buzz',
                    'targets_set': [
                        'andy:woody',
                        'andy:rex'
                    ]
                },
                {
                    '_id': 'lenny',
                    'targets_set': []
                }
            ],
            '_id:(woody OR rex)': [
                {
                    '_id': 'woody',
                    'targets_set': [
                        'andy:sarge'
                    ]
                },
                {
                    '_id': 'rex',
                    'targets_set': [
                        'andy:sid'
                    ]
                }
            ],
            '_id:(sarge OR sid)': [
                {
                    '_id': 'sarge',
                    'targets_set': []
                },
                {
                    '_id': 'sid',
                    'targets_set': []
                }
            ],
            'targets_set:("molly:sarge")': [
                {
                    '_id': 'squeeze',
                    'targets_set': []
                }
            ],
            'targets_set:("molly:sid")': [
                {
                    '_id': 'squeeze',
                    'targets_set': []
                }
            ],
            'targets_set:("molly:squeeze")': [
                {
                    '_id': 'hamm',
                    'targets_set': []
                }
            ],
            'targets_set:("andy:sarge" OR "molly:sarge")': [
                {
                    '_id': 'squeeze',
                    'targets_set': []
                }
            ],
            'targets_set:("andy:sid" OR "molly:sid")': [
                {
                    '_id': 'squeeze',
                    'targets_set': []
                }
            ],
            'targets_set:("andy:squeeze" OR "molly:squeeze")': [
                {
                    '_id': 'hamm',
                    'targets_set': []
                }
            ],
            'targets_set:("molly:hamm")': [
                {
                    '_id': 'bopeep',
                    'targets_set': []
                }
            ],
            'targets_set:("molly:bopeep")': [
                {
                    '_id': 'mrpotato',
                    'targets_set': []
                }
            ]
        }
        self.expected_rels = {
            'through0filter': [
                {'_id': 'andy'},
                {'_id': 'molly'}
            ]
        }

        from0 = MagicMock()
        from0.set_ = 'NODES'
        from0.alias = 'elt0'
        from0.filter = 'fromfilter'

        from1 = MagicMock()
        from1.set_ = 'elt0'
        from1.alias = 'elt1'
        from1.filter = ''

        from2 = MagicMock()
        from2.set_ = 'elt1'
        from2.alias = 'elt2'
        from2.filter = '_id:buzz'

        statement = MagicMock()
        statement.froms = [from0, from1, from2]

        path = MagicMock()

        through0 = MagicMock()
        through0.set_ = 'RELS'
        through0.alias = 'rel0'
        through0.wmode.type = 'BREADTH'
        through0.wmode.begin = 1
        through0.wmode.end = None
        through0.wmode.direction = 'FORWARD'
        through0.filter = 'through0filter'

        through1 = MagicMock()
        through1.set_ = 'rel0'
        through1.alias = 'rel1'
        through1.wmode.type = 'DEPTH'
        through1.wmode.begin = 1
        through1.wmode.end = 2
        through1.wmode.direction = 'BACKWARD'
        through1.filter = '_id:molly'

        through2 = MagicMock()
        through2.set_ = 'rel1'
        through2.alias = 'rel1'
        through2.wmode.type = 'DEPTH'
        through2.wmode.begin = 1
        through2.wmode.end = 2
        through2.wmode.direction = 'BACKWARD'
        through2.filter = ''

        path.through = [through0, through1, through2]

        to0 = MagicMock()
        to0.alias = 'elt3'
        to0.filter = '_id:mrpotato'

        to1 = MagicMock()
        to1.alias = 'elt4'
        to1.filter = ''

        path.to = [to0, to1]

        statement.path = [path]

        result = self.walk([statement])

        self.assertIn('elt0', result)
        self.assertIn('elt1', result)
        self.assertIn('elt2', result)
        self.assertIn('elt3', result)
        self.assertIn('elt4', result)
        self.assertIn('rel0', result)
        self.assertIn('rel1', result)

        self.assertEqual(result['elt0']['type'], 'nodes')
        self.assertEqual(len(result['elt0']['dataset']), 2)
        self.assertIn(
            {
                '_id': 'buzz',
                'targets_set': ['andy:woody', 'andy:rex']
            },
            result['elt0']['dataset']
        )
        self.assertIn(
            {
                '_id': 'lenny',
                'targets_set': []
            },
            result['elt0']['dataset']
        )

        self.assertEqual(result['elt1']['type'], 'nodes')
        self.assertEqual(len(result['elt1']['dataset']), 2)
        self.assertIn(
            {
                '_id': 'buzz',
                'targets_set': ['andy:woody', 'andy:rex']
            },
            result['elt1']['dataset']
        )
        self.assertIn(
            {
                '_id': 'lenny',
                'targets_set': []
            },
            result['elt1']['dataset']
        )

        self.assertEqual(result['elt2']['type'], 'nodes')
        self.assertEqual(len(result['elt2']['dataset']), 1)
        self.assertIn(
            {
                '_id': 'buzz',
                'targets_set': ['andy:woody', 'andy:rex']
            },
            result['elt2']['dataset']
        )

        self.assertEqual(result['elt3']['type'], 'nodes')
        self.assertEqual(len(result['elt3']['dataset']), 1)
        self.assertIn(
            {
                '_id': 'mrpotato',
                'targets_set': []
            },
            result['elt3']['dataset']
        )

        self.assertEqual(result['elt4']['type'], 'nodes')
        self.assertEqual(len(result['elt4']['dataset']), 3)
        self.assertIn(
            {
                '_id': 'hamm',
                'targets_set': []
            },
            result['elt4']['dataset']
        )
        self.assertIn(
            {
                '_id': 'bopeep',
                'targets_set': []
            },
            result['elt4']['dataset']
        )
        self.assertIn(
            {
                '_id': 'mrpotato',
                'targets_set': []
            },
            result['elt4']['dataset']
        )

        self.assertEqual(result['rel0']['type'], 'relationships')
        self.assertEqual(len(result['rel0']['dataset']), 2)
        self.assertIn({'_id': 'andy'}, result['rel0']['dataset'])
        self.assertIn({'_id': 'molly'}, result['rel0']['dataset'])

        self.assertEqual(result['rel1']['type'], 'relationships')
        self.assertEqual(len(result['rel1']['dataset']), 1)
        self.assertIn({'_id': 'molly'}, result['rel1']['dataset'])


if __name__ == '__main__':
    main()
