# -*- coding: utf-8 -*-

from grako.model import DepthFirstWalker


class CRUDFilterWalker(DepthFirstWalker):

    OPERATOR_MAP = {
        '<': '$lt',
        '<=': '$lte',
        '=': '$eq',
        '!=': '$ne',
        '>=': '$gte',
        '>': '$gt',
        '~=': '$regex'
    }

    def walk_TermRequestFilterNode(self, node, children):
        node.result = {
            CRUDFilterWalker.OPERATOR_MAP[node.op]: node.value
        }

        return node.result

    def walk_AndRequestFilterNode(self, node, children):
        node.result = {
            '$and': [
                node.left.result,
                node.right.result
            ]
        }

        return node.result

    def walk_OrRequestFilterNode(self, node, children):
        node.result = {
            '$or': [
                node.left.result,
                node.right.result
            ]
        }

        return node.result
