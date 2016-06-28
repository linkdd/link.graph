# -*- coding: utf-8 -*-

from b3j0f.conf import Configurable, category, Parameter
from link.middleware.core import Middleware

from link.graph.dsl.generator import single_parser_per_scope
from link.graph import CONF_BASE_PATH


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

        self.parser = single_parser_per_scope()

    def call_algorithm(self, dataset, algocls):
        algo = algocls(self)
        return self.parallel_backend(algo.map, algo.reduce, dataset)

    def __call__(self, request):
        model = self.parser.parse(request, rule_name='start')
        print(model)
