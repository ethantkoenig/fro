from composition_parser import CompositionFroParser
from nested_parser import NestedFroParser
from regex_parser import RegexFroParser
from sequence_parser import SequenceFroParser

# --------------------------------------------------------------------
# public interface

def compose(parsers, reducer=lambda *x: x):
    return CompositionFroParser(parsers, reducer)

def nested(open_regex_string, close_regex_string):
    return NestedFroParser(open_regex_string, close_regex_string)

def rgx(regex_string, func=None):
    return RegexFroParser(regex_string, func)

def seq(value, separator=None, start=None, end=None):
    return SequenceFroParser(value, separator, start, end)

# --------------------------------------------------------------------
# internals




