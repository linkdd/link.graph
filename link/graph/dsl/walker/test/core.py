# -*- coding: utf-8 -*-

from b3j0f.utils.ut import UTCase
from mock import MagicMock, patch
from unittest import main

from link.graph.dsl.walker.core import GraphDSLNodeWalker


def get_mocked_name():
    for name in ['foo', 'bar', 'baz']:
        m = MagicMock()
        m.name = name
        yield m


def get_mocked_value():
    for val in ['foo', 'bar', 'baz']:
        m = MagicMock()
        m.value = val
        yield m


def get_mocked_statements():
    for stmt in ['foo', 'bar', 'baz']:
        m = MagicMock()
        m.statement = stmt
        yield m


class TestNodeWalker(UTCase):
    def setUp(self):
        self.aliased_sets = {
            'foo': ['bar', 'baz']
        }
        self.result = 'foo'

        self.graphmgr = MagicMock()
        self.op_walk = MagicMock(return_value=self.aliased_sets)
        self.op_crud = MagicMock(return_value=self.result)

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

    def test_walk_AndFilterNode(self):
        nw = GraphDSLNodeWalker(self.graphmgr)

        node = MagicMock()
        node.left.query = 'left'
        node.right.query = 'right'

        nw.walk_AndFilterNode(node, [])

        self.assertEqual(node.query, 'left right')

    def test_walk_OrFilterNode(self):
        nw = GraphDSLNodeWalker(self.graphmgr)

        node = MagicMock()
        node.left.query = 'left'
        node.right.query = 'right'

        nw.walk_OrFilterNode(node, [])

        self.assertEqual(node.query, 'left OR right')

    def test_walk_InnerFilterNode(self):
        nw = GraphDSLNodeWalker(self.graphmgr)

        node = MagicMock()
        node.search.value.query = 'expected'

        nw.walk_InnerFilterNode(node, [])

        self.assertEqual(node.query, 'expected')

    def test_walk_TypedFilterNode(self):
        nw = GraphDSLNodeWalker(self.graphmgr)

        node = MagicMock()
        node.types.values_ = list(get_mocked_name())
        node.filter.filter = None

        nw.walk_TypedFilterNode(node, [])

        self.assertEqual(node.query, 'type_set:(foo OR bar OR baz)')

        node = MagicMock()
        node.types.values_ = list(get_mocked_name())
        node.filter.filter.query = 'filter'

        nw.walk_TypedFilterNode(node, [])

        self.assertEqual(node.query, 'type_set:(foo OR bar OR baz) filter')

        node = MagicMock()
        node.types.values_ = []
        node.filter.filter.query = 'filter'

        nw.walk_TypedFilterNode(node, [])

        self.assertEqual(node.query, 'filter')

    def test_walk_NodeTypeNode(self):
        nw = GraphDSLNodeWalker(self.graphmgr)

        node = MagicMock()
        node.alias.name = 'alias'
        node.types.values_ = list(get_mocked_name())
        node.properties.assignations = 'assignations'

        nw.walk_NodeTypeNode(node, [])

        self.assertEqual(node.alias, 'alias')
        self.assertEqual(node.types, ['foo', 'bar', 'baz'])
        self.assertEqual(node.properties, 'assignations')

        node = MagicMock()
        node.alias = None
        node.types.values_ = list(get_mocked_name())
        node.properties.assignations = 'assignations'

        nw.walk_NodeTypeNode(node, [])

        self.assertIsNone(node.alias)
        self.assertEqual(node.types, ['foo', 'bar', 'baz'])
        self.assertEqual(node.properties, 'assignations')

    def test_walk_RelationTypeNode(self):
        nw = GraphDSLNodeWalker(self.graphmgr)

        node = MagicMock()
        node.alias.name = 'alias'
        node.types.values_ = list(get_mocked_name())
        node.properties.assignations = 'assignations'

        nw.walk_RelationTypeNode(node, [])

        self.assertEqual(node.alias, 'alias')
        self.assertEqual(node.types, ['foo', 'bar', 'baz'])
        self.assertEqual(node.properties, 'assignations')

        node = MagicMock()
        node.alias = None
        node.types.values_ = list(get_mocked_name())
        node.properties.assignations = 'assignations'

        nw.walk_RelationTypeNode(node, [])

        self.assertIsNone(node.alias)
        self.assertEqual(node.types, ['foo', 'bar', 'baz'])
        self.assertEqual(node.properties, 'assignations')

    def test_walk_FromNode(self):
        nw = GraphDSLNodeWalker(self.graphmgr)

        node = MagicMock()
        node.set_.name = 'set'
        node.alias.name = 'alias'
        node.filter.query = 'filter'

        nw.walk_FromNode(node, [])

        self.assertEqual(node.set_, 'set')
        self.assertEqual(node.alias, 'alias')
        self.assertEqual(node.filter, 'filter')

        node = MagicMock()
        node.set_.name = 'set'
        node.alias = None
        node.filter.query = 'filter'

        nw.walk_FromNode(node, [])

        self.assertEqual(node.set_, 'set')
        self.assertIsNone(node.alias)
        self.assertEqual(node.filter, 'filter')

    def test_walk_WalkModeNode(self):
        nw = GraphDSLNodeWalker(self.graphmgr)

        node = MagicMock()
        node.type.value = 'type'
        node.direction.value = 'dir'
        node.begin.value = 'begin'
        node.end.value = 'end'

        nw.walk_WalkModeNode(node, [])

        self.assertEqual(node.type, 'type')
        self.assertEqual(node.direction, 'dir')
        self.assertEqual(node.begin, 'begin')
        self.assertEqual(node.end, 'end')

        node = MagicMock()
        node.type = None
        node.direction = None
        node.begin = None
        node.end = None

        nw.walk_WalkModeNode(node, [])

        self.assertIsNone(node.type)
        self.assertIsNone(node.direction)
        self.assertIsNone(node.begin)
        self.assertIsNone(node.end)

    def test_walk_ThroughNode(self):
        nw = GraphDSLNodeWalker(self.graphmgr)

        node = MagicMock()
        node.set_.name = 'set'
        node.alias.name = 'alias'
        node.filter.query = 'filter'

        nw.walk_ThroughNode(node, [])

        self.assertEqual(node.set_, 'set')
        self.assertEqual(node.alias, 'alias')
        self.assertEqual(node.filter, 'filter')

        node = MagicMock()
        node.set_.name = 'set'
        node.alias = None
        node.filter = None

        nw.walk_ThroughNode(node, [])

        self.assertEqual(node.set_, 'set')
        self.assertIsNone(node.alias)
        self.assertIsNone(node.filter)

    def test_walk_ToNode(self):
        nw = GraphDSLNodeWalker(self.graphmgr)

        node = MagicMock()
        node.alias.name = 'alias'
        node.filter.query = 'filter'

        nw.walk_ToNode(node, [])

        self.assertEqual(node.alias, 'alias')
        self.assertEqual(node.filter, 'filter')

        node = MagicMock()
        node.alias.name = 'alias'
        node.filter = None

        nw.walk_ToNode(node, [])

        self.assertEqual(node.alias, 'alias')
        self.assertIsNone(node.filter)

    def test_walk_CreateStatementNode(self):
        nw = GraphDSLNodeWalker(self.graphmgr)

        node = MagicMock()
        node.typed.properties = list(get_mocked_value())

        nw.walk_CreateStatementNode(node, [])

        self.assertEqual(node.typed.properties, ['foo', 'bar', 'baz'])

    def test_walk_ReadStatementNode(self):
        nw = GraphDSLNodeWalker(self.graphmgr)

        node = MagicMock()
        node.aliases = list(get_mocked_name())

        nw.walk_ReadStatementNode(node, [])

        self.assertEqual(node.aliases, ['foo', 'bar', 'baz'])

    def test_walk_UpdateStatementNode(self):
        nw = GraphDSLNodeWalker(self.graphmgr)

        node = MagicMock()
        node.updates = list(get_mocked_value())

        nw.walk_UpdateStatementNode(node, [])

        self.assertEqual(node.updates, ['foo', 'bar', 'baz'])

    def test_walk_DeleteStatementNode(self):
        nw = GraphDSLNodeWalker(self.graphmgr)

        node = MagicMock()
        node.aliases = list(get_mocked_name())

        nw.walk_DeleteStatementNode(node, [])

        self.assertEqual(node.aliases, ['foo', 'bar', 'baz'])

    def test_walk_CRUDBlock(self):
        nw = GraphDSLNodeWalker(self.graphmgr)

        node = MagicMock()
        node.statements = list(get_mocked_statements())

        nw.walk_CRUDBlock(node, [])

        self.assertEqual(node.statements, ['foo', 'bar', 'baz'])

    def test_walk_RequestNode(self):
        nw = GraphDSLNodeWalker(self.graphmgr)

        node = MagicMock()
        node.crud.statements = 'crud'
        node.walkthrough = 'walk'

        result = nw.walk_RequestNode(node, [])

        self.op_walk.assert_called_with('walk')
        self.op_crud.assert_called_with('crud', self.aliased_sets)
        self.assertEqual(result, self.result)


if __name__ == '__main__':
    main()
