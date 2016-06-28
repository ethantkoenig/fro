from fro_chomper import AlternationChomper, CompositionChomper, GroupRegexChomper,\
    NestedChomper, RegexChomper, SequenceChomper


import fro_parse_error
from fro_parser import FroParser


# public interface

FroParseError = fro_parse_error.FroParseError


def alt(parsers, name=None): # TODO add name to rest
    chompers = [_extract(parser) for parser in parsers]
    return FroParser(AlternationChomper(chompers, name=name))

def compose(parsers, sep=None, reducer=lambda *x: x):
    chompers = [_extract(parser) for parser in parsers]
    return FroParser(CompositionChomper(chompers, sep, reducer))


def group_rgx(regex_string, reducer=lambda *x: x):
    return FroParser(GroupRegexChomper(regex_string, reducer))


def nested(open_regex_string, close_regex_string):
    return FroParser(NestedChomper(open_regex_string, close_regex_string))


def rgx(regex_string, func=lambda x: x):
    return FroParser(RegexChomper(regex_string, func))


def seq(value, sep=None, sep_at_start=False, sep_at_end=False):
    return FroParser(SequenceChomper(_extract(value), _extract(sep),
                                     sep_at_start, sep_at_end))


boolp = rgx(r"True|False", bool)

_float_nothing_before_decimal = r"-?\.[0-9]+"
_float_something_before_decimal = r"-?[0-9]+(\.[0-9]*)?"
_floatp = "({})|({})".format(_float_nothing_before_decimal, _float_something_before_decimal)
floatp = rgx("{}(e[-+]?[0-9]+)?".format(_floatp), float)

intp = rgx(r"-?[0-9]+", int)
nonneg_intp = rgx(r"[0-9]+", int)
pos_intp = rgx(r"0*[1-9][0-9]*", int)


def offset_of_index(line, index):
    uc_line = line.decode("utf-8")
    lo = 0
    hi = len(uc_line)
    while hi - lo > 1:
        mid = (lo + hi) / 2
        uc_subline = uc_line[:mid]
        num_bytes = len(uc_subline.encode("utf-8"))
        if num_bytes == index:
            return mid
        elif num_bytes < index:
            lo = mid
        else:
            hi = mid
    if lo == len(uc_line) - 1 and index >= len(line):
        return lo + 1
    return lo


# --------------------------------------------------------------------
# internals

def _extract(value):
    if isinstance(value, FroParser):
        return value._chomper
    return value
