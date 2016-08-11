import io

from builtins import bytes, str

from fro._implementation import chompers


class Parser(object):
    """
    An immutable parser.
    """

    def __init__(self, chomper):
        self._chomper = chomper

    # public interface

    def parse(self, lines, loud=True):
        """
        Parse an iterable collection of chunks. Returns the produced value, or throws a ``FroParseError``
        explaining why the parse failed (or returns ``None`` if ``loud`` is ``False``).

        :param Iterable[str] lines:
        :param bool loud: if parsing failures should result in an exception
        :return: Value produced by parse
        """
        tracker = chompers.abstract.FroParseErrorTracker()
        state = chompers.state.ChompState(lines)
        box = self._chomper.chomp(state, tracker)
        if box is None:
            return self._failed_parse(state, tracker, False, loud)
        elif not state.at_end():
            return self._failed_parse(state, tracker, True, loud)
        return box.value

    def parse_str(self, string_to_parse, loud=True):
        """
        Attempts to parse ``string_to_parse``. Treats the entire string ``string_to_parse`` as a single
        chunk. Returns the produced value, or throws a ``FroParseError`` explaining why
        the parse failed (or returns ``None`` if ``loud`` is ``False``).

        :param str string_to_parse: string to parse
        :param loud: if parsing failures should result in an exception
        :return: value produced by parse
        """
        return self.parse([string_to_parse], loud)

    def parse_file(self, filename, encoding="utf-8", loud=True):
        """
        Parse the contents of a file with the given filename, treating each line as a separate chunk.
        Returns the produced value, or throws a ``FroParseError`` explaining why
        the parse failed (or returns ``None`` if ``loud`` is ``False``).

        :param filename: filename of file to parse
        :param encoding: encoding of filename to parse
        :param loud: if parsing failures should result in an exception
        :return: value produced by parse
        """
        with io.open(filename, encoding=encoding) as file_to_parse:
            return self.parse(file_to_parse, loud=loud)

    def name(self, name):
        """
        Returns a parser equivalent to ``self``, but with the given name.

        :param str name: name for new parser
        :return: a parser identical to this, but with specified name
        :rtype: Parser
        """
        return Parser(self._chomper.clone(name=name))

    def maybe(self, default=None):
        """
        Returns a parser equivalent to ``self``, but defaults to consuming none of the input
        string and producing ``default`` when ``self`` fails to chomp a string. See :doc:`parser` for an explanation of
        chomping.

        :param Any default: default value to produce
        :return: parser that defaults to consuming nothing and producing ``default`` instead of failing
        :rtype: Parser

        Example::

            parser = fro.comp([fro.rgx(r"ab+").maybe("a"), fro.intp])
            parser.parse_str("abb3")  # evaluates to ("abb", 3)
            parser.parse_str("87")  # evaluates to ("a", 87)
        """
        return Parser(chompers.util.OptionalChomper(
            self._chomper,
            default=default,
            significant=self._chomper.significant(),
            name=self._chomper.name()))

    def append(self, value):
        """
        Returns a parser that chomps with the called parser, chomps with the ``Parser``
        represented by ``value``, and produces the value produced by the called parser. The returned parser has
        the same name as significance as ``self``.

        :param Union[Parser,str] value: parser to "append" to ``self``
        :return: ``value`` appended to ``self``
        :rtype: Parser
        """
        return Parser(chompers.composition.CompositionChomper(
            [self._chomper.clone(significant=True),
             _extract(value).clone(significant=False)],
            significant=self._chomper.significant(),
            name=self._chomper.name())).get()

    def prepend(self, value):
        """
        Returns a parser that chomps with the ``Parser`` represented by ``value``, then chomps
        with ``self``, and produces the value produced by ``self``. The returned parser has
        the same name as significance as ``self``.

        :param Union[Parser,str] value: parser to "prepend" to ``self``
        :return: ``value`` prepended to ``self``
        :rtype: Parser
        """
        return Parser(chompers.composition.CompositionChomper(
            [_extract(value).clone(significant=False),
             self._chomper.clone(significant=True)],
            significant=self._chomper.significant(),
            name=self._chomper.name())).get()

    def lstrip(self):
        """
        Returns a parser that is equivalent to ``self``, but ignores and
        consumes any leading whitespace inside a single chunk. Equivalent to
        ``fro.comp([r"~\s*", self]).get()``, but with the same name and significance as ``self``.

        :return: a parser that ignores leading whitespace inside a single chunk
        :rtype: Parser

        Example::

            parser = fro.rgx(r"[a-z]+").lstrip()

            # Will succeed, producing "hello". It's okay if there's no whitespace
            parser.parse_str("hello")

            # Will succeed, producing "world"
            parser.parse_str("\\nworld")

            # Will succeed, producing "planet". Note that the leading whitespace is
            # confined to a single chunk (even though this chunk is different than
            # the chunk that "planet" appears in)
            parser.parse(["  ", "planet"])

            # Will fail, leading whitespace is across multiple chunks
            parser.parse(["  ", "\\tgalaxy"])
        """
        return self.prepend(r"~\s*")

    def lstrips(self):
        """
        Returns a parser that is equivalent to ``self``, but ignores and
        consumes any leading whitespace across multiple chunks.

        :return: a parser that ignored leading whitespace
        :rtype: Parser

        Example::

            parser = fro.rgx(r"[a-z]+").lstrips()

            # Will succeed, producing "hello". It's okay if there's no whitespace
            parser.parse_str("hello")

            # Will succeed, producing "world"
            parser.parse_str("\\nworld")

            # Will succeed, producing "planet". Note that the leading whitespace is
            # confined to a single chunk (even though this chunk is different than
            # the chunk that "planet" appears in)
            parser.parse(["  ", "planet"])

            # Will succeed, producing "galaxy". Unlike lstrip(), lstrips() can handle
            # whitespace across multiple chunks
            parser.parse(["  ", "\\r\\r", "\\tgalaxy"])
        """
        return self.prepend(until(r"~[^\s]"))

    def rstrip(self):
        """
        Returns a parser that is equivalent to ``self``, but ignores and consumes
        trailing whitespace inside a single chunk. Equivalent to ``fro.comp([self, r"~\s*"]).get()``,
        but with the same name and significance as ``self``.

        :return: parser that ignore trailing whitespace inside a single chunk
        :rtype: Parser

        Example::

            parser = fro.rgx(r"[a-z]+").rstrip()

            # Will succeed, producing "hello". It's okay if there's no whitespace
            parser.parse_str("hello")

            # Will succeed, producing "world"
            parser.parse_str("world\\n")

            # Will succeed, producing "planet". Note that the trailing whitespace is
            # confined to a single chunk (even though this chunk is different than
            # the chunk that "planet" appears in)
            parser.parse(["planet", "    "])

            # Will fail, trailing whitespace is across multiple chunks
            parser.parse(["galaxy\\t", "\\r"])
        """
        return self.append(r"~\s*")

    def rstrips(self):
        """
        Returns a parser that is equivalent to ``self``, but ignores and
        consumes any leading whitespace across multiple chunks.

        :return: parser that ignores leading whitespace
        :rtype: Parser

        Example::

            parser = fro.rgx(r"[a-z]+").lstrips()

            # Will succeed, producing "hello". It's okay if there's no whitespace
            parser.parse_str("hello")

            # Will succeed, producing "world"
            parser.parse_str("world\\n")

            # Will succeed, producing "planet".
            parser.parse(["planet", "   "])

            # Will succeed, producing "galaxy". Unlike rstrip(), rstrips() can handle
            # whitespace spread across multiple chunks
            parser.parse(["galaxy\\n\\n", "  ", "\\r\\r"])
        """
        return self.append(until(r"~[^\s]"))

    def strip(self):
        """
        Returns a parser that is equivalent to ``self``, but ignores and consumes leading and
        trailing whitespace inside a single chunk. ``self.strip()`` is equivalent to
        ``self.lstrip().rstrip()``.

        :return: parser that ignores leading and trailing whitespace inside a single chunk
        :rtype: Parser

        Example::

            parser = fro.rgx(r"[a-z]+").strip()

            # This will succeed, producing "abc". All whitespace is inside a single chunk.
            parser.parse_str(["  abc  \\t"])

            # This will also succeed, producing "abc". All leading whitespace is inside
            # a single chunk, as is all trailing whitespace (even though those chunks
            # are different!)
            parser.parse_str(["\\n\\n", "abc \\t"])

            # This will not succeed. Leading whitespace is spread across multiple chunks.
            parser.parse_str(["\\n\\n", "\\n abc\\t\\r"])
        """
        return self.lstrip().rstrip()

    def strips(self):
        """
        Returns a parser object that is equivalent to ``self``, but ignores and consumes leading
        and trailing whitespace, across chunk boundaries. ``self.strips()`` is equivalent to
        ``self.lstrips().rstrips()``.

        :return: parser that ignores leading and trailing whitespace
        :rtype: Parser

        Example::

            parser = fro.rgx(r"[a-z]+").strips()

            # This will succeed, producing "abc". All whitespace is inside a single chunk.
            parser.parse_str(["  abc  \\t"])

            # This will also succeed, producing "abc".
            parser.parse_str(["\\n\\n", "abc \\t"])

            # This will succeed, producing "abc". Unlike strip(), strips() can handle
            # whitespace that spans multiple chunks.
            parser.parse_str(["\\n\\n", "\\n abc\\t\\r"])
        """
        return self.lstrips().rstrips()

    def unname(self):
        """
        Returns a copy of the called parser that does not have a name.

        :return: a copy of the called parser that does not have a name
        :rtype: Parser
        """
        return Parser(self._chomper.unname())

    def get(self):
        """
        Returns a ``Parser`` object that retrieves the sole first element of the value produced by ``self``, and
        throws an error if ``self`` produces an non-iterable value or an iterable value that does not have exactly
        one element. Equivalent to ``self >> lambda x: x``.

        :return: parser that unpacks the sole produced value
        :rtype: Parser

        Example::

            # Recall that comp(..) always produces a tuple, in this case a tuple with one value
            parser = fro.comp(r"~\(", fro.intp, r"~\)").get()
            parser.parse_str("(-3)")  # evaluates to -3
        """
        return self >> (lambda x: x)

    def __invert__(self):
        """
        Returns a new ``Parser`` that is equivalent to ``self`` but is insignificant.

        :return: an insignificant copy of the called parser
        :rtype: Parser

        Example::

            commap = fro.rgx(r",")
            composition = fro.comp([~fro.intp, ~commap, fro.intp]).get()
            composition.parse("2,3")  # evaluates to 3
        """
        return Parser(self._chomper.clone(significant=False))

    def significant(self):
        """
        Returns a parser that is equivalent to ``self`` but is significant.

        :return: a significant copy of the called parser
        :rtype: Parser
        """
        return Parser(self._chomper.clone(significant=True))

    def __or__(self, func):
        """
        Returns a new ``Parser`` object that applies ``func`` to the values produced
        by ``self``. The new parser has the same name and significance as ``self``.

        :param Callable[[T], U] func: function applied to produced values
        :return: a new parser that maps produced values using ``func``
        :rtype: Parser

        Example::

            parser = fro.intp | (lambda x: x * x)
            parser.parse_str("4")  # evaluates to 16
        """
        return Parser(self._chomper.clone(func=func))

    def __rshift__(self, func):
        """
        Returns a ``Parser`` object that unpacks the values produced by ``self`` and then applies ``func`` to
        them. Throws an error if the number of unpacked arguments does not equal a number of arguments that ``func``
        can take, or if the value by produced ``self`` is not unpackable. Equivalent to ``self | lambda x: func(*x)``.

        The new parser has the same name and significance as ``self``.

        :param Callable[?, U] func: function applied to unpacked produced values
        :return: a new parser that maps produced values using ``func``
        :rtype: Parser

        Example::

            parser = fro.comp([fro.intp, r"~,", fro.intp]) >> (lambda x, y: x + y)
            parser.parse_str("4,5")  # evaluates to 9
        """
        return Parser(self._chomper.clone(func=lambda x: func(*x)))

    # internals

    def _failed_parse(self, state, tracker, valid_value, loud):
        if valid_value:
            curr = state.current()
            col = state.column()
            msg = "Unexpected character {}".format(curr[col])
            chomp_err = chompers.chomp_error.ChompError(msg, state.location())
            tracker.report_error(chomp_err)
        return self._raise(tracker.retrieve_error(), loud)

    def _raise(self, err, loud):
        if not loud:
            return None
        if err is None:
            raise AssertionError("err to raise is None")
        raise err


