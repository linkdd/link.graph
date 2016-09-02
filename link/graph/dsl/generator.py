# -*- coding: utf-8 -*-

from b3j0f.conf import Configurable, category, Parameter
from b3j0f.conf.driver.file.base import FileConfDriver

from b3j0f.utils.runtime import singleton_per_scope

from link.utils.grammar import codegenerator
from link.graph import CONF_BASE_PATH

import os


@Configurable(
    paths='{0}/dsl/generator.conf'.format(CONF_BASE_PATH),
    conf=category(
        'DSLGEN',
        Parameter(
            name='grammar',
            value='{0}/dsl/grammar.bnf'.format(CONF_BASE_PATH)
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
        return self._grammar

    @grammar.setter
    def grammar(self, value):
        if value is not None and not os.path.isabs(value):
            fconfdrv = FileConfDriver()
            paths = fconfdrv.rscpaths(value)

            value = paths[0] if paths else None

        self._grammar = value

    def load_grammar(self):
        if self.grammar is None:
            raise GraphDSLGenerator.Error(
                'Grammar is unspecified or not found'
            )

        with open(self.grammar) as f:
            grammar = f.read()

        return grammar

    def __call__(self):
        grammar = self.load_grammar()

        return codegenerator(
            self.modname,
            GraphDSLGenerator.MODEL_PREFIX,
            grammar
        )


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
