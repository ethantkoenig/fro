"""
The public interface exposed by the fro package
"""

from builtins import bytes, str

import parser
import chompers

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


def alt(parsers, name=None):
    chompers_ = [_extract(p) for p in parsers]
    return parser.FroParser(chompers.AlternationChomper(chompers_, name=name))


def comp(parsers, sep=None, name=None):
    chompers_ = [_extract(p) for p in parsers]
    return parser.FroParser(chompers.CompositionChomper(chompers_, sep, name=name))


def group_rgx(regex_string, name=None):
    rgx_str, fertile = _parse_rgx(regex_string)
    return parser.FroParser(chompers.GroupRegexChomper(
        rgx_str, fertile=fertile, name=name))


def nested(open_regex_string, close_regex_string, name=None):
    return parser.FroParser(chompers.NestedChomper(
        open_regex_string, close_regex_string, name=name))


def rgx(regex_string, name=None):
    rgx_str, fertile = _parse_rgx(regex_string)
    return parser.FroParser(chompers.RegexChomper(
        rgx_str, fertile=fertile, name=name))


def seq(value, sep=None, sep_at_start=False, sep_at_end=False, name=None):
    return parser.FroParser(chompers.SequenceChomper(_extract(value), _extract(sep),
                                                     sep_at_start, sep_at_end, name=name))

# nothing before decimal or something before decimal
_floatp = r"(-?\.[0-9]+)|(-?[0-9]+(\.[0-9]*)?)"
floatp = rgx(r"{}(e[-+]?[0-9]+)?".format(_floatp)) | float

intp = rgx(r"-?[0-9]+") | int
natp = rgx(r"[0-9]+") | int
posintp = rgx(r"0*[1-9][0-9]*") | int