# --------------------------------------------------------------------
# internals (put first to avoid use before def'n issues)

def _extract(value):
    if value is None:
        return None
    elif isinstance(value, str):
        return rgx(value)._chomper
    elif isinstance(value, bytes):
        return rgx(value)._chomper
    elif isinstance(value, Parser):
        return value._chomper
    else:
        msg = "{} does not represent a parser".format(repr(value))
        raise ValueError(msg)


def _parse_rgx(regex_string):
    """
    :return: a tuple of (modified regex_string, whether significant)
    """
    if regex_string[0:1] == r"~":
        return regex_string[1:], False
    elif regex_string[0:2] == r"\~":
        return regex_string[1:], True
    return regex_string, True


# --------------------------------------------------------------------
# public interface

def alt(parser_values, name=None):
    """
    Returns a parser that is the alternation of the parsers in ``parser_values``.

    More specifically, the returned parser chomps by successively trying to chomp with the parsers in ``parser_values``,
    and producing the value producing by the first successful chomp, and failing if none of the parsers in
    ``parser_values`` successfully chomp.

    :param Iterable[Union[Parser | str]] parser_values: collection of parser values
    :param str name: name of the created parser
    :return: a parser that is the alternation of the parsers in ``parser_values``
    :rtype: Parser

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
    """
    chompers_ = [_extract(p) for p in parser_values]
    return Parser(chompers.alternation.AlternationChomper(
        chompers_, name=name))


