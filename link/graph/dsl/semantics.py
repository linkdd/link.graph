# -*- coding: utf-8 -*-

from b3j0f.utils.iterable import isiterable
from six import string_types


class GraphDSLSemantics(object):
    def parse_StringNode(self, node):
        return node.value

    def parse_NaturalNode(self, node):
        return int(''.join(node.value))

    def parse_IntegerNode(self, node):
        if node.sign is not None:
            return int('{0}{1}'.format(node.sign, node.int.value))

        else:
            return node.int.value

    def parse_DecimalNode(self, node):
        if node.sign is not None:
            return float('{0}{1}.{2}'.format(
                node.sign,
                node.int.value,
                node.dec.value
            ))

        else:
            return float('{0}.{1}'.format(node.int.value, node.dec.value))

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

    def parse_query_types(self, node):
        types = [
            t.name
            for t in node.types
        ]

        return 'type_set:({0})'.format(' OR '.join(types))

    def parse_query_conditions(self, node):
        prop_queries = []

        for condition in node.properties:
            if condition.op == '>':
                prop_query = '{0}:[{1} TO *]'.format(
                    condition.propname,
                    condition.value
                )

            elif condition.op == '>=':
                prop_query = '{0}:[{1} TO *]'.format(
                    condition.propname,
                    condition.value - 1
                )

            elif condition.op == '<':
                prop_query = '{0}:[* TO {1}]'.format(
                    condition.propname,
                    condition.value - 1
                )

            elif condition.op == '>=':
                prop_query = '{0}:[* TO {1}]'.format(
                    condition.propname,
                    condition.value
                )

            elif condition.op in ['=', '~=']:
                prop_query = '{0}:{1}'.format(
                    condition.propname,
                    condition.value
                )

            elif condition.op == '!=':
                prop_query = '-{0}:{1}'.format(
                    condition.propname,
                    condition.value
                )

            prop_queries.append(prop_query)

        return ' '.join(prop_queries)

    def parse_query(self, node):
        return '{0} {1}'.format(
            self.parse_query_types(node),
            self.parse_query_conditions(node)
        )
