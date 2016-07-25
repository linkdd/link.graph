# -*- coding: utf-8 -*-

from link.graph.cli.completion.semantic import Semantic
from link.graph.dsl.lexer import GraphDSLLexer
from pygments.token import Token

from prompt_toolkit.completion import Completer, Completion


class GraphCompleter(Completer):
    def __init__(self, *args, **kwargs):
        super(GraphCompleter, self).__init__(*args, **kwargs)

        self.lexer = GraphDSLLexer()

    def get_tokens(self, request, isnewline):
        tokens = list(self.lexer.get_tokens(request))
        start_pos = 0
        startswith = ''

        if len(tokens) > 0:
            tokens = list(filter(
                lambda tok: tok[1] != '\n',
                tokens
            ))

            word_started = all([
                len(tokens) > 0 and tokens[-1][0] != Token.Text.Whitespace,
                not isnewline
            ])

            if word_started:
                start_pos -= len(tokens[-1][1])
                startswith = tokens[-1][1]
                tokens = tokens[:-1]

        else:
            tokens = []

        return tokens, start_pos, startswith

    def get_completions(self, document, event):
        tokens, start_pos, startswith = self.get_tokens(
            document.text,
            document.cursor_position != 0 and document.cursor_position_col == 0
        )

        tokens = list(filter(
            lambda tok: tok[0] != Token.Text.Whitespace,
            tokens
        ))

        semantic = Semantic(tokens)
        matches = semantic.get_matches()

        return [
            Completion(match, start_position=start_pos)
            for match in matches
            if match.startswith(startswith)
        ]
