# -*- coding: utf-8 -*-

from pygments.token import Keyword, Operator, Name, String, Number
from pygments.lexer import RegexLexer, bygroups


class GraphDSLLexer(RegexLexer):
    name = 'GraphDSL'
    aliases = ['graphdsl']
    filenames = []

    tokens = {
        'root': [
            (r'\b(INSERT|SELECT|UPDATE|DELETE)\b', Keyword.Reserved),
            (r'\b(SET|ADDTOSET|UNSET|DELFROMSET)\b', Name.Function),
            (r'\b(FROM|TO|WHERE)\b', Keyword.Namespace),
            (r'\b(AS|AND|OR|FOLLOW)\b', Keyword.Declaration),
            (r'\b(RELS|NODES|REL|NODE)\b', Name.Class),
            (r'\b(DEPTH|BACKWARD|FORWARD|BOTH)\b', Keyword.Constant),
            (r'(L?)(")', bygroups(String.Affix, String), 'string'),
            (r'\b(\d+\.\d*|\.\d+|\d+)\b', Number.Float),
        ],
        'string': [
            (r'"', String, '#pop'),
            (r'\\([\\abfnrtv"\']|x[a-fA-F0-9]{2,4}|'
             r'u[a-fA-F0-9]{4}|U[a-fA-F0-9]{8}|[0-7]{1,3})', String.Escape),
            (r'[^\\"\'\n]+', String),  # all other characters
            (r'\\\n', String),  # line continuation
            (r'\\', String)  # stray backslash
        ]
    }
