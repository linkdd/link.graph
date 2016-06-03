# -*- coding: utf-8 -*-

from b3j0f.conf import Configurable, category, Parameter
from b3j0f.conf.driver.file.base import FileConfDriver

from b3j0f.utils.runtime import singleton_per_scope
from b3j0f.utils.path import lookup

from link.graph import CONF_BASE_PATH

from grako.parser import GrakoGrammarGenerator
from grako.codegen import pythoncg

from six import exec_, string_types
import imp
import sys
import os


@Configurable(
    paths='{0}/dsl/generator.conf'.format(CONF_BASE_PATH),
    conf=category(
        'DSLGEN',
        Parameter(
            name='grammar',
            value='{0}/dsl/grammar.bnf'.format(CONF_BASE_PATH)
        ),
        Parameter(
            name='semantics',
            value='link.graph.dsl.semantics.GraphDSLSemantics'
        ),
        Parameter(name='modname', value='graph_dsl_generated')
    )
)
class GraphDSLGenerator(object):

    MODEL_PREFIX = 'GraphDSL'

    class Error(Exception):
        pass

    @property
    def grammar(self):
        if not hasattr(self, '_grammar'):
            self.grammar = None

        return self._grammar

    @grammar.setter
    def grammar(self, value):
        if value is not None and not os.path.isabs(value):
            fconfdrv = FileConfDriver()
            paths = fconfdrv.rscpaths(value)

            value = paths[0] if paths else None

        self._grammar = value

    @property
    def semantics(self):
        if not hasattr(self, '_semantics'):
            self.semantics = None

        return self._semantics

    @semantics.setter
    def semantics(self, value):
        if isinstance(value, string_types):
            value = lookup(value)

        self._semantics = value

    def load_grammar(self):
        if self.grammar is None:
            raise GraphDSLGenerator.Error(
                'Grammar is unspecified or not found'
            )

        with open(self.grammar) as f:
            grammar = f.read()

        return grammar

    def parse_model(self, grammar):
        parser = GrakoGrammarGenerator(
            GraphDSLGenerator.MODEL_PREFIX,
            filename=self.grammar
        )

        return parser.parse(grammar)

    def generate_code(self, model):
        code = pythoncg(model)

        module = imp.new_module(self.modname)
        exec_(code, module.__dict__)

        module.__dict__[self.semantics.__name__] = self.semantics

        sys.modules[self.modname] = module

        return module

    def __call__(self):
        grammar = self.load_grammar()
        model = self.parse_model(grammar)
        return self.generate_code(model)


def single_parser_per_scope(_scope=None, _renew=False):
    generator = singleton_per_scope(
        GraphDSLGenerator,
        _scope=_scope,
        _renew=_renew
    )

    return singleton_per_scope(
        generator,
        _scope=_scope,
        _renew=_renew
    )
