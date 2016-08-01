
Fro Interface
=============


Parser
------

``Parser`` objects are immutable. Therefore, many ``Parser`` methods return a new parser instead of modifying the called
parser.

For explanations of terminology like "chomp" "chunk" and "significant", see :doc:`parser`.

.. py:class:: Parser(object):

    .. py:method:: __invert__()

        Returns a new ``Parser`` that is equivalent to ``self`` but is insignificant.

        Example::

            commap = fro.rgx(r",")
            composition = fro.comp([~fro.intp, ~commap, fro.intp]).get()
            composition.parse("2,3")  # evaluates to 3

    .. py:method:: __or__(func)

       Returns a new ``Parser`` object that applies ``func`` to the values produced
       by ``self``. The new parser has the same name and significance as ``self``.

       Example::

            parser = fro.intp | (lambda x: x * x)
            parser.parse_str("4")  # evaluates to 16

    .. py:method:: __rshift__(func)

        Returns a ``Parser`` object that unpacks the values produced by ``self`` and then applies ``func`` to
        them. Throws an error if the number of unpacked arguments does not equal a number of arguments that ``func``
        can take, or if the value by produced ``self`` is not unpackable. Equivalent to ``self | lambda x: func(*x)``.

        The new parser has the same name and significance as ``self``.

        Example::

            parser = fro.comp([fro.intp, r"~,", fro.intp]) >> (lambda x, y: x + y)
            parser.parse_str("4,5")  # evaluates to 9

    .. py:method:: get()

        Returns a ``Parser`` object that retrieves the sole first element of the value produced by ``self``, and
        throws an error if ``self`` produces an non-iterable value or an iterable value that does not have exactly
        one element. Equivalent to ``self >> lambda x: x``.

        Example::

            # Recall that comp(..) always produces a tuple, in this case a tuple with one value
            parser = fro.comp(r"~\(", fro.intp, r"~\)").get()
            parser.parse_str("(-3)")  # evaluates to -3


    .. py:method:: lstrip()

        Returns a ``Parser`` object that is equivalent to ``self``, but ignores and
        consumes any leading whitespace inside a single chunk. Equivalent to
        ``fro.comp([r"~\s*", self]).get()``, but with the same name and significance as ``self``.

        Example::

            parser = fro.rgx(r"[a-z]+").lstrip()

            # Will succeed, producing "hello". It's okay if there's no whitespace
            parser.parse_str("hello")

            # Will succeed, producing "world"
            parser.parse_str("\nworld")

            # Will succeed, producing "planet". Note that the leading whitespace is
            # confined to a single chunk (even though this chunk is different than
            # the chunk that "planet" appears in)
            parser.parse(["  ", "planet"])

            # Will fail, leading whitespace is across multiple chunks
            parser.parse(["  ", "\tgalaxy"])

    .. py:method:: lstrips()

        Returns a ``Parser`` object that is equivalent to ``self``, but ignores and
        consumes any leading whitespace across multiple chunks.

        Example::

            parser = fro.rgx(r"[a-z]+").lstrips()

            # Will succeed, producing "hello". It's okay if there's no whitespace
            parser.parse_str("hello")

            # Will succeed, producing "world"
            parser.parse_str("\nworld")

            # Will succeed, producing "planet". Note that the leading whitespace is
            # confined to a single chunk (even though this chunk is different than
            # the chunk that "planet" appears in)
            parser.parse(["  ", "planet"])

            # Will succeed, producing "galaxy". Unlike lstrip(), lstrips() can handle
            # whitespace across multiple chunks
            parser.parse(["  ", "\r\r", "\tgalaxy"])

    .. py:method:: maybe(default=None)

        Returns a ``Parser`` object equivalent to ``self``, but defaults to consuming none of the input
        string and producing ``default`` when ``self`` fails to chomp a string. See :doc:`parser` for an explanation of
        chomping.

        Example::

            parser = fro.comp([fro.rgx(r"ab+").maybe("a"), fro.intp])
            parser.parse_str("abb3")  # evaluates to ("abb", 3)
            parser.parse_str("87")  # evaluates to ("a", 87)

    .. py:method:: name(name)

        Returns a ``Parser`` object equivalent to ``self``, but with the given name.

    .. py:method:: parse(chunks[, loud=True])

        Parse an iterable collection of chunks. Returns the produced value, or throws a ``FroParseError`` explaining why
        the parse failed (or returns ``None`` if ``loud`` is ``False``).

    .. py:method:: parse_file(filename[, encoding="utf-8", loud=True])

        Parse the contents of a file with the given filename, treating each line as a separate chunk.
        Returns the produced value, or throws a ``FroParseError`` explaining why
        the parse failed (or returns ``None`` if ``loud`` is ``False``).

    .. py:method:: parse_str(string_to_parse[, loud=False])

        Attempts to parse ``string_to_parse``. Treats the entire string ``string_to_parse`` as a single
        chunk. Returns the produced value, or throws a ``FroParseError`` explaining why
        the parse failed (or returns ``None`` if ``loud`` is ``False``).

    .. py:method:: rstrip()

        Returns a ``Parser`` object that is equivalent to ``self``, but ignores and
        consumes trailing whitespace. Equivalent to ``fro.comp([self, r"~\s*"]).get()``, but with
        the same name and significance as ``self``.

        Example::

            parser = fro.rgx(r"[a-z]+").rstrip()

            # Will succeed, producing "hello". It's okay if there's no whitespace
            parser.parse_str("hello")

            # Will succeed, producing "world"
            parser.parse_str("world\n")

            # Will succeed, producing "planet". Note that the trailing whitespace is
            # confined to a single chunk (even though this chunk is different than
            # the chunk that "planet" appears in)
            parser.parse(["planet", "    "])

            # Will fail, trailing whitespace is across multiple chunks
            parser.parse(["galaxy\t", "\r"])

    .. py:method:: rstrips()

        Returns a ``Parser`` object that is equivalent to ``self``, but ignores and
        consumes any leading whitespace across multiple chunks.

        Example::

            parser = fro.rgx(r"[a-z]+").lstrips()

            # Will succeed, producing "hello". It's okay if there's no whitespace
            parser.parse_str("hello")

            # Will succeed, producing "world"
            parser.parse_str("world\n")

            # Will succeed, producing "planet".
            parser.parse(["planet", "   "])

            # Will succeed, producing "galaxy". Unlike rstrip(), rstrips() can handle
            # whitespace spread across multiple chunks
            parser.parse(["galaxy\n\n", "  ", "\r\r"])

    .. py:method:: significant()

        Returns a ``Parser`` that is equivalent to ``self`` but is significant.

    .. py:method:: strip()

        Returns a ``Parser`` object that is equivalent to ``self``, but ignores and
        consumes leading and trailing whitespace inside a single chunk. ``self.strip()`` is equivalent to
        ``self.lstrip().rstrip()``.

        Example::

            parser = fro.rgx(r"[a-z]+").strip()

            # This will succeed, producing "abc". All whitespace is inside a single chunk.
            parser.parse_str(["  abc  \t"])

            # This will also succeed, producing "abc". All leading whitespace is inside
            # a single chunk, as is all trailing whitespace (even though those chunks
            # are different!)
            parser.parse_str(["\n\n", "abc \t"])

            # This will not succeed. Leading whitespace is spread across multiple chunks.
            parser.parse_str(["\n\n", "\n abc\t\r"])


    .. py:method:: strips()

        Returns a ``Parser`` object that is equivalent to ``self``, but ignores and consumes
        leading and trailing whitespace, across chunk boundaries. ``self.strips()`` is equivalent to
        ``self.lstrips().rstrips()``.

        Example::

            parser = fro.rgx(r"[a-z]+").strips()

            # This will succeed, producing "abc". All whitespace is inside a single chunk.
            parser.parse_str(["  abc  \t"])

            # This will also succeed, producing "abc".
            parser.parse_str(["\n\n", "abc \t"])

            # This will succeed, producing "abc". Unlike strip(), strips() can handle
            # whitespace that spans multiple chunks.
            parser.parse_str(["\n\n", "\n abc\t\r"])

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