def chain(func, name=None):
    """
    Given a function ``func`` which maps one parser to another, returns a parser value that is equivalent
    to a large number of successive calls to ``func``.

    Conceptually, the returned parser is equivalent to ``func(func(func(...)))``. During parsing,
    successive calls to ``func`` are made lazily on an as-needed basis.

    Fro parsers parse top-down, so users of this function should take care to avoid left recursion.
    In general the parser ``func(parser)`` should consume input before delegating
    parsing to the ``parser`` argument.

    :param Callable[[Parser],Union[Parser,str]] func: function from ``Parser`` to parser value
    :param name: name for created parser
    :return: lazily-evaluated infinite parser
    :rtype: Parser

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
    """
    def func_(chomper):
        return _extract(func(Parser(chomper)))
    return Parser(chompers.util.ChainChomper(func_, name=name))


def comp(parser_values, sep=None, name=None):
    """
    Returns a parser that is the composition of the parsers in ``parser_values``.

    More specifically, the returned parser chomps by successively chomping with the parsers in ``parser_values``, and
    produces a tuple of the values produced by ``parser_values``. If ``sep`` is not ``None``, then the returned parser
    will chomp with ``sep`` between each parser in ``parser_values`` (and discard the produced value).

    :param Iterable[Union[Parser,str]] parser_values: collection of parser values to compose
    :param Union[Parser,str] sep: separating parser to use between composition elements
    :param str name: name for the parser
    :return: a parser that is the composition of the parsers ``parser_values``
    :rtype: Parser

    Example::

        parser = fro.comp([r"ab?c+", r"~,", fro.intp])
        parser.parse_str("abcc,4")  # evaluates to ("abcc", 4)
        parser.parse_str("ac,-1")  # evaluates to ("ac", -1)
        parser.parse_str("abc,0,")  # fails
    """
    if isinstance(parser_values, str) or isinstance(parser_values, bytes):
        raise TypeError("Do not pass a string/bytes for the parser_values argument")
    chompers_ = [_extract(p) for p in parser_values]
    return Parser(chompers.composition.CompositionChomper(
        chompers_, sep, name=name))


