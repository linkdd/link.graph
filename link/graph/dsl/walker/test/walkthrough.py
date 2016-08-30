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
            feature.search.return_value = expected

        return feature

    def setUp(self):
        self.expected_nodes = []
        self.expected_rels = []

        self.graphmgr = MagicMock()
        self.walk = Walkthrough(self.graphmgr)

        patcher = patch('link.graph.dsl.walker.walkthrough.getfeature')
        self.getfeature = patcher.start()
        self.getfeature.side_effect = self._getfeature
        self.addCleanup(patcher.stop)

    def test_walkthrough(self):
        from_ = MagicMock()
        from_.set_ = 'NODES'
        from_.alias = 'elt0'
        from_.filter = 'filter'

        statement = MagicMock()
        statement.froms = [from_]

        path = MagicMock()

        through = MagicMock()
        through.set_ = 'RELS'
        through.alias = None
        through.wmode.type = 'DEPTH'
        through.wmode.begin = 5
        through.wmode.end = 10
        through.wmode.direction = 'BACKWARD'
        through.filter = 'filter'
        path.through = [through]

        to = MagicMock()
        to.alias = 'elt1'
        to.filter = 'filter'

        path.to = [to]

        statement.path = [path]

        result = self.walk([statement])


if __name__ == '__main__':
    main()
