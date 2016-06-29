from fro_chomper import AlternationChomper, CompositionChomper, GroupRegexChomper,\
    NestedChomper, RegexChomper, SequenceChomper


import fro_parse_error
from fro_parser import FroParser


# public interface

FroParseError = fro_parse_error.FroParseError


def alt(parsers, name=None):
    chompers = [_extract(parser) for parser in parsers]
    return FroParser(AlternationChomper(chompers, name=name))


def compose(parsers, sep=None, name=None):
    chompers = [_extract(parser) for parser in parsers]
    return FroParser(CompositionChomper(chompers, sep, name=name))


def group_rgx(regex_string, name=None):
    return FroParser(GroupRegexChomper(regex_string, name=name))


def nested(open_regex_string, close_regex_string, name=None):
    return FroParser(NestedChomper(open_regex_string, close_regex_string, name=name))


def rgx(regex_string, name=None):
    return FroParser(RegexChomper(regex_string, name=name))


def seq(value, sep=None, sep_at_start=False, sep_at_end=False, name=None):
    return FroParser(SequenceChomper(_extract(value), _extract(sep),
                                     sep_at_start, sep_at_end, name=name))


boolp = rgx(r"True|False") | bool

_float_nothing_before_decimal = r"-?\.[0-9]+"
_float_something_before_decimal = r"-?[0-9]+(\.[0-9]*)?"
_floatp = "({})|({})".format(_float_nothing_before_decimal, _float_something_before_decimal)
floatp = rgx("{}(e[-+]?[0-9]+)?".format(_floatp)) | float

intp = rgx(r"-?[0-9]+") | int
nonneg_intp = rgx(r"[0-9]+") | int
pos_intp = rgx(r"0*[1-9][0-9]*") | int

# --------------------------------------------------------------------
# internals

def _extract(value):
    if isinstance(value, FroParser):
        return value._chomper
    return value