def group_rgx(regex_string, name=None):
    """
    Returns a parser that consumes the regular expression ``regex_string``, and produces a tuple of the groups of
    the corresponding match. Regular expressions should adhere to the syntax outlined in the
    `re module <https://docs.python.org/3/library/re.html>`_. Also see the
    `re module <https://docs.python.org/3/library/re.html>`_ for a description of regular expression groups.

    :param str regex_string: regular expression
    :param str name: name for the parser
    :return: parser that consumes the regular expression ``regex_string``, and produces a tuple of the groups of
             the corresponding match.
    :rtype: Parser

    Example::

        parser = fro.group_rgx(r"(x*)(y*)(z*)")
        parser.parse_str("xxz")  # evaluates to ("xx", "", "z")
        parser.parse_str("wxyz")  # fails
    """
    rgx_str, significant = _parse_rgx(regex_string)
    return Parser(chompers.regex.GroupRegexChomper(
        rgx_str, significant=significant, name=name))


def nested(open_regex_string, close_regex_string, reducer="".join, name=None):
    """
    Returns a ``Parser`` that parses well-nested sequences where the opening token is given by
    ``open_regex_string`` and the closing token given by ``close_regex_string``.

    The parser passes an iterator containing the chunks of content between the first opening token
    and final closing token into ``reducer``, and produces the resulting value. The default behavior
    is to concatenate the chunks.

    If there are overlapping opening and closing tokens, the token with the earliest start positions wins,
    with ties going to opening tokens.

    :param str open_regex_string: regex for opening tokens
    :param str close_regex_string: regex for closing tokens
    :param Callable[[Iterable[str],T] reducer: function from iterator of chunks to produced value
    :param name:
    :return:

    Example::

        parser = fro.nested(r"\(", r"\)")
        parser.parse_str("(hello (there))")  # evaluates to "hello (there)"
        parser.parse_str("(hello (there)")  # fails, no closing ) for the first (
    """
    return Parser(chompers.nested.NestedChomper(
        open_regex_string,
        close_regex_string,
        reducer,
        name=name))


