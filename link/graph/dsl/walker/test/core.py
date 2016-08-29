# -*- coding: utf-8 -*-

from b3j0f.utils.ut import UTCase
from mock import MagicMock, patch
from unittest import main

from link.graph.dsl.walker.core import GraphDSLNodeWalker


class TestNodeWalker(UTCase):
    def setUp(self):
        self.graphmgr = MagicMock()
        self.op_walk = MagicMock()
        self.op_crud = MagicMock()

        patcher1 = patch('link.graph.dsl.walker.core.Walkthrough')
        patcher2 = patch('link.graph.dsl.walker.core.CRUDOperations')

        self.walkthrough = patcher1.start()
        self.crud = patcher2.start()

        self.walkthrough.return_value = self.op_walk
        self.crud.return_value = self.op_crud

        self.addCleanup(patcher1.stop)
        self.addCleanup(patcher2.stop)

    def test_init(self):
        nw = GraphDSLNodeWalker(self.graphmgr)

        self.walkthrough.assert_called_with(self.graphmgr)
        self.crud.assert_called_with(self.graphmgr)

        self.assertIs(nw.op_walk, self.op_walk)
        self.assertIs(nw.op_crud, self.op_crud)

    def test_walk_StringNode(self):
        nw = GraphDSLNodeWalker(self.graphmgr)

        node = MagicMock()
        node.value = 'expected'
        nw.walk_StringNode(node, [])

        self.assertEqual(node.value, 'expected')

    def test_walk_NaturalNode(self):
        nw = GraphDSLNodeWalker(self.graphmgr)

        node = MagicMock()
        node.value = '42'
        nw.walk_NaturalNode(node, [])

        self.assertEqual(node.value, 42)

    def test_walk_DecimalNode(self):
        nw = GraphDSLNodeWalker(self.graphmgr)

        node = MagicMock()
        node.sign = None
        node.int.value = '42'
        node.dec.value = '42'
        nw.walk_DecimalNode(node, [])

        self.assertEqual(node.value, 42.42)

        node = MagicMock()
        node.sign = '-'
        node.int.value = '42'
        node.dec.value = '42'
        nw.walk_DecimalNode(node, [])

        self.assertEqual(node.value, -42.42)

    def test_walk_IntegerNode(self):
        nw = GraphDSLNodeWalker(self.graphmgr)

        node = MagicMock()
        node.sign = None
        node.int.value = '42'
        nw.walk_IntegerNode(node, [])

        self.assertEqual(node.value, 42)

        node = MagicMock()
        node.sign = '-'
        node.int.value = '42'
        nw.walk_IntegerNode(node, [])

        self.assertEqual(node.value, -42)

    def test_walk_BooleanNode(self):
        nw = GraphDSLNodeWalker(self.graphmgr)

        node = MagicMock()
        node.value = 'TRUE'
        nw.walk_BooleanNode(node, [])

        self.assertTrue(node.value)

        node = MagicMock()
        node.value = 'FALSE'
        nw.walk_BooleanNode(node, [])

        self.assertFalse(node.value)

    def test_walk_ValueNode(self):
        nw = GraphDSLNodeWalker(self.graphmgr)

        node = MagicMock()
        node.value.value = 'expected'
        nw.walk_ValueNode(node, [])

        self.assertEqual(node.value, 'expected')

    def test_walk_AliasNode(self):
        nw = GraphDSLNodeWalker(self.graphmgr)

        node = MagicMock()
        node.name.name = 'expected'
        nw.walk_AliasNode(node, [])

        self.assertEqual(node.name, 'expected')

    def test_walk_TypeNode(self):
        nw = GraphDSLNodeWalker(self.graphmgr)

        node = MagicMock()
        node.name.name = 'expected'
        nw.walk_TypeNode(node, [])

        self.assertEqual(node.name, 'expected')

    def test_walk_AssignSetNode(self):
        nw = GraphDSLNodeWalker(self.graphmgr)

        node = MagicMock()
        node.propname.name = 'expected'
        node.value.value = 'expected'

        nw.walk_AssignSetNode(node, [])

        self.assertEqual(node.propname, 'expected')
        self.assertEqual(node.value, 'expected')

    def test_walk_AssignAddNode(self):
        nw = GraphDSLNodeWalker(self.graphmgr)

        node = MagicMock()
        node.propname.name = 'expected'
        node.value.value = 'expected'

        nw.walk_AssignAddNode(node, [])

        self.assertEqual(node.propname, 'expected')
        self.assertEqual(node.value, 'expected')

    def test_walk_UpdateSetPropertyNode(self):
        nw = GraphDSLNodeWalker(self.graphmgr)

        node = MagicMock()
        node.alias.name = 'expected'
        node.propname.name = 'expected'
        node.value.value = 'expected'

        nw.walk_UpdateSetPropertyNode(node, [])

        self.assertEqual(node.alias, 'expected')
        self.assertEqual(node.propname, 'expected')
        self.assertEqual(node.value, 'expected')

    def test_walk_UpdateAddPropertyNode(self):
        nw = GraphDSLNodeWalker(self.graphmgr)

        node = MagicMock()
        node.alias.name = 'expected'
        node.propname.name = 'expected'
        node.value.value = 'expected'

        nw.walk_UpdateAddPropertyNode(node, [])

        self.assertEqual(node.alias, 'expected')
        self.assertEqual(node.propname, 'expected')
        self.assertEqual(node.value, 'expected')

    def test_walk_UpdateUnsetPropertyNode(self):
        nw = GraphDSLNodeWalker(self.graphmgr)

        node = MagicMock()
        node.alias.name = 'expected'
        node.propname.name = 'expected'

        nw.walk_UpdateUnsetPropertyNode(node, [])

        self.assertEqual(node.alias, 'expected')
        self.assertEqual(node.propname, 'expected')

    def test_walk_UpdateDelPropertyNode(self):
        nw = GraphDSLNodeWalker(self.graphmgr)

        node = MagicMock()
        node.alias.name = 'expected'
        node.propname.name = 'expected'
        node.value.value = 'expected'

        nw.walk_UpdateDelPropertyNode(node, [])

        self.assertEqual(node.alias, 'expected')
        self.assertEqual(node.propname, 'expected')
        self.assertEqual(node.value, 'expected')

    def test_walk_TermFilterNode(self):
        nw = GraphDSLNodeWalker(self.graphmgr)

        node = MagicMock()
        node.op.value = '<'
        node.propname.name = 'foo'
        node.value.value = 42

        nw.walk_TermFilterNode(node, [])

        self.assertEqual(node.query, 'foo:[* TO 41]')

        node = MagicMock()
        node.op.value = '<='
        node.propname.name = 'foo'
        node.value.value = 42

        nw.walk_TermFilterNode(node, [])

        self.assertEqual(node.query, 'foo:[* TO 42]')

        node = MagicMock()
        node.op.value = '='
        node.propname.name = 'foo'
        node.value.value = 'bar'

        nw.walk_TermFilterNode(node, [])

        self.assertEqual(node.query, 'foo:bar')

        node = MagicMock()
        node.op.value = '!='
        node.propname.name = 'foo'
        node.value.value = 'bar'

        nw.walk_TermFilterNode(node, [])

        self.assertEqual(node.query, '-foo:bar')

        node = MagicMock()
        node.op.value = '>='
        node.propname.name = 'foo'
        node.value.value = 42

        nw.walk_TermFilterNode(node, [])

        self.assertEqual(node.query, 'foo:[42 TO *]')

        node = MagicMock()
        node.op.value = '>'
        node.propname.name = 'foo'
        node.value.value = 42

        nw.walk_TermFilterNode(node, [])

        self.assertEqual(node.query, 'foo:[41 TO *]')


if __name__ == '__main__':
    main()
