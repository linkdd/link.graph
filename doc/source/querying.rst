Graph Querying Language
=======================

A query to the graph is composed of two distinct parts:

 - the ``walk through`` part, used to walk through the graph and select sets of elements
 - the ``operations`` part, used to execute operations on the selected sets

Walk through
------------

The first statement of the walk-through is used to selects elements from the graph,
creating a sub-graph:

.. code-block::

   FROM <element filter>

A second ``FROM`` statements will select another sub-graph, from the sub-graph
selected by the previous statement.

It can be followed by a ``FOLLOW`` statement used to reduce the walked elements:

.. code-block::

   FROM
       <element filter>
   FROM
       <element filter>
   FOLLOW <DEPTH|BREADTH> <BACKWARD|FORWARD|BOTH> <mindepth>..<maxdepth>
       <element filter>
   FROM
       <element filter>
   FOLLOW <DEPTH|BREADTH> <BACKWARD|FORWARD|BOTH> <mindepth>..<maxdepth>
       <element filter>

Element filter
--------------

A filter is composed of:

 - a filter type
 - a list of element's types
 - a list of conditions
 - an optional alias

.. code-block::

   <filter type> (<element types>) { <conditions> } [ AS <alias> ]

There is two type of filters:

 - node filters: ``NODES``
 - relationship filters: ``RELS``

A condition is used to filter elements according to their properties:

.. code-block::

   RELS(r1, r2, r3) { weight > 2, weight < 10 } AS rels0
   NODES(n1, n2, n3) { foo = "bar" } AS nodes0

Operations
----------

There is 4 types of operations:

 - ``SELECT`` used to fetch aliased elements
 - ``INSERT`` used to create new elements (may be aliased)
 - ``UPDATE`` used to update aliased elements
 - ``DELETE`` used to delete aliased elements

Read operations
~~~~~~~~~~~~~~~

A ``SELECT`` statement expects a list of alias to be returned, and optionally a
filter for each alias:

.. code-block::

   SELECT
       alias1
       alias2
       alias3 { <filter> }

Here, a filter is a condition on properties from aliased elements, example:

.. code-block::

   alias1 { foo > 2 AND foo < 5 OR foo = 8 }

Create operations
~~~~~~~~~~~~~~~~~

An ``INSERT`` statement expects one of two kinds of element definition that can
be aliased for further use:

 - node definition
 - relationship definition, which expects a set of source nodes and a set of target nodes

.. code-block::

   INSERT
       NODE(<new node types>) { <new node assignations> } AS alias0

   INSERT
       REL(<new relationship types) { <new relationship assignations> }

       FROM
           <alias or node filter>
       TO
           <alias or node filter>

For example:

.. code-block::

   INSERT
       NODE(n2) {
           ADDTOSET foo "bar"
       } AS elt18
   INSERT
       REL(r3) {
           SET weight 2
       }
       FROM
           NODES(n4) { foo = "buzz" }
       TO
           elt18

Update operations
~~~~~~~~~~~~~~~~~

An ``UPDATE`` statement expects a set of new assignations on aliased properties:

.. code-block::

   UPDATE ( <assignations> )

For example:

.. code-block::

   UPDATE (
       SET alias2.weight 17
       ADDTOSET alias0.bar "baz"
       UNSET alias1.foo
       DELFROMSET alias0.bar "biz"
   )

Delete operations
~~~~~~~~~~~~~~~~~

A ``DELETE`` statement have exactly the same syntax as a ``SELECT`` statement:

.. code-block::

   DELETE
       alias1
       alias2
       alias3 { foo > 2 AND foo < 5 OR foo = 8 }
