import re

from builtins import bytes, str

from fro._implementation import chompers, iters, parse_error


class FroParser(object):
    """
    An immutable parser
    """
    def __init__(self, chomper, quiet=False):
        self._chomper = chomper
        self._quiet = quiet

    # public interface

    def parse(self, lines):
        """
        Parses the string into an object
        :param lines: lines to parse
        :return: value parsed, or None if parse failed (and no exception was thrown)
        """
        tracker = chompers.abstract.FroParseErrorTracker()
        state = chompers.state.ChompState(iters.Stream(lines))
        box = self._chomper.chomp(state, tracker)
        if box is None:
            return self._failed_parse(state, tracker, False)
        elif not state.at_end():
            return self._failed_parse(state, tracker, True)
        return box.value

    def parse_str(self, string_to_parse):
        return self.parse([string_to_parse])

    def name(self, name):
        """
        :return: a parser identical to this, but with specified name
        """
        return FroParser(self._chomper.clone(name=name))

    def maybe(self, default=None):
        return FroParser(chompers.util.OptionalChomper(
            self._chomper,
            default=default,
            fertile=self._chomper.fertile(),
            name=self._chomper.name()))

    def quiet(self):
        return FroParser(self._chomper, quiet=True)

    def loud(self):
        return FroParser(self._chomper, quiet=False)

    def lstrip(self):
        if self._chomper.fertile():
            chomper = chompers.composition.CompositionChomper(
                [chompers.regex.RegexChomper(r"\s*", fertile=False), self._chomper],
                fertile=True,
                name=self._chomper.name())
            return FroParser(chomper, quiet=self._quiet).get()
        return -((+self).lstrip())

    def rstrip(self):
        if self._chomper.fertile():
            chomper = chompers.composition.CompositionChomper(
                [self._chomper, chompers.regex.RegexChomper(r"\s*", fertile=False)],
                fertile=True,
                name=self._chomper.name())
            return FroParser(chomper, quiet=self._quiet).get()
        return -((+self).rstrip())

    def strip(self):
        return self.lstrip().rstrip()

    def unname(self):
        return FroParser(self._chomper.unname())

    def get(self):
        return self >> (lambda x: x)

    def dependent(self, func, name=None):
        return FroParser(chompers.util.DependentChomper(
            self._chomper,
            lambda x: _extract(func(x)),
            name=name))

    def __neg__(self):
        """
        :return: an infertile copy of the called parser
        """
        if not self._chomper.fertile():
            return self
        return FroParser(chompers.util.DelegateChomper(
            self._chomper,
            fertile=False,
            name=self._chomper.name()))

    def __pos__(self):
        """
        :return: a fertile copy of the called parser
        """
        if self._chomper.fertile():
            return self
        return FroParser(chompers.util.DelegateChomper(
            self._chomper,
            fertile=True,
            name=self._chomper.name()))

    def __or__(self, func):
        return FroParser(chompers.util.MapChomper(
            self._chomper,
            func,
            fertile=self._chomper.fertile(),
            name=self._chomper.name()))

    def __rshift__(self, func):
        return FroParser(chompers.util.MapChomper(
            self._chomper,
            lambda x: func(*x),
            fertile=self._chomper.fertile(),
            name=self._chomper.name()))

    # internals

    def _failed_parse(self, state, tracker, valid_value):
        if valid_value:
            curr = state.current()
            col = state.column()
            msg = "Unexpected character {}".format(curr[col])
            chomp_err = chompers.chomp_error.ChompError(msg, state.location())
            tracker.report_error(chomp_err)
        return self._raise(tracker.retrieve_error())

    def _raise(self, err):
        if self._quiet:
            return None
        if err is None:
            raise AssertionError()
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
    elif isinstance(value, FroParser):
        return value._chomper
    else:
        msg = "{} does not represent a parser".format(repr(value))
        raise ValueError(msg)


def _parse_rgx(regex_string):
    """
    :return: a tuple of (modified regex_string, whether fertile)
    """
    if regex_string[0:1] == r"~":
        return regex_string[1:], False
    elif regex_string[0:2] == r"\~":
        return regex_string[1:], True
    return regex_string, True


# --------------------------------------------------------------------
# public interface

def alt(parser_values, name=None):
    chompers_ = [_extract(p) for p in parser_values]
    return FroParser(chompers.alternation.AlternationChomper(
        chompers_, name=name))


def chain(func, name=None):
    def func_(chomper):
        return _extract(func(FroParser(chomper)))
    return FroParser(chompers.util.LazyChomper(func_, name=name))


def comp(parser_values, sep=None, name=None):
    if isinstance(parser_values, str) or isinstance(parser_values, bytes):
        raise TypeError("Do not pass a string/bytes for the parser_values argument")
    chompers_ = [_extract(p) for p in parser_values]
    return FroParser(chompers.composition.CompositionChomper(
        chompers_, sep, name=name))


def group_rgx(regex_string, name=None):
    rgx_str, fertile = _parse_rgx(regex_string)
    return FroParser(chompers.regex.GroupRegexChomper(
        rgx_str, fertile=fertile, name=name))


def nested(open_regex_string, close_regex_string, reducer="".join, name=None):
    return FroParser(chompers.nested.NestedChomper(
        open_regex_string,
        lambda _: re.compile(close_regex_string),
        reducer,
        name=name))


def rgx(regex_string, name=None):
    rgx_str, fertile = _parse_rgx(regex_string)
    return FroParser(chompers.regex.RegexChomper(
        rgx_str, fertile=fertile, name=name))


def seq(parser_value, reducer=list, sep=None, name=None):
    return FroParser(chompers.sequence.SequenceChomper(
        _extract(parser_value), reducer, _extract(sep), name=name))


def tie(func, name=None):
    stub_chomper = chompers.util.StubChomper(name=name)
    stub_parser = FroParser(stub_chomper)
    result = func(stub_parser)
    stub_chomper.set_delegate(result._chomper)
    if name is not None:
        result = result.name(name)
    return result


def until(regex_str, reducer="".join, name=None):
    return FroParser(chompers.until.UntilChomper(regex_str, reducer, name=name))


# nothing before decimal or something before decimal
_floatp = r"(-?\.[0-9]+)|(-?[0-9]+(\.[0-9]*)?)"
floatp = (rgx(r"{}(e[-+]?[0-9]+)?".format(_floatp)) | float).name("float")

intp = (rgx(r"-?[0-9]+") | int).name("int")
natp = (rgx(r"[0-9]+") | int).name("non-negative int")
posintp = (rgx(r"0*[1-9][0-9]*") | int).name("positive int")
