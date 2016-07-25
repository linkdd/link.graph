# -*- coding: utf-8 -*-

from b3j0f.utils.iterable import ensureiterable
from pygments.token import Token


class ChainedToken(object):
    def __init__(self, idx, token, *args, **kwargs):
        super(ChainedToken, self).__init__(*args, **kwargs)

        self.idx = idx
        self.type = token[0]
        self.name = token[1]
        self.prev = None
        self.next = None

    def isof(self, *types):
        return self.type in types

    def called(self, *names):
        return self.name in names

    def __eq__(self, other):
        return self.idx == other.idx

    @classmethod
    def chain_tokens(cls, tokens):
        tokens = [cls(i, token) for i, token in enumerate(tokens)]
        l = len(tokens) - 1

        for tok in tokens:
            if tok.idx > 0:
                tok.prev = tokens[tok.idx - 1]

            if tok.idx < l:
                tok.next = tokens[tok.idx + 1]

        return tokens


class Semantic(object):
    def __init__(self, tokens, *args, **kwargs):
        super(Semantic, self).__init__(*args, **kwargs)

        self.tokens = ChainedToken.chain_tokens(tokens)

    def get_aliases(self):
        return [
            tok.next.name
            for tok in self.tokens
            if tok.called('AS') and tok.next is not None
        ]

    def last_token(self):
        return self.tokens[-1] if len(self.tokens) else None

    def last_keyword(self, exclude=None):
        lkw = None

        if exclude is not None:
            exclude = ensureiterable(exclude)

        else:
            exclude = []

        for tok in reversed(self.tokens):
            if tok.isof(Token.Keyword.Reserved):
                lkw = tok

                if not lkw.called(exclude):
                    break

        return lkw

    def can_match_from(self):
        if len(self.tokens):
            lkw = self.last_keyword(exclude=['FROM', 'TO'])
            ltk = self.last_token()

            return any([
                lkw is None,
                lkw is not None and not lkw.called(
                    'SELECT', 'INSERT', 'UPDATE', 'DELETE',
                    'WHERE', 'AND', 'OR', 'FROM', 'TO'
                ),
                not ltk.called('{', '(', ',') and ltk.isof(
                    Token.Punctuation, Token.Name.Label
                )
            ])

        return True

    def can_match_follow(self):
        if len(self.tokens):
            lkw = self.last_keyword(exclude='AS')
            ltk = self.last_token()

            return all([
                not ltk.called('{', '(', ',') and ltk.isof(
                    Token.Punctuation, Token.Name.Label
                ),
                lkw.called('FROM')
            ])

        return False

    def can_match_walkmode(self):
        if len(self.tokens):
            ltk = self.last_token()
            return ltk.called('FOLLOW')

        return False

    def can_match_walkdir(self):
        if len(self.tokens):
            ltk = self.last_token()

            return ltk.called('DEPTH', 'BREADTH')

        return False

    def is_last_tokens_card(self):
        if len(self.tokens) > 3:
            card = self.tokens[-3:]

            return all([
                card[0].isof(Token.Literal.Number.Float),
                card[1].isof(Token.Punctuation),
                card[2].isof(Token.Literal.Number.Float)
            ])

        return False

    def can_match_elttype(self):
        if len(self.tokens):
            ltk = self.last_token()

            return ltk.called('FROM') or self.is_last_tokens_card()

        return False

    def is_inserting(self):
        if len(self.tokens):
            lkw = self.last_keyword(exclude=['FROM', 'TO', 'AS'])

            return lkw.called('INSERT')

        return False

    def can_match_aliasdef(self):
        if len(self.tokens):
            ltk = self.last_token()
            lkw = self.last_keyword()

            return all([
                ltk.called('}'),
                not lkw.called('FROM', 'TO') and self.is_inserting()
            ])

        return False

    def can_match_select_update_delete(self):
        if len(self.tokens):
            lkw = self.last_keyword()
            ltk = self.last_token()

            return any([
                (lkw == ltk) and not lkw.called(
                    'SELECT', 'INSERT', 'UPDATE', 'DELETE',
                    'WHERE', 'AND', 'OR', 'FROM', 'TO'
                ),
                ltk.isof(
                    Token.Name.Label,
                    Token.Literal.String,
                    Token.Literal.Number.Float,
                    Token.Name.Builtin
                )
            ])

        return False

    def can_match_insert(self):
        if len(self.tokens) == 0:
            return True

        return self.can_match_select_update_delete()

    def can_match_where(self):
        if len(self.tokens):
            lkw = self.last_keyword(exclude=['FROM', 'TO'])
            ltk = self.last_token()

            return all([
                lkw is not None and lkw.called('SELECT', 'DELETE'),
                ltk.isof(Token.Name.Label)
            ])

        return False

    def can_match_andor(self):
        if len(self.tokens):
            lkw = self.last_keyword(exclude=['FROM', 'TO'])
            ltk = self.last_token()

            return all([
                lkw is not None and lkw.called('WHERE', 'AND', 'OR'),
                ltk.isof(
                    Token.Name.Label,
                    Token.Literal.String,
                    Token.Literal.Number.Float,
                    Token.Name.Builtin
                )
            ])

        return False

    def can_match_new_elttype(self):
        if len(self.tokens):
            ltk = self.last_token()

            return ltk.called('INSERT')

        return False

    def can_match_aliases(self):
        if len(self.tokens):
            lkw = self.last_keyword(exclude=['FROM', 'TO'])
            ltk = self.last_token()

            if lkw is not None:
                if lkw.called('SELECT', 'DELETE'):
                    return (lkw == ltk or ltk.isof(Token.Punctuation))

                elif lkw.called('INSERT'):
                    return ltk.called('FROM', 'TO')

                elif lkw.called('UPDATE'):
                    return ltk.isof(Token.Name.Function)

                elif lkw.called('WHERE', 'AND', 'OR'):
                    return (lkw == ltk)

        return False

    def match_walkthrough(self):
        result = []

        if self.can_match_from():
            result.append('FROM')

        if self.can_match_elttype():
            result.extend(['RELS', 'NODES'])

        if self.can_match_follow():
            result.append('FOLLOW')

        if self.can_match_walkmode():
            result.extend(['DEPTH', 'BREADTH'])

        if self.can_match_walkdir():
            result.extend(['BACKWARD', 'FORWARD', 'BOTH'])

        if self.can_match_aliasdef():
            result.append('AS')

        return result

    def match_statements(self):
        result = []

        if self.can_match_insert():
            result.append('INSERT')

        if self.can_match_select_update_delete():
            result.extend(['SELECT', 'UPDATE', 'DELETE'])

        if self.can_match_where():
            result.append('WHERE')

        if self.can_match_andor():
            result.extend(['AND', 'OR'])

        if self.can_match_new_elttype():
            result.extend(['REL', 'NODE'])

        return result

    def match_aliases(self):
        return self.get_aliases() if self.can_match_aliases() else []

    def get_matches(self):
        methods = [
            self.match_walkthrough,
            self.match_statements,
            self.match_aliases
        ]

        result = []

        for method in methods:
            result.extend(method())

        return result