def rgx(regex_string, name=None):
    """
    Returns a parser that parses strings that match the given regular expression, and produces
    the string it consumed. The regular expressions should adhere to the syntax outlined in the
    `re module <https://docs.python.org/3/library/re.html>`_

    :param str regex_string: regex that parser should match
    :param str name: name for the parser
    :return: parser that parses strings that match the given regular expression
    :rtype: Parser

    Example::

        parser = fro.rgx(r"abc+")
        parser.parse_str("abccc")  # evaluates to "abccc"
        parser.parse_str("abd")  # fails
    """
    rgx_str, significant = _parse_rgx(regex_string)
    return Parser(chompers.regex.RegexChomper(
        rgx_str, significant=significant, name=name))


def seq(parser_value, reducer=list, sep=None, name=None):
    """
    Returns a parser that parses sequences of the values parsed by ``parser_value``.

    More specifically, the returned parser repeatedly chomps with ``parser_value`` until it fails,
    passes an iterator of the produced values as argument to ``reducer``, and produces the
    resulting value. ``reducer`` default to producing a list of the produced values.If ``sep`` is not ``None``, the returned parser chomps using
    ``sep`` between each ``parser_value`` chomp (and discards the produced value).

    :param Union[Parser,str] parser_value: Parser-like value
    :param Callable[[Iterable[str]],T] reducer: function from iterator of chunks to produced value
    :param Union[Parser,str] sep: separating parser to use between adjacent sequence elements
    :param str name: name for the parser
    :return: a parser that parses sequences of the values parsed by ``parser_value``
    :rtype: Parser

    Example::

        parser = fro.seq(fro.intp, sep=r",")
        parser.parse_str("")  # evaluates to []
        parser.parse_str("1")  # evaluates to [1]
        parser.parse_str("1,2,3")  # evaluates to [1, 2, 3]
        parser.parse_str("1,2,3,")  # fails
    """
    return Parser(chompers.sequence.SequenceChomper(
        _extract(parser_value), reducer, _extract(sep), name=name))


