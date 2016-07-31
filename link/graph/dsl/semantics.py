# -*- coding: utf-8 -*-


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

    def parse_TermFilterNode(self, node):
        if node.op == '>':
            prop_query = '{0}:[{1} TO *]'.format(
                node.propname,
                node.value
            )

        elif node.op == '>=':
            prop_query = '{0}:[{1} TO *]'.format(
                node.propname,
                node.value - 1
            )

        elif node.op == '<':
            prop_query = '{0}:[* TO {1}]'.format(
                node.propname,
                node.value - 1
            )

        elif node.op == '>=':
            prop_query = '{0}:[* TO {1}]'.format(
                node.propname,
                node.value
            )

        elif node.op in ['=', '~=']:
            prop_query = '{0}:{1}'.format(
                node.propname,
                node.value
            )

        elif node.op == '!=':
            prop_query = '-{0}:{1}'.format(
                node.propname,
                node.value
            )

        return prop_query

    def parse_AndFilterNode(self, node):
        return '{0} {1}'.format(node.left.query, node.right.query)

    def parse_OrFilterNode(self, node):
        return '{0} {1}'.format(node.left.query, node.right.query)

    def parse_TypedFilterNode(self, node):
        fulltext = ''

        if node.types:
            fulltext += 'type_set:({0})'.format(' OR '.join(node.types))

        if node.filter:
            if fulltext:
                fulltext += ' '

            fulltext += node.filter

        return fulltext
