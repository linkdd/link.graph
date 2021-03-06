# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from b3j0f.conf import Configurable, category, Parameter

from link.graph.cli.history import HistoryManager
from link.graph.cli import CONF_PATH, CATEGORY
from link.graph.dsl.lexer import GraphDSLLexer
from link.graph.core import GraphMiddleware
from link.graph import __version__

from prompt_toolkit.key_binding.manager import KeyBindingManager
from prompt_toolkit.layout.lexers import PygmentsLexer
from prompt_toolkit.styles import style_from_pygments
from prompt_toolkit.token import Token
from prompt_toolkit.keys import Keys
from prompt_toolkit import prompt

from pygments.styles import get_style_by_name

from six import print_


@Configurable(
    paths=CONF_PATH,
    conf=category(
        CATEGORY,
        Parameter(name='color_scheme', svalue='default'),
        Parameter(name='tab_width', ptype=int, svalue='4')
    )
)
class GraphCLI(object):
    def __init__(self, graphuri, *args, **kwargs):
        super(GraphCLI, self).__init__(*args, **kwargs)

        self.graph = GraphMiddleware.get_middleware_by_uri(graphuri)
        self.kbmgr = KeyBindingManager.for_prompt()
        self.histmgr = HistoryManager()

        self.register_shortcuts()

    def register_shortcuts(self):
        self.kbmgr.registry.add_binding(Keys.ControlJ)(self.newline_or_execute)
        self.kbmgr.registry.add_binding(Keys.ControlC)(self.cancel_input)
        self.kbmgr.registry.add_binding(Keys.ControlI)(self.tab_or_complete)

    def newline_or_execute(self, event):
        buf = event.current_buffer
        doc = buf.document

        if buf.complete_state:
            compl = buf.complete_state.current_completion

            if compl:
                compl.text += ' '
                buf.apply_completion(compl)

            else:
                buf.cancel_completion()

        else:
            text = doc.text.strip()

            if len(text) > 0 and text[-1] == ';':
                buf.accept_action.validate_and_handle(event.cli, buf)

            else:
                buf.newline()

    def cancel_input(self, event):
        buf = event.current_buffer

        if buf.complete_state:
            buf.cancel_completion()

        else:
            buf.reset()

    def tab_or_complete(self, event):
        buf = event.current_buffer

        if not buf.complete_state:
            doc = buf.document
            col = doc.cursor_position_col
            nbspaces = ((col // self.tab_width) + 1) * self.tab_width

            buf.insert_text(' ' * nbspaces)

    def get_title(self):
        return 'GraphCLI v{0}'.format(__version__)

    def continuation_tokens(self, cli, width):
        return [
            (Token, '.' * (width - 1) + ' ')
        ]

    def __call__(self):
        print_(self.get_title())

        while True:
            try:
                request = prompt(
                    '>>> ',
                    multiline=True,
                    get_title=self.get_title,
                    get_continuation_tokens=self.continuation_tokens,
                    key_bindings_registry=self.kbmgr.registry,
                    lexer=PygmentsLexer(GraphDSLLexer),
                    style=style_from_pygments(
                        get_style_by_name(self.color_scheme),
                        {}
                    ),
                    history=self.histmgr.history,
                    enable_history_search=True,
                )

                requests = [req.strip() for req in request.split(';')]

                for request in requests:
                    if request:
                        try:
                            result = self.graph(request)
                            self.histmgr.add_to_history(request)
                            print_(result)

                        except Exception as err:
                            print_('Error:', err)

            except EOFError:
                break

        self.histmgr.close()
        print_('Goodbye!')
