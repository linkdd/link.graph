Graph Querying Language
=======================

A query to the graph is composed of two distinct parts:

 - the ``walk through`` part, used to walk through the graph and select sets of elements
 - the ``operations`` part, used to execute operations on the selected sets

Walk through
------------

A walk-through is composed of:

 - ``FROM`` statements, used to define sets of nodes
 - ``THROUGH`` statements, used to walk through aliased relations
 - ``TO`` statements, used to alias the destination nodes

The first ``FROM`` statement is used to selects elements from the graph, creating
a sub-graph:

.. code-block:: text

   FROM <set> <node filter> [ AS <alias> ]

   THROUGH <set> <relation filter> [ AS <alias> ] [ <walk mode> ]

   TO <node filter> <alias>

A second ``FROM`` statements will select another sub-graph, from the alias
created by the previous statement.

.. code-block:: text

   FROM NODES () {} AS nodes0
   FROM nodes0 (n1 n2) { foo = "bar" } AS nodes1
   FROM nodes1 (n1) { bar = "baz" AND baz = "biz" } AS nodes2

   THROUGH
       RELS () {} AS rels0
       DEPTH BACKWARD 5 10
   THROUGH
       rels0 (r1 r2) { weight > 2 } AS rels1
       BREADTH FORWARD 2 *
   THROUGH
       rels1 (r1) {}

   TO
       (n3) {}
       nodes3

   TO
       (n4) {}
       nodes4 

Operations
----------

There is 4 types of operations:

 - ``SELECT`` used to fetch aliased elements
 - ``INSERT`` used to create new elements (may be aliased)
 - ``UPDATE`` used to update aliased elements
 - ``DELETE`` used to delete aliased elements

Read operations
~~~~~~~~~~~~~~~

A ``SELECT`` statement expects a list of alias to be returned

.. code-block:: text

   SELECT alias1, alias2, alias3

Create operations
~~~~~~~~~~~~~~~~~

An ``INSERT`` statement expects one of two kinds of element definition that can
be aliased for further use:

 - node definition
 - relationship definition, which expects a set of source nodes and a set of target nodes

.. code-block:: text

   INSERT
       NODE(<new node types>) { <new node assignations> } AS alias0

   INSERT
       REL(<new relationship types) { <new relationship assignations> }

       SOURCE
           <alias or node filter>
       TARGET
           <alias or node filter>

For example:

.. code-block:: text

   INSERT
       NODE(n2) {
           ADDTOSET foo "bar"
       } AS elt18
   INSERT
       REL(r3) {
           SET weight 2
       }
       SOURCE
           (n4) { foo = "buzz" }
       TARGET
           elt18

Update operations
~~~~~~~~~~~~~~~~~

An ``UPDATE`` statement expects a set of new assignations on aliased properties:

.. code-block:: text

   UPDATE ( <assignations> )

For example:

.. code-block:: text

   UPDATE (
       SET alias2.weight 17
       ADDTOSET alias0.bar "baz"
       UNSET alias1.foo
       DELFROMSET alias0.bar "biz"
   )

Delete operations
~~~~~~~~~~~~~~~~~

A ``DELETE`` statement have exactly the same syntax as a ``SELECT`` statement:

.. code-block:: text

   DELETE alias1, alias2, alias3
