# -*- coding: utf-8 -*-


class GraphDSLSemantics(object):
    def digit(self, ast):
        return ast

    def symbol(self, ast):
        return ast

    def characters(self, ast):
        return ast

    def identifier(self, ast):
        return ast

    def string(self, ast):
        return ast[1]

    def natural(self, ast):
        return ast

    def sign(self, ast):
        return ast

    def integer(self, ast):
        return int(''.join(ast))

    def decimal(self, ast):
        return ast

    def boolean(self, ast):
        return ast

    def value(self, ast):
        return ast

    def property_name(self, ast):
        return ast

    def alias(self, ast):
        return ast

    def aliased_property(self, ast):
        return ast

    def aliases(self, ast):
        return ast

    def cond_operator(self, ast):
        return ast

    def expression(self, ast):
        return ast

    def type(self, ast):
        return ast

    def types(self, ast):
        return ast

    def property_cond(self, ast):
        return ast

    def properties_cond(self, ast):
        return ast

    def elements(self, ast):
        return ast

    def aliased_elements(self, ast):
        return ast

    def graph_joint(self, ast):
        return ast

    def elt_joint(self, ast):
        return ast

    def backward(self, ast):
        return ast

    def forward(self, ast):
        return ast

    def cardinality(self, ast):
        c1, c2, c3 = ast

        return [
            int(''.join(c1)),
            c2,
            int(''.join(c3))
        ]

    def walk_mode(self, ast):
        return ast

    def base_joint(self, ast):
        return ast

    def node_joint(self, ast):
        return ast

    def relationship_joint(self, ast):
        return ast

    def joint(self, ast):
        return ast

    def path(self, ast):
        return ast

    def walkthrough_stmt(self, ast):
        return ast

    def walkthrough_stmts(self, ast):
        return ast

    def condition(self, ast):
        return ast

    def filter_stmt(self, ast):
        return ast

    def new_property(self, ast):
        return ast

    def new_properties(self, ast):
        return ast

    def new_cardinality(self, ast):
        return int(''.join(ast))

    def new_data(self, ast):
        return ast

    def create_stmt(self, ast):
        return ast

    def read_stmt(self, ast):
        return ast

    def update_keyword(self, ast):
        return ast

    def update_alias(self, ast):
        return ast

    def update_data(self, ast):
        return ast

    def update_stmt(self, ast):
        return ast

    def delete_stmt(self, ast):
        return ast

    def crud_stmt(self, ast):
        return ast

    def request(self, ast):
        return ast
