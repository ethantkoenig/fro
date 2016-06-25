import fro_parser
import fro_parser_utils

class CompositionFroParser(fro_parser.AbstractFroParser):

    def __init__(self, parsers, reducer):
        fro_parser.AbstractFroParser.__init__(self)
        self._parsers = [fro_parser_utils.parser_of(x) for x in parsers]
        self._reducer = reducer

    def _chomp(self, s, index, fail_hard):
        remainder = s
        values = []
        for parser in self._parsers:
            chomp_result = parser._chomp(remainder, index, fail_hard)
            if chomp_result is None:
                return self._quit(index, fail_hard)
            value, index = chomp_result
            if parser._fertile:
                values.append(value)
        return self._reducer(*tuple(values)), index
