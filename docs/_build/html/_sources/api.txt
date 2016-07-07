
Fro Interface
=============


Parser
------

``Parser`` objects are immutable. Therefore, many ``Parser`` methods return a new parser instead of modifying the called
parser.

For explanations of terminology like "chomp" and "significant", see :doc:`parser`.

.. py:class:: Parser(object):

    .. py:method:: __neg__()

        Returns a new ``Parser`` that is equivalent to ``self`` but is insignificant.

    .. py:method:: __or__(func)

       Returns a new ``Parser`` object that applies ``func`` to the values produced
       by ``self``.

       Example::

            parser = fro.intp | (lambda x: x * x)
            parser.parse("4")  # evaluates to 16

    .. py:method:: __pos__()

        Returns a ``Parser`` that is equivalent to ``self`` but is significant.

    .. py:method:: __rshift__(func)

        Returns a ``Parser`` object that unpacks the values produced by ``self`` and then applies ``func`` to
        them. Throws an error if the number of unpacked arguments does not equal a number of arguments that ``func``
        can take, or if the value by produced ``self`` is not unpackable. Equivalent to ``self | lambda x: func(*x)``.

        Example::

            parser = fro.comp([fro.intp, r"~,", fro.intp]) >> (lambda x, y: x + y)
            parser.parse("4,5")  # evaluates to 9

    .. py:method:: get()

        Returns a ``Parser`` object that retrieves the sole first element of the value produced by ``self``, and
        throws an error if ``self`` produces an non-iterable value or an iterable value that does not have exactly
        one element. Equivalent to ``self >> lambda x: x``.

        Example::

            # Recall that comp(..) always produces a tuple, in this case a tuple with one value
            parser = fro.comp(r"~\(", fro.intp, r"~\)").get()
            parser.parse("(-3)")  # evaluates to -3

    .. py:method:: loud()

        Returns a ``Parser`` that is equivalent to ``self``, but raises a ``FroParseError``
        on parsing failures.

    .. py:method:: lstrip()

       Returns a ``Parser`` object that is equivalent to ``self``, but ignores and
       consumes leading whitespace.

    .. py:method:: maybe(default=None)

        Returns a ``Parser`` object equivalent to ``self``, but defaults to consuming none of the input
        string and producing ``default`` when ``self`` fails to chomp a string. See :doc:`parser` for an explanation of
        chomping.

        Example::

            parser = fro.comp([fro.rgx(r"ab+").maybe("a"), fro.intp])
            parser.parse("abb3")  # evaluates to ("abb", 3)
            parser.parse("87")  # evaluates to ("a", 87)

    .. py:method:: name(name)

        Returns a ``Parser`` object equivalent to ``self``, but with the given name.

    .. py:method:: parse(string_to_parse)

        Attempts to parse ``string_to_parse``. Returns the produced value, or throws a ``FroParseError`` explaining why
        the parse failed (or returns ``None`` if ``self`` is a "quiet" parser).

    .. py:method:: quiet()

         Return a ``Parser`` object that is equivalent to ``self``, but returns ``None`` on
         parsing failures instead of throwing an error.

    .. py:method:: rstrip()

       Returns a ``Parser`` object that is equivalent to ``self``, but ignores and
       consumes trailing whitespace.

    .. py:method:: strip()

       Returns a ``Parser`` object that is equivalent to ``self``, but ignores and
       consumes leading and trailing whitespace. ``self.strip()`` is equivalent to
       ``self.lstrip().rstrip()``.

Constructing Parsers
--------------------

``Parser`` objects should not be instantiated directly; instead Fro provides factory functions for constructing ``Parser``
instances.

Many of these factory functions input "parser-like" values, or more commonly collections of "parser-like" values.
A ``Parser`` object is a parser-like value, which corresponds to itself. A string ``s`` is also a parser-like value,
and it corresponds to ``fro.rgx(s)``. The decision to automatically cast string to regular expression parser is
primarily intended to make code using the Fro module more concise.

To mark a "parser-like" string as insignificant, prepend it with a tilde (``~``). If you actually want a regular
expression that begins with a tilde, escape it (e.g. ``r"\~..."``). This rule only applies to strings that are used
as "parser-like" values, and not to the first argument of `rgx`, say.

Since strings are not actually ``Parser`` objects, you can't use any of the methods provided by the ``Parser`` class
on them.


.. py:function:: alt(parser_values[, name=None])

    Returns a ``Parser`` that is the alternation of the parsers in ``parser_values``.

    More specifically, the returned parser chomps by successively trying to chomp with the parsers in ``parser_values``,
    and producing the value producing by the first successful chomp, and failing if none of the parsers in
    ``parser_values`` successfully chomp.

    Example::

        parser = fro.alt([r"a*b*c*", r"[0-9]{3}", fro.intp])
        parser.parse("aac")  # evaluates to "aac"
        parser.parse("12")  # evaluates to 12
        parser.parse("235")  # evaluates to "235"
        parser.parse("abc123")  # fails
        parser.parse("")  # evaluates to ""
        parser.parse("1234")  # fails

        # The last one is tricky. When r"a*b*c*" tries to chomp "1234", it fails to chomp.
        # Then, when r"[0-9]{3}" tries to chomp "1234", it chomps off "123", leaving behind "4"
        # This is the first successful chomp, this is what the variable parser chomps. However,
        # since the variable parser did not chomp the entire string "1234", it fails to parse it.


