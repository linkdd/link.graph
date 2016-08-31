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

        self.graphmgr = MagicMock()
        self.graphmgr.mapreduce.side_effect = self._mapreduce
        self.walk = Walkthrough(self.graphmgr)

        patcher = patch('link.graph.dsl.walker.walkthrough.getfeature')
        self.getfeature = patcher.start()
        self.getfeature.side_effect = self._getfeature
        self.addCleanup(patcher.stop)

    def test_walkthrough(self):
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
        through.wmode.begin = 2
        through.wmode.end = 3
        through.wmode.direction = 'BACKWARD'
        through.filter = 'throughfilter'
        path.through = [through]

        to = MagicMock()
        to.alias = 'elt1'
        to.filter = '_id:sarge'

        path.to = [to]

        statement.path = [path]

        result = self.walk([statement])


if __name__ == '__main__':
    main()
