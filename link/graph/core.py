# -*- coding: utf-8 -*-

from b3j0f.conf import category, Parameter
from link.graph.conf import DriverLoader

from link.graph.dsl.generator import single_parser_per_scope
from link.graph.dsl.walker.core import GraphDSLNodeWalker

from link.middleware.core import Middleware, register_middleware
from link.parallel.core import MapReduceMiddleware
from link.kvstore.core import KeyValueStore
from link.graph import CONF_BASE_PATH

from grako.model import ModelBuilderSemantics
import os


def getparser(cls):
    return lambda svalue, **_: cls.get_middleware_by_uri(svalue)


@DriverLoader(
    paths='{0}/manager.conf'.format(CONF_BASE_PATH),
    conf=category(
        'GRAPHMANAGER',
        Parameter(
            name='parallel_backend',
            parser=getparser(MapReduceMiddleware),
            svalue='mapreduce+parallel:///graph'
        ),
        Parameter(
            name='nodes_storage',
            parser=getparser(KeyValueStore),
            svalue='kvstore:///nodes/default'
        ),
        Parameter(
            name='relationships_storage',
            parser=getparser(KeyValueStore),
            svalue='kvstore:///relationships/default'
        )
    )
)
class GraphManager(object):
    """
    Process request and manage access to graph storage.
    """

    def __init__(self, *args, **kwargs):
        super(GraphManager, self).__init__(*args, **kwargs)

        module = single_parser_per_scope()
        self.parser = module.GraphDSLParser(semantics=ModelBuilderSemantics())
        self.walker = GraphDSLNodeWalker(self)

    def mapreduce(self, identifier, mapper, reducer, dataset):
        return self.parallel_backend(identifier, mapper, reducer, dataset)

    def __call__(self, request):
        model = self.parser.parse(request, rule_name='start')
        return self.walker.walk(model)


@register_middleware
class GraphMiddleware(Middleware):

    __protocols__ = ['graph']

    def __init__(self, *args, **kwargs):
        super(GraphMiddleware, self).__init__(*args, **kwargs)

        if self.path:
            cfg = DriverLoader(paths=os.path.join(*self.path))
            graphcls = cfg(GraphManager)

        else:
            graphcls = GraphManager

        self._graph = graphcls()

    def __call__(self, request):
        return self._graph(request)
