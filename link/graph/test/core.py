# -*- coding: utf-8 -*-

from b3j0f.utils.ut import UTCase
from mock import MagicMock, patch
from unittest import main

from link.graph.core import MapReduceMiddleware, KeyValueStore
from link.graph.core import GraphManager, GraphMiddleware
from link.middleware.core import Middleware


class TestGraph(UTCase):
    def setUp(self):
        self.pbackend = MagicMock()
        self.kvstore = MagicMock()
        self.nodewalker = MagicMock()

        self.parser = MagicMock()
        self.parsermod = MagicMock()
        self.parsermod.GraphDSLParser.return_value = self.parser

        MapReduceMiddleware.get_middleware_by_uri = MagicMock(
            return_value=self.pbackend
        )

        KeyValueStore.get_middleware_by_uri = MagicMock(
            return_value=self.kvstore
        )

        patcher1 = patch('link.graph.core.single_parser_per_scope')
        patcher2 = patch('link.graph.core.GraphDSLNodeWalker')

        self.single_parser = patcher1.start()
        self.nodewalkercls = patcher2.start()

        self.addCleanup(self.single_parser)
        self.addCleanup(self.nodewalkercls)

        self.nodewalkercls.return_value = self.nodewalker
        self.single_parser.return_value = self.parsermod

    def test_instanciate(self):
        mgr = GraphManager()

        self.assertIs(mgr.parallel_backend, self.pbackend)
        self.assertIs(mgr.nodes_storage, self.kvstore)
        self.assertIs(mgr.relationships_storage, self.kvstore)
        self.assertIs(mgr.parser, self.parser)
        self.assertIs(mgr.walker, self.nodewalker)

        self.pbackend.return_value = 'expected'
        result = mgr.mapreduce('identifier', 'mapper', 'reducer', 'dataset')

        self.assertEqual(result, 'expected')
        self.pbackend.assert_called_with(
            'identifier', 'mapper', 'reducer', 'dataset'
        )

        self.nodewalker.walk.return_value = 'expected'
        self.parser.parse.return_value = 'model'
        result = mgr('request')

        self.assertEqual(result, 'expected')
        self.parser.parse.assert_called_with('request', rule_name='start')
        self.nodewalker.walk.assert_called_with('model')

    def test_middleware(self):
        mid = Middleware.get_middleware_by_uri('graph://')

        self.assertIsInstance(mid, GraphMiddleware)

        self.assertIs(mid._graph.parallel_backend, self.pbackend)
        self.assertIs(mid._graph.nodes_storage, self.kvstore)
        self.assertIs(mid._graph.relationships_storage, self.kvstore)
        self.assertIs(mid._graph.parser, self.parser)
        self.assertIs(mid._graph.walker, self.nodewalker)

        self.nodewalker.walk.return_value = 'expected'
        self.parser.parse.return_value = 'model'
        result = mid('request')

        self.assertEqual(result, 'expected')
        self.parser.parse.assert_called_with('request', rule_name='start')
        self.nodewalker.walk.assert_called_with('model')

    def test_middleware_with_path(self):
        mid = Middleware.get_middleware_by_uri('graph:///test.conf')

        self.assertIsInstance(mid, GraphMiddleware)

        self.assertIs(mid._graph.parallel_backend, self.pbackend)
        self.assertIs(mid._graph.nodes_storage, self.kvstore)
        self.assertIs(mid._graph.relationships_storage, self.kvstore)
        self.assertIs(mid._graph.parser, self.parser)
        self.assertIs(mid._graph.walker, self.nodewalker)

        self.nodewalker.walk.return_value = 'expected'
        self.parser.parse.return_value = 'model'
        result = mid('request')

        self.assertEqual(result, 'expected')
        self.parser.parse.assert_called_with('request', rule_name='start')
        self.nodewalker.walk.assert_called_with('model')



if __name__ == '__main__':
    main()
