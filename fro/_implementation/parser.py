import re

from builtins import bytes, str

from fro._implementation import chompers


class FroParser(object):
    """
    An immutable parser
    """
    def __init__(self, chomper):
        self._chomper = chomper

    # public interface

    def parse(self, lines, loud=True):
        """
        Parses the string into an object
        :param lines: lines to parse
        :param loud: if parsing failures should raise exceptions
        :return: value parsed, or None if parse failed (and no exception was thrown)
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
        return self.parse([string_to_parse], loud)

    def name(self, name):
        """
        :return: a parser identical to this, but with specified name
        """
        return FroParser(self._chomper.clone(name=name))

    def maybe(self, default=None):
        return FroParser(chompers.util.OptionalChomper(
            self._chomper,
            default=default,
            significant=self._chomper.significant(),
            name=self._chomper.name()))

    def append(self, value):
        return FroParser(chompers.composition.CompositionChomper(
            [self._chomper.clone(significant=True),
             _extract(value).clone(significant=False)],
            significant=self._chomper.significant(),
            name=self._chomper.name())).get()

    def prepend(self, value):
        return FroParser(chompers.composition.CompositionChomper(
            [_extract(value).clone(significant=False),
             self._chomper.clone(significant=True)],
            significant=self._chomper.significant(),
            name=self._chomper.name())).get()

    def lstrip(self):
        return self.prepend(r"~\s*")

    def lstrips(self):
        return self.prepend(until(r"~[^\s]"))

    def rstrip(self):
        return self.append(r"~\s*")

    def rstrips(self):
        return self.append(until(r"~[^\s]"))

    def strip(self):
        return self.lstrip().rstrip()

    def strips(self):
        return self.lstrips().rstrips()

    def unname(self):
        return FroParser(self._chomper.unname())

    def get(self):
        return self >> (lambda x: x)

    def __invert__(self):
        """
        :return: an insignificant copy of the called parser
        """
        return FroParser(self._chomper.clone(significant=False))

    def significant(self):
        """
        :return: a significant copy of the
        """
        return FroParser(self._chomper.clone(significant=True))

    def __or__(self, func):
        return FroParser(self._chomper.clone(func=func))

    def __rshift__(self, func):
        return FroParser(self._chomper.clone(func=lambda x: func(*x)))

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
    elif isinstance(value, FroParser):
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
    chompers_ = [_extract(p) for p in parser_values]
    return FroParser(chompers.alternation.AlternationChomper(
        chompers_, name=name))


def chain(func, name=None):
    def func_(chomper):
        return _extract(func(FroParser(chomper)))
    return FroParser(chompers.util.ChainChomper(func_, name=name))


def comp(parser_values, sep=None, name=None):
    if isinstance(parser_values, str) or isinstance(parser_values, bytes):
        raise TypeError("Do not pass a string/bytes for the parser_values argument")
    chompers_ = [_extract(p) for p in parser_values]
    return FroParser(chompers.composition.CompositionChomper(
        chompers_, sep, name=name))


def group_rgx(regex_string, name=None):
    rgx_str, significant = _parse_rgx(regex_string)
    return FroParser(chompers.regex.GroupRegexChomper(
        rgx_str, significant=significant, name=name))


def nested(open_regex_string, close_regex_string, reducer="".join, name=None):
    return FroParser(chompers.nested.NestedChomper(
        open_regex_string,
        close_regex_string,
        reducer,
        name=name))


def rgx(regex_string, name=None):
    rgx_str, significant = _parse_rgx(regex_string)
    return FroParser(chompers.regex.RegexChomper(
        rgx_str, significant=significant, name=name))


def seq(parser_value, reducer=list, sep=None, name=None):
    return FroParser(chompers.sequence.SequenceChomper(
        _extract(parser_value), reducer, _extract(sep), name=name))


def thunk(func, name=None):
    return FroParser(chompers.util.ThunkChomper(
        lambda: _extract(func()), name=name))


def tie(func, name=None):
    stub_chomper = chompers.util.StubChomper(name=name)
    stub_parser = FroParser(stub_chomper)
    result = func(stub_parser)
    stub_chomper.set_delegate(result._chomper)
    if name is not None:
        result = result.name(name)
    return result


def until(regex_str, reducer=lambda _: None, name=None):
    rgx_str, significant = _parse_rgx(regex_str)
    return FroParser(chompers.until.UntilChomper(rgx_str, reducer, name=name,
                                                 significant=significant))


# nothing before decimal or something before decimal
_floatp = r"(-?\.[0-9]+)|(-?[0-9]+(\.[0-9]*)?)"
floatp = (rgx(r"{}([eE][-+]?[0-9]+)?".format(_floatp)) | float).name("float")

intp = (rgx(r"-?[0-9]+") | int).name("int")
natp = (rgx(r"[0-9]+") | int).name("non-negative int")
posintp = (rgx(r"0*[1-9][0-9]*") | int).name("positive int")