def thunk(func, name=None):
    """
    Given a function ``func``, which takes no argument and produces a parser value, returns a parser
    that when chomping, calls ``func()`` and chomps with the resulting parser. This function is primarily
    intended for creating parsers whose behavior is dependent on some sort of external state.

    :param Callable[[],Parser] func:
    :param str name: name for the parser
    :return: a parser that parses with the parsers generated by ``func``
    :rtype: Parser

    Example::

        regex_box = fro.BoxedValue(r"ab*")
        parser = fro.thunk(lambda: regex_box.get(), name="Boxed regex")
        parser.parse_str("abb")  # evaluates to "abb"
        parser.parse_str("aab")  # fails
        box.update(r"cd*")
        parser.parse_str("cdddd")  # evaluates to "cdddd"
        parser.parse_str("abb")  # fails
    """
    return Parser(chompers.util.ThunkChomper(
        lambda: _extract(func()), name=name))


def tie(func, name=None):
    """
    Given a function ``func``, which maps one parser to another parser, returns a cyclic parser whose
    structure matches the parsers returned by ``func``.

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

    :param Callable[[Parser],Parser]  func: function for generating cyclic parser
    :param str name: name for the parser
    :return: a cyclic parser whose structure matches the parsers returned by ``func``
    :rtype: Parser

    Example::

        def func(parser):
            return fro.comp([r"~\(", parser.maybe(0),r"~\)"]) | lambda n: n + 1
        parser = fro.tie(func)
        parser.parse("(())")  # evaluates to 2
        parser.parse("(((())))")  # evaluates to 4
        parser.parse("((()")  # fails
    """
    stub_chomper = chompers.util.StubChomper(name=name)
    stub_parser = Parser(stub_chomper)
    result = func(stub_parser)
    stub_chomper.set_delegate(result._chomper)
    if name is not None:
        result = result.name(name)
    return result


def until(regex_str, reducer=lambda _: None, name=None):
    """
    Returns a parser that consumes all input until it encounters a match to the given regular expression,
    or the end of the input.

    The parser passes an iterator of the chunks it consumed to ``reducer``, and produces the resulting
    value. By default, the parser produces ``None``. The parser does not consume the match when parsing,
    but only everything up until the match.

    :param str regex_str: regex until which the parser will consume
    :param Callable[[Iterable[str]],T] reducer: function from iterator of chunks to produced value
    :param str name: name for the parser
    :return: a parser that consumes all input until it encounters a match to ``regex_str`` or the end of
             the input
    :rtype: Parser

    Example::

        untilp = fro.until(r"a|b",
                           reducer=lambda chunks: sum(len(chunk) for chunk in chunks),
                           name="until a or b")
        parser = fro.comp([untilp, r"apples"], name="composition")
        parser.parse(["hello\\n","world\\n", "apples"])  # evaluates to (12, apples)
    """
    rgx_str, significant = _parse_rgx(regex_str)
    return Parser(chompers.until.UntilChomper(rgx_str, reducer, name=name,
                                              significant=significant))


# nothing before decimal or something before decimal
_floatp = r"(-?\.[0-9]+)|(-?[0-9]+(\.[0-9]*)?)"


#: A parser that parses floating-point values from their string representations.
#:
#: :type: Parser
floatp = (rgx(r"{}([eE][-+]?[0-9]+)?".format(_floatp)) | float).name("float")

#: A parser that parses int values from their string representations.
#:
#: :type: Parser
intp = (rgx(r"-?[0-9]+") | int).name("int")

#: A parser that parses non-negative integers (i.e. natural numbers) from their string representations.
#:
#: :type: Parser
natp = (rgx(r"[0-9]+") | int).name("non-negative int")

#:  A parser that parses positive integers from their string representations.
#:
#: :type: Parser
posintp = (rgx(r"0*[1-9][0-9]*") | int).name("positive int")
