# -*- coding: utf-8 -*-

from b3j0f.utils.ut import UTCase
from mock import MagicMock, patch
from unittest import main

from link.graph.dsl.generator import single_parser_per_scope
from link.graph.dsl.generator import GraphDSLGenerator


class TestGenerator(UTCase):
    def setUp(self):
        self.grammar = 'GRAMMAR'
        self.code = 'CODE'

        patcher1 = patch('link.graph.dsl.generator.open')
        patcher2 = patch('link.graph.dsl.generator.FileConfDriver')
        patcher3 = patch('link.graph.dsl.generator.codegenerator')

        self.open = patcher1.start()
        self.cfgdrvcls = patcher2.start()
        self.codegen = patcher3.start()

        self.addCleanup(patcher1.stop)
        self.addCleanup(patcher2.stop)
        self.addCleanup(patcher3.stop)

        self.fd = MagicMock()
        self.fd.read.return_value = self.grammar
        self.fd.__enter__.return_value = self.fd
        self.open.return_value = self.fd

        self.cfgdrv = MagicMock()
        self.cfgdrvcls.return_value = self.cfgdrv

        self.codegen.return_value = self.code

    def test_instance(self):
        self.cfgdrv.rscpaths.return_value = ['path0']

        generator = GraphDSLGenerator()

        self.cfgdrv.rscpaths.assert_called_with('link/graph/dsl/grammar.bnf')
        self.assertEqual(generator.grammar, 'path0')
        self.assertEqual(generator.modname, 'graph_dsl_generated')

        self.cfgdrv.rscpaths.return_value = []

        generator = GraphDSLGenerator()

        self.cfgdrv.rscpaths.assert_called_with('link/graph/dsl/grammar.bnf')
        self.assertIsNone(generator.grammar)
        self.assertEqual(generator.modname, 'graph_dsl_generated')

    def test_singleton(self):
        generator1 = single_parser_per_scope()
        generator2 = single_parser_per_scope()

        self.assertIs(generator1, generator2)

    def test_load_success(self):
        self.cfgdrv.rscpaths.return_value = ['path0']

        generator = GraphDSLGenerator()

        self.cfgdrv.rscpaths.assert_called_with('link/graph/dsl/grammar.bnf')
        self.assertEqual(generator.grammar, 'path0')
        self.assertEqual(generator.modname, 'graph_dsl_generated')

        code = generator()

        self.assertEqual(code, self.code)
        self.codegen.assert_called_with(
            'graph_dsl_generated',
            GraphDSLGenerator.MODEL_PREFIX,
            self.grammar
        )

    def test_load_fail(self):
        self.cfgdrv.rscpaths.return_value = []

        generator = GraphDSLGenerator()

        self.cfgdrv.rscpaths.assert_called_with('link/graph/dsl/grammar.bnf')
        self.assertIsNone(generator.grammar)
        self.assertEqual(generator.modname, 'graph_dsl_generated')

        with self.assertRaises(GraphDSLGenerator.Error):
            generator()


if __name__ == '__main__':
    main()
