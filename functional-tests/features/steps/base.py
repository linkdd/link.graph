# -*- coding: utf-8 -*-

from b3j0f.conf import Configuration, Category, Parameter, applyconfiguration
from link.graph.core import GraphManager
from aloe import world, step
import json


@step(r'I have a graph with:')
def initialize_graph(step):
    conf = Configuration()
    cat = Category('scenario')

    for line in step.multiline.splitlines():
        param, value = line.split('=', 1)
        cat += Parameter(name=param, svalue=value)

    world.graph = GraphManager()
    applyconfiguration([world.graph], conf=conf)


@step(r'I can execute the request "([^"]*)"')
def execute_request(step, requestfile):
    with open(requestfile) as f:
        world.result = world.graph(f.read())


@step(r'I have the same result as "([^"]*)"')
def verify_result(step, resultfile):
    with open(resultfile) as f:
        result = json.load(f)

        assert result == world.result
