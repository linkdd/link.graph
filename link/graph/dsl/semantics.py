# -*- coding: utf-8 -*-

from b3j0f.utils.iterable import isiterable
from six import string_types


class GraphDSLSemantics(object):
    def parse_StringNode(self, node):
        return node.value

    def parse_IntegerNode(self, node):
        return int(''.join(node.value))

    def parse_DecimalNode(self, node):
        return float(''.join(node.value))

    def parse_BooleanNode(self, node):
        return (node.value == 'TRUE')

    def parse_ValueNode(self, node):
        return node.value.value

    def parse_PathNode(self, node):
        aelts = node.aelts
        joints = node.joint

        if not isiterable(aelts, exclude=string_types):
            aelts = [aelts]

        if not isiterable(joints, exclude=string_types):
            joints = [joints]

        nodes = []

        for i in range(len(aelts) + len(joints)):
            if i % 2 == 0:
                local_node = aelts[i // 2]

            else:
                local_node = joints[i // 2]

            if local_node is not None:
                nodes.append(local_node)

        return nodes