.. py:function:: alt(parser_values[, name=None])

    Returns a ``Parser`` that is the alternation of the parsers in ``parser_values``.

    More specifically, the returned parser chomps by successively trying to chomp with the parsers in ``parser_values``,
    and producing the value producing by the first successful chomp, and failing if none of the parsers in
    ``parser_values`` successfully chomp.

    Example::

        parser = fro.alt([r"a*b*c*", r"[0-9]{3}", fro.intp])
        parser.parse_str("aac")  # evaluates to "aac"
        parser.parse_str("12")  # evaluates to 12
        parser.parse_str("235")  # evaluates to "235"
        parser.parse_str("abc123")  # fails
        parser.parse_str("")  # evaluates to ""
        parser.parse_str("1234")  # fails

        # The last one is tricky. When r"a*b*c*" tries to chomp "1234", it fails to chomp.
        # Then, when r"[0-9]{3}" tries to chomp "1234", it chomps off "123", leaving behind
        # "4". This is the first successful chomp, so this is what the variable parser chomps.
        # However, since the variable parser did not chomp the entire string "1234", it fails
        # to parse it.


.. py:function:: chain(func[, name=None])

    Given a function ``func`` which maps one parser to another, returns a ``Parser`` that is equivalent
    to a large number of successive calls to ``func``.

    Conceptually, the returned parser is equivalent to ``func(func(func(...)))``. During parsing,
    successive calls to ``func`` are made lazily on a as-needed basis.

    Fro parsers parse top-down, so users of this function should take care to avoid left recursion.
    In general the parser ``func(parser)`` should consume input before delegating
    parsing to the ``parser`` argument.

    Example::

        box = fro.BoxedValue(None)
        def wrap(parser):
            openp = fro.rgx(r"[a-z]", name="open") | box.update_and_get
            closep = fro.thunk(lambda: box.get(), name="close")
            return fro.comp([~openp, parser.maybe(0), ~closep]) >> lambda n: n + 1
        parser = fro.chain(wrap)
        parser.parse_str("aa")  # evaluates to 1
        parser.parse_str("ab")  # fails
        parser.parse_str("aeiiea")  # evaluates to 3
        parser.parse_str("aeiie")  # fails

