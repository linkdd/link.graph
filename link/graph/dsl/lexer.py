# -*- coding: utf-8 -*-

from pygments.lexer import RegexLexer
from pygments.token import Keyword


class GraphDSLLexer(RegexLexer):
    name = 'GraphDSL'
    aliases = ['graphdsl']
    filenames = []

    tokens = {
        'root': [
            (r'(FROM|RELS|NODES|FOLLOW|INSERT|SELECT|UPDATE|DELETE)', Keyword)
        ]
    }
