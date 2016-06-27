import fro_parser
import fro_parser_utils


class CompositionFroParser(fro_parser.AbstractFroParser):

    def __init__(self, parsers, separator=None, reducer=lambda *x: x):
        fro_parser.AbstractFroParser.__init__(self)
        self._parsers = [fro_parser_utils.parser_of(x) for x in parsers]
        self._separator = fro_parser_utils.parser_of(separator)  # may be None
        self._reducer = reducer

    def _chomp(self, s, index, logger):
        start_index = index
        values = []
        for i, parser in enumerate(self._parsers):
            chomp_result = parser._chomp(s, index, logger)
            if chomp_result is None:
                return None
            value, index = chomp_result
            if parser._fertile:
                values.append(value)
            if i < len(self._parsers) - 1 and self._separator is not None:
                chomp_result = self._separator._chomp(s, index, logger)
                if chomp_result is None:
                    return None
                _, index = chomp_result
        value = fro_parser.AbstractFroParser._apply(start_index, index, self._reducer, *values)
        return value, index