.. py:function:: comp(parser_values[, sep=None, name=None])

    Returns a ``Parser`` that is the composition of the parsers in ``parser_values``.

    More specifically, the returned parser chomps by successively chomping with the parsers in ``parser_values``, and
    produces a tuple of the values produced by ``parser_values``. If ``sep`` is not ``None``, then the returned parser
    will chomp with ``sep`` between each parser in ``parser_values`` (and discard the produced value).

    Example::

        parser = fro.comp([r"ab?c+", r"~,", fro.intp])
        parser.parse("abcc,4")  # evaluates to ("abcc", 4)
        parser.parse("ac,-1")  # evaluates to ("ac", -1)
        parser.parse("abc,0,")  # fails


.. py:function:: group_rgx(regex_string[, name=None])

    Returns a ``Parser`` that consumes the regular expression ``regex_string``, and produces a tuple of the groups of
    the corresponding match. See the `re module <https://docs.python.org/2/library/re.html>`_ for a description of
    regular expression groups.

    Example::

        parser = fro.group_rgx(r"(x*)(y*)(z*)")
        parser.parse("xxz")  # evaluates to ("xx", "", "z")
        parser.parse("wxyz")  # fails

.. py:function:: nested(open_regex_string, close_regex_string[, name=None])

    Returns a ``Parser`` that parses well-nested sequences where the opening token is given by ``open_regex_string`` and
    the closing token given by ``close_regex_string``.

    Example::

        parser = fro.nested(r"\(", r"\)")
        parser.parse("(hello (there))")  # evaluates to "hello (there)"
        parser.parse("(hello (there)")  # fails, no closing ) for the first (

.. py:function:: rgx(regex_string[, name=None])

    Returns a ``Parser`` that parses strings that match the given regular expression, and produces the string it
    consumed.

    Example::

        parser = fro.rgx(r"abc+")
        parser.parse("abccc")  # evaluates to "abccc"
        parser.parse("abd")  # fails

.. py:function:: seq(parser_value[, sep=None, sep_at_start=False, sep_at_end=False])

    Returns a ``Parser`` that parses sequences of the values parsed by ``parser_value``.

    More specifically, the returned parser repeatedly chomps with ``parser_value`` until it fails, and produces a list
    of the values produced by ``parser_value``. If ``sep`` is not ``None``, the returned parser chomps using
    ``sep`` between each ``parser_value`` chomp (and discards the produced value). If ``sep_at_start`` is ``True``, then
    the parser will expect a separator before the first element. Similarly, if ``sep_at_end`` is ``True``, then the parser will
    expect a separator after the first element. If (and only if) both ``sep_at_start`` and ``sep_at_end`` are ``True``,
    the returned parser will expected a separator even if there are no elements.

    Example::

        parser = fro.seq(fro.intp, sep=r",")
        parser.parse("")  # evaluates to []
        parser.parse("1")  # evaluates to [1]
        parser.parse("1,2,3")  # evaluates to [1, 2, 3]
        parser.parse("1,2,3,")  # fails


Built-in Parsers
----------------

For convenience, the Fro module provides several common parsers.

.. py:data:: floatp

   A ``Parser`` that parses floating-point values from their string representations.

.. py:data:: intp

   A ``Parser`` that parses int values from their string representations.

.. py:data:: natp

   A ``Parser`` that parses non-negative integers (i.e. natural numbers) from their string representations.

.. py:data:: posintp

    A ``Parser`` that parses positive integers from their string representations.

FroParseError
-------------

Exceptions raised by the ``parse(..)`` method upon parsing failures.

.. py:class:: FroParseError(Exception)

    .. py:method:: __str__()

        A human readable description of the error. Include both the error messages, and extra information describing the
        location of the error.

    .. py:method:: cause()

        Returns the ``Exception`` that triggered this error, or ``None`` is this error was not triggered by another
        exception

    .. py:method:: context()

        Returns a pretty-printable string that depicts where in the input string the parsing error occurred.

    .. py:method:: end_index()

        Returns the end index of the substring of the input that caused the error

    .. py:method:: messages()

        Returns a non-empty list of ``Message`` objects which describe the reasons for failure.

    .. py:method:: start_index()

        Returns the beginning index of the substring of the input that caused the error

    .. py:class:: Message

        Each ``Message`` object represents an error message describing a reason for failure.

        .. py:method:: __str__()

            Returns a string representation of the message that includes both the content and parser name.

        .. py:method:: content()

            Returns the content of the error message

        .. py:method:: name()

            Returns the name of the parser at which the message was generated, or ``None`` if the parser had no name.