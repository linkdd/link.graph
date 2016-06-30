# -*- coding: utf-8 -*-

from b3j0f.conf import Configurable, category, Parameter

from link.graph.dsl.generator import single_parser_per_scope
from link.graph.dsl.walker import GraphDSLNodeWalker

from link.middleware.core import Middleware
from link.graph import CONF_BASE_PATH

from grako.model import ModelBuilderSemantics


@Configurable(
    paths='{0}/manager.conf'.format(CONF_BASE_PATH),
    conf=category(
        'GRAPHMANAGER',
        Parameter(
            name='parallel_backend',
            parser=Middleware.get_middleware_by_uri
        ),
        Parameter(
            name='nodes_store',
            parser=Middleware.get_middleware_by_uri
        ),
        Parameter(
            name='relationships_store',
            parser=Middleware.get_middleware_by_uri
        ),
        Parameter(
            name='graphs_store',
            parser=Middleware.get_middleware_by_uri
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

    def call_algorithm(self, dataset, algocls):
        algo = algocls(self)
        return self.parallel_backend(algo.map, algo.reduce, dataset)

    def __call__(self, request):
        model = self.parser.parse(request, rule_name='start')
        return self.walker.walk(model)
