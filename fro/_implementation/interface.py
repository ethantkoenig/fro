"""
The public interface exposed by the fro package
"""

from builtins import bytes, str
import re

from fro._implementation import chompers, parser

# --------------------------------------------------------------------
# internals (put first to avoid use before def'n issues)


def _extract(value):
    if value is None:
        return None
    elif isinstance(value, str):
        return rgx(value)._chomper
    elif isinstance(value, bytes):
        return rgx(value)._chomper
    elif isinstance(value, parser.FroParser):
        return value._chomper
    else:
        msg = "{} does not represent a parser".format(repr(value))
        raise ValueError(msg)


def _parse_rgx(regex_string):
    """
    :return: (modified regex_string, whether fertile)
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
    return parser.FroParser(chompers.alternation.AlternationChomper(
        chompers_, name=name))


def comp(parser_values, sep=None, name=None):
    chompers_ = [_extract(p) for p in parser_values]
    return parser.FroParser(chompers.composition.CompositionChomper(
        chompers_, sep, name=name))


def group_rgx(regex_string, name=None):
    rgx_str, fertile = _parse_rgx(regex_string)
    return parser.FroParser(chompers.regex.GroupRegexChomper(
        rgx_str, fertile=fertile, name=name))


def nested(open_regex_string, close_regex_string, reducer="".join, name=None):
    return parser.FroParser(chompers.nested.NestedChomper(
        open_regex_string,
        lambda _: re.compile(close_regex_string),
        reducer,
        name=name))


def rgx(regex_string, name=None):
    rgx_str, fertile = _parse_rgx(regex_string)
    return parser.FroParser(chompers.regex.RegexChomper(
        rgx_str, fertile=fertile, name=name))


def seq(parser_value, reducer=list, sep=None, name=None):
    return parser.FroParser(chompers.sequence.SequenceChomper(
        _extract(parser_value), reducer, _extract(sep), name=name))


def tie(func, name=None):
    stub_chomper = chompers.util.StubChomper(name=name)
    stub_parser = parser.FroParser(stub_chomper)
    result = func(stub_parser)
    stub_chomper.set_delegate(result._chomper)
    if name is not None:
        result = result.name(name)
    return result

# nothing before decimal or something before decimal
_floatp = r"(-?\.[0-9]+)|(-?[0-9]+(\.[0-9]*)?)"
floatp = (rgx(r"{}(e[-+]?[0-9]+)?".format(_floatp)) | float).name("float")

intp = (rgx(r"-?[0-9]+") | int).name("int")
natp = (rgx(r"[0-9]+") | int).name("non-negative int")
posintp = (rgx(r"0*[1-9][0-9]*") | int).name("positive int")
