import fro_parser
import regex_parser

def parser_of(x):
    if x is None:
        return None
    elif isinstance(x, fro_parser.AbstractFroParser):
        return x
    elif isinstance(x, str):
        return regex_parser.RegexFroParser(x)
    else:
        raise ValueError("{} does not represent a parser".format(x))
