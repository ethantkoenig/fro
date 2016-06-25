from composition_parser import CompositionFroParser
from group_regex_fro_parser import GroupRegexFroParser
from nested_parser import NestedFroParser
from regex_parser import RegexFroParser
from sequence_parser import SequenceFroParser

# --------------------------------------------------------------------
# public interface

def compose(parsers, sep=None, reducer=lambda *x: x):
    return CompositionFroParser(parsers, sep, reducer)

def group_rgx(regex_string, reduce=lambda *x: x):
    return GroupRegexFroParser(regex_string, reduce)

def nested(open_regex_string, close_regex_string):
    return NestedFroParser(open_regex_string, close_regex_string)

def rgx(regex_string, func=None):
    return RegexFroParser(regex_string, func)

def seq(value, separator=None, start=None, end=None):
    return SequenceFroParser(value, separator, start, end)


boolp = rgx(r"True|False", bool)

_float_nothing_before_decimal = r"-?\.[0-9]+"
_float_something_before_decimal = r"-?[0-9]+(\.[0-9]*)?"
_floatp = "({})|({})".format(_float_nothing_before_decimal, _float_something_before_decimal)
floatp = rgx("{}(e[-+]?[0-9]+)?".format(_floatp), float)

intp = rgx(r"-?[0-9]+", int)
nonneg_intp = rgx(r"[0-9]+", int)
pos_intp = rgx(r"0*[1-9][0-9]*", int)




# --------------------------------------------------------------------
# internals




