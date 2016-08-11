
Fro Interface
=============

Parser
------

``Parser`` objects are immutable. Therefore, many ``Parser`` methods return a new parser instead of modifying the called
parser.

For explanations of terminology like "chomp" "chunk" and "significant", see :doc:`parser`.

.. autoclass:: fro.Parser()
    :members:


Constructing Parsers
--------------------

``Parser`` objects should not be instantiated directly; instead Fro provides factory functions for constructing ``Parser``
instances.

Many of these factory functions input "parser-like" values, or more commonly collections of "parser-like" values.
A ``Parser`` object is a parser-like value, which corresponds to itself. A string ``s`` is also a parser-like value,
and it corresponds to ``fro.rgx(s)``. The decision to automatically cast string to regular expression parser is
primarily intended to make the client code using the Fro module more concise.

To mark a "parser-like" regular expression as insignificant, prepend it with a tilde (``~``).
If you actually want a regular expression that begins with a tilde, escape it (e.g. ``r"\~..."``).
This rule only applies to strings that are used as "parser-like" values. It does not apply in other
context where regular expression are used, such as the argument of `rgx(..)`.


.. autofunction:: fro._implementation.parser.alt

.. autofunction:: fro._implementation.parser.chain

.. autofunction:: fro._implementation.parser.comp

.. autofunction:: fro._implementation.parser.group_rgx

.. autofunction:: fro._implementation.parser.nested

.. autofunction:: fro._implementation.parser.rgx

.. autofunction:: fro._implementation.parser.seq

.. autofunction:: fro._implementation.parser.thunk

.. autofunction:: fro._implementation.parser.tie

.. autofunction:: fro._implementation.parser.until

Built-in Parsers
----------------

For convenience, the Fro module provides several common parsers.

.. .. automodule:: fro._implementation.parser
   :special-members:

.. autodata:: fro._implementation.parser.floatp

.. autodata:: fro._implementation.parser.intp

.. autodata:: fro._implementation.parser.natp

.. autodata:: fro._implementation.parser.posintp


FroParseError
-------------

`FroParseError` exceptions are raised by the ``parse(..)`` family of methods upon parsing failures.

.. autoexception:: fro._implementation.parse_error::FroParseError()
    :members:

.. autoclass:: fro._implementation.parse_error::FroParseError.Message()
    :members:

BoxedValue
----------

To facilitate creating parser that dependent on external state, the Fro module offers the
``BoxedValue`` class. For an example of their usage, see :ref:`xml-example`.

.. autoclass:: fro._implementation.boxed_value.BoxedValue
    :members:
