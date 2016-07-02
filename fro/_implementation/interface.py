"""
The public interface exposed by the fro package
"""

from builtins import bytes, str

from fro._implementation import parser
from fro._implementation import chompers

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
    return parser.FroParser(chompers.AlternationChomper(chompers_, name=name))


def comp(parser_values, sep=None, name=None):
    chompers_ = [_extract(p) for p in parser_values]
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


def seq(parser_value, sep=None, sep_at_start=False, sep_at_end=False, name=None):
    return parser.FroParser(chompers.SequenceChomper(_extract(parser_value), _extract(sep),
                                                     sep_at_start, sep_at_end, name=name))

# nothing before decimal or something before decimal
_floatp = r"(-?\.[0-9]+)|(-?[0-9]+(\.[0-9]*)?)"
floatp = (rgx(r"{}(e[-+]?[0-9]+)?".format(_floatp)) | float).name("float")

intp = (rgx(r"-?[0-9]+") | int).name("int")
natp = (rgx(r"[0-9]+") | int).name("non-negative int")
posintp = (rgx(r"0*[1-9][0-9]*") | int).name("positive int")