.. py:function:: comp(parser_values[, sep=None, name=None])

    Returns a ``Parser`` that is the composition of the parsers in ``parser_values``.

    More specifically, the returned parser chomps by successively chomping with the parsers in ``parser_values``, and
    produces a tuple of the values produced by ``parser_values``. If ``sep`` is not ``None``, then the returned parser
    will chomp with ``sep`` between each parser in ``parser_values`` (and discard the produced value).

    Example::

        parser = fro.comp([r"ab?c+", r"~,", fro.intp])
        parser.parse_str("abcc,4")  # evaluates to ("abcc", 4)
        parser.parse_str("ac,-1")  # evaluates to ("ac", -1)
        parser.parse_str("abc,0,")  # fails


.. py:function:: group_rgx(regex_string[, name=None])

    Returns a ``Parser`` that consumes the regular expression ``regex_string``, and produces a tuple of the groups of
    the corresponding match. Regular expressions should adhere to the syntax outlined in the
    `re module <https://docs.python.org/3/library/re.html>`_. Also see the
    `re module <https://docs.python.org/3/library/re.html>`_ for a description of regular expression groups.

    Example::


        parser = fro.group_rgx(r"(x*)(y*)(z*)")
        parser.parse_str("xxz")  # evaluates to ("xx", "", "z")
        parser.parse_str("wxyz")  # fails

.. py:function:: nested(open_regex_string, close_regex_string[, reducer="".join, name=None])

    Returns a ``Parser`` that parses well-nested sequences where the opening token is given by
    ``open_regex_string`` and the closing token given by ``close_regex_string``.

    The parser passes an iterator containing the chunks of content between the first opening token
    and final closing token into ``reducer``, and produces the resulting value. The default behavior
    is to concatenate the chunks.

    If there are overlapping opening and closing tokens, the token with the earliest start positions wins,
    with ties going to opening tokens.

    Example::

        parser = fro.nested(r"\(", r"\)")
        parser.parse_str("(hello (there))")  # evaluates to "hello (there)"
        parser.parse_str("(hello (there)")  # fails, no closing ) for the first (

.. py:function:: rgx(regex_string[, name=None])

    Returns a ``Parser`` that parses strings that match the given regular expression, and produces
    the string it consumed. The regular expressions should adhere to the syntax outlined in the
    `re module <https://docs.python.org/3/library/re.html>`_

    Example::

        parser = fro.rgx(r"abc+")
        parser.parse_str("abccc")  # evaluates to "abccc"
        parser.parse_str("abd")  # fails

.. py:function:: seq(parser_value[, reducer=list, sep=None, name=None])

    Returns a ``Parser`` that parses sequences of the values parsed by ``parser_value``.

    More specifically, the returned parser repeatedly chomps with ``parser_value`` until it fails,
    passes an iterator of the produced values as argument to ``reducer``, and produces the
    resulting value. ``reducer`` default to producing a list of the produced values.If ``sep`` is not ``None``, the returned parser chomps using
    ``sep`` between each ``parser_value`` chomp (and discards the produced value).

    Example::

        parser = fro.seq(fro.intp, sep=r",")
        parser.parse_str("")  # evaluates to []
        parser.parse_str("1")  # evaluates to [1]
        parser.parse_str("1,2,3")  # evaluates to [1, 2, 3]
        parser.parse_str("1,2,3,")  # fails

