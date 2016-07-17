from fro._implementation.chompers.abstract import AbstractChomper


class CompositionChomper(AbstractChomper):

    def __init__(self, parsers, separator=None, fertile=True, name=None):
        AbstractChomper.__init__(self, fertile, name)
        self._parsers = list(parsers)
        self._separator = separator  # self._separator may be None

    def _chomp(self, state, tracker):
        values = []
        length = len(self._parsers)
        for i, parser in enumerate(self._parsers):
            box_ = parser.chomp(state, tracker)
            if box_ is None:
                return None
            if parser._fertile:
                values.append(box_.value)
            if i == length - 1:
                box_.value = tuple(values)
                return box_
            elif self._separator is not None:
                box_ = self._separator.chomp(state, tracker)
                if box_ is not None:
                    return None
        raise AssertionError()
