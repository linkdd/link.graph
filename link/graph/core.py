# -*- coding: utf-8 -*-

from b3j0f.conf import Configurable, category, Parameter

from link.graph.dsl.generator import single_parser_per_scope
from link.graph.dsl.walker.core import GraphDSLNodeWalker

from link.middleware.core import Middleware, register_middleware
from link.parallel.core import MapReduceMiddleware
from link.kvstore.core import KeyValueStore
from link.graph import CONF_BASE_PATH

from grako.model import ModelBuilderSemantics
import os


@Configurable(
    paths='{0}/manager.conf'.format(CONF_BASE_PATH),
    conf=category(
        'GRAPHMANAGER',
        Parameter(
            name='parallel_backend',
            parser=MapReduceMiddleware.get_middleware_by_uri
        ),
        Parameter(
            name='nodes_store',
            parser=KeyValueStore.get_middleware_by_uri
        ),
        Parameter(
            name='relationships_store',
            parser=KeyValueStore.get_middleware_by_uri
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

    def mapreduce(self, mapper, reducer, dataset):
        return self.parallel_backend(mapper, reducer, dataset)

    def __call__(self, request):
        model = self.parser.parse(request, rule_name='start')
        return self.walker.walk(model)


@register_middleware
class GraphMiddleware(Middleware):

    __protocols__ = ['graph']

    def __init__(self, *args, **kwargs):
        super(GraphMiddleware, self).__init__(*args, **kwargs)

        if self.path:
            cfg = Configurable(paths=os.path.join(self.path))
            graphcls = cfg(GraphManager)

        else:
            graphcls = GraphManager

        self._graph = graphcls()

    def __call__(self, request):
        return self._graph(request)