.. py:function:: thunk(func[, name=None])

    Given a function ``func``, which takes no argument and produces a parser value, returns a parser
    that when chomping, calls ``func()`` and chomps with the resulting parser. This function is primarily
    intended for creating parsers whose behavior is dependent on some sort of external state.

    Example::

        regex_box = fro.BoxedValue(r"ab*")
        parser = fro.thunk(lambda: regex_box.get(), name="Boxed regex")
        parser.parse_str("abb")  # evaluates to "abb"
        parser.parse_str("aab")  # fails
        box.update(r"cd*")
        parser.parse_str("cdddd")  # evaluates to "cdddd"
        parser.parse_str("abb")  # fails

.. py:function:: tie(func[, name=None])

    Given a function ``func``, which maps one parser to another parser, returns a cyclic parser that
    whose structure matches the parsers returned by ``func``.

    Conceptually, what happens is::

        stub = some_placeholder
        result = func(stub)
        ... # in result, replace all references to stub to instead point back to result

    The parser ``tie(func)`` is equivalent to ``chain(func)``, except that ``tie(func)`` is a
    cyclic parser, whereas ``chain(func)`` is a lazily-evaluated infinite parser.
    This difference is relevant only when the corresponding parsers are dependent on external state.
    In other cases, it is more memory-efficient to use ``tie(func)``.

    Fro parsers parse top-down, so users of this function should take care to avoid left recursion.
    In general the parser ``func(parser)`` should consume input before delegating
    parsing to the ``parser`` argument.

    Since parsers are immutable, the only way to create a self-referencing parser is via ``tie(..)``.

    Example::

        def func(parser):
            return fro.comp([r"~\(", parser.maybe(0),r"~\)"]) | lambda n: n + 1
        parser = fro.tie(func)
        parser.parse("(())")  # evaluates to 2
        parser.parse("(((())))")  # evaluates to 4
        parser.parse("((()")  # fails

.. py:function:: until(regex_string[, reducer=lambda _: None, name=None])

    Returns a parser that consumes all input until it encounters a match to the given regular expression,
    or the end of the input.

    The parser passes an iterator of the chunks it consumed to ``reducer``, and produces the resulting
    value. By default, the parser produces ``None``. The parser does not consume the match when parsing,
    but only everything up until the match.

    Example::

        untilp = fro.until(r"a|b",
                           reducer=lambda chunks: sum(len(chunk) for chunk in chunks),
                           name="until a or b")
        parser = fro.comp([untilp, r"apples"], name="composition")
        parser.parse(["hello\n","world\n", "apples"])  # evaluates to (12, apples)


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

`FroParseError` exceptions are raised by the ``parse(..)`` family of methods upon parsing failures.

.. py:class:: FroParseError(Exception)

    .. py:method:: __str__()

        A human readable description of the error. Include both the error messages, and extra information describing the
        location of the error. Equivalent to ``to_str()``.

    .. py:method:: cause()

        Returns the ``Exception`` that triggered this error, or ``None`` is this error was not triggered by another
        exception

    .. py:method:: column(index_from=1)

        Returns the column number where the error occurred, or more generally the
        index inside the chunk where the error occurred. Indices are indexed from
        ``index_from``.

    .. py:method:: context()

        Returns a pretty-printable string that depicts where in the input string the parsing error occurred.

    .. py:method:: end_index()

        Returns the end index of the substring of the input that caused the error

    .. py:method:: line(index_from=1)

        Returns the line number where the error occurred, or more generally
        the index of the chunk where the error occurred. Indices are indexed from
        ``index_from``.

    .. py:method:: messages()

        Returns a non-empty list of ``Message`` objects which describe the reasons for failure.

    .. py:method:: to_str(index_from=1, filename=None)

        Returns a readable description of the error, with indices starting at ``index_from``, and a
        filename of ``filename`` include if a filename is provided. Include both the error messages, and extra information describing the
        location of the error. This method is identical to ``__str__()``, but is configurable.

    .. py:class:: Message

        Each ``Message`` object represents an error message describing a reason for failure.

        .. py:method:: __str__()

            Returns a string representation of the message that includes both the content and parser name.

        .. py:method:: content()

            Returns the content of the error message

        .. py:method:: name()

            Returns the name of the parser at which the message was generated, or ``None`` if the parser had no name.


BoxedValue
----------

To facilitate creating parser that dependent on external state, the Fro module offers the
``BoxedValue`` class. For an example of their usage, see :ref:`xml-example`.

.. py:class:: BoxedValue

    .. py:method:: __init__(value)

        Initialize the box with ``value``

    .. py:method:: get()

        Return the box's current value

    .. py:method:: get_and_update(value)

        Update the box's value to ``value``, and return the previous value

    .. py:method:: update(value)

        Update the box's value to ``value``

    .. py:method:: update_and_get(value)

        Update the box's value to ``value``, and return the new value
