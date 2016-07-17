from fro._implementation.chompers.abstract import AbstractChomper


class CompositionChomper(AbstractChomper):

    def __init__(self, parsers, separator=None, fertile=True, name=None):
        AbstractChomper.__init__(self, fertile, name)
        self._parsers = list(parsers)
        self._separator = separator  # self._separator may be None

    def _chomp(self, state, tracker):
        values = []
        for i, parser in enumerate(self._parsers):
            value = parser.chomp(state, tracker)
            if parser._fertile:
                values.append(value)
            if i < len(self._parsers) - 1 and self._separator is not None:
                self._separator.chomp(state, tracker)
        return tuple(values)
