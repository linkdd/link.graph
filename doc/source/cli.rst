Command Line Interface
======================

The command line interface can be started with the command ``graphcli``:

.. code-block::

   $ graphcli
   GraphCLI v0.1
   >>>

Use ``Ctrl+D`` to exit:

.. code-block::

   $ graphcli
   GraphCLI v0.1
   >>>
   Good bye!

Commands history is saved in a **SQLite3** database (if available), located at:
``~/.cache/graphcli/history.db``.

The configuration is stored in ``$B3J0F_CONF_DIR/link/graph/cli.conf``:

.. code-block:: ini

   [GRAPHCLI]

   color_scheme = default  # syntax highliting in command line (see Pygments documentation)
   history_size = 200  # number of commands to be loaded when graphcli is started
