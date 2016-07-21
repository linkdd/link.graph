# -*- coding: utf-8 -*-

from b3j0f.conf import Configurable, category, Parameter
from link.graph.cli import CONF_PATH, CATEGORY

from prompt_toolkit.history import InMemoryHistory

from xdg.BaseDirectory import save_cache_path
from time import time
import os


try:
    import sqlite3
    HAVE_SQLITE = True

except ImportError:
    HAVE_SQLITE = False


@Configurable(
    paths=CONF_PATH,
    conf=category(
        CATEGORY,
        Parameter(name='history_size', ptype=int, svalue=200)
    )
)
class HistoryManager(object):
    def __init__(self, *args, **kwargs):
        super(HistoryManager, self).__init__(*args, **kwargs)

        self._history = None
        self.last_cmd = None
        self.db = None

        if HAVE_SQLITE:
            dbpath = os.path.join(
                save_cache_path('graphcli'),
                'history.db'
            )
            self.db = sqlite3.connect(dbpath)
            self.cursor = self.db.cursor()

            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS graphcli_history (
                    ts INT,
                    cmd TEXT
                )
            ''')

    @property
    def history(self):
        if self._history is None:
            self._history = InMemoryHistory()

            for cmd in self.read_history():
                self._history.append('{0};'.format(cmd))
                self.last_cmd = cmd

        return self._history

    def read_history(self):
        if self.db is not None:
            commands = self.cursor.execute('''
                SELECT cmd FROM graphcli_history
                ORDER BY ts DESC
                LIMIT ?
            ''', (self.history_size,))

            for row in reversed(list(commands)):
                yield row[0]

    def add_to_history(self, cmd):
        if cmd != self.last_cmd:
            if self.db is not None:
                ts = int(time())

                self.cursor.execute('''
                    INSERT INTO graphcli_history VALUES (:ts, :cmd)
                ''', {'ts': ts, 'cmd': cmd})

            self.last_cmd = cmd

    def close(self):
        if self.db is not None:
            self.db.commit()
            self.db.close()
