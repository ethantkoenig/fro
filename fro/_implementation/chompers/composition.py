from fro._implementation.chompers.abstract import AbstractChomper


class CompositionChomper(AbstractChomper):

    def __init__(self, parsers, separator=None, fertile=True, name=None, quiet=False):
        AbstractChomper.__init__(self, fertile, name, quiet)
        self._parsers = list(parsers)
        self._separator = separator  # self._separator may be None

    def _chomp(self, s, index, tracker):
        values = []
        for i, parser in enumerate(self._parsers):
            chomp_result = parser.chomp(s, index, tracker)
            if chomp_result is None:
                return None
            value, index = chomp_result
            if parser._fertile:
                values.append(value)
            if i < len(self._parsers) - 1 and self._separator is not None:
                chomp_result = self._separator.chomp(s, index, tracker)
                if chomp_result is None:
                    return None
                _, index = chomp_result
        return tuple(values), index
