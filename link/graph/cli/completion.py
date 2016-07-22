# -*- coding: utf-8 -*-

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

    def match_walkthrough(self, tokens):
        if len(tokens) == 0:
            return ['FROM']

        else:
            ltk = tokens[-1]

            if ltk[0] == Token.Keyword.Reserved and ltk[1] != 'AS':
                if ltk[1] == 'FOLLOW':
                    return ['DEPTH', 'BREADTH']

                elif ltk[1] == 'FROM':
                    return ['RELS', 'NODES']

            elif ltk[0] == Token.Keyword.Constant:
                if ltk[1] in ['DEPTH', 'BREADTH']:
                    return ['BACKWARD', 'FORWARD', 'BOTH']

                else:
                    return []

            elif ltk[0] in [Token.Punctuation, Token.Name.Label]:
                lkw = None
                keywords = [
                    'SELECT',
                    'INSERT',
                    'UPDATE',
                    'DELETE',
                    'WHERE', 'AND', 'OR'
                ]

                for token in reversed(tokens):
                    if token[0] == Token.Keyword.Reserved:
                        lkw = token

                        if lkw[1] not in ['FROM', 'TO']:
                            break

                if lkw is None:
                    return ['FROM']

                elif lkw[1] in keywords:
                    return []

                elif ltk[1] not in ['{', '(', ',']:
                    result = ['FROM', 'FOLLOW']

                    if ltk[1] == '}':
                        result.append('AS')

                    return result

            elif len(tokens) > 3:
                card = tokens[-3:]

                iscard = all([
                    card[0][0] == Token.Literal.Number.Float,
                    card[1][0] == Token.Punctuation,
                    card[2][0] == Token.Literal.Number.Float
                ])

                if iscard:
                    return ['RELS', 'NODES']

        return []

    def match_statements(self, tokens):
        if len(tokens) == 0:
            return ['INSERT']

        else:
            ltk = tokens[-1]
            lkw = None
            keywords = [
                'SELECT',
                'INSERT',
                'UPDATE',
                'DELETE',
                'WHERE', 'AND', 'OR'
            ]

            for token in reversed(tokens):
                if token[0] == Token.Keyword.Reserved:
                    lkw = token

                    if lkw[1] not in ['FROM', 'TO']:
                        break

            if lkw is not None and lkw[1] in keywords:
                return []

            else:
                toktypes = [Token.Punctuation, Token.Name.Label]

                if ltk[0] in toktypes and ltk[1] not in ['{', '(', ',']:
                    return ['SELECT', 'INSERT', 'UPDATE', 'DELETE']

        return []

    def match_aliases(self, tokens):
        if len(tokens) == 0:
            return []

        ltk = tokens[-1]
        aliases = [
            token[1]
            for i, token in enumerate(tokens)
            if i > 0 and tokens[i - 1][1] == 'AS'
        ]

        lkw = None
        keywords = [
            'SELECT',
            'INSERT',
            'UPDATE',
            'DELETE',
            'WHERE', 'AND', 'OR'
        ]

        for token in reversed(tokens):
            if token[0] == Token.Keyword.Reserved:
                lkw = token

                if lkw[1] not in ['FROM', 'TO']:
                    break

        if lkw is None:
            return []

        ret = all([
            lkw[1] in keywords,
            any(
                [
                    all(
                        [
                            lkw[1] in ['SELECT', 'DELETE'],
                            lkw == ltk or ltk[0] == Token.Punctuation
                        ]
                    ),
                    lkw[1] == 'INSERT' and ltk[0] == Token.Keyword.Reserved,
                    lkw[1] == 'UPDATE' and ltk[0] == Token.Name.Function,
                    lkw[1] in ['WHERE', 'AND', 'OR'] and lkw == ltk
                ]
            )
        ])

        return aliases if ret else []

    def get_completions(self, document, event):
        tokens, start_pos, startswith = self.get_tokens(
            document.text,
            document.cursor_position != 0 and document.cursor_position_col == 0
        )

        tokens = list(filter(
            lambda tok: tok[0] != Token.Text.Whitespace,
            tokens
        ))

        matches = self.match_walkthrough(tokens)
        matches += self.match_statements(tokens)
        matches += self.match_aliases(tokens)

        matches = list(set(matches))  # uniq

        return [
            Completion(match, start_position=start_pos)
            for match in matches
            if match.startswith(startswith)
        ]
